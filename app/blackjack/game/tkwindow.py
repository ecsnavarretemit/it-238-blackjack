# window.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

import os
import sys
import tkinter as pygui
from tkinter import messagebox
from PIL import Image, ImageTk
from app.cards.transformer import CardToCardImagePositionTransformer
from app.blackjack.game.error import GameError
from app.blackjack.cards.transformer import TextToCardTransformer
from Pyro4.errors import SerializeError, CommunicationError
from Pyro4.core import Proxy as PyroProxy
from Pyro4.util import getPyroTraceback as PyroExceptionTraceback, excepthook as PyroExceptHook

# add hooks to exception hooks
sys.excepthook = PyroExceptHook

# TODO: Hide 1 of the server's card
# TODO: Re-create deck when all cards have been played
# TODO: Apply blackjack rules
class Window(object):

  def __init__(self, window_title="BlackJack"):
    # create new instance of TK
    self.window = pygui.Tk()

    # save the window title
    self.window_title = window_title

    # initialize remote connection
    self.remote_connection = None

    # Initialize game deck
    self.game_deck = PyroProxy('PYRO:standard.deck@localhost:3000')

    # Images
    self.card_img = None
    self.splash_img = None

    # client cards
    self.client_cards = []

    # server cards
    self.server_cards = []

    # [Splash GUI Init] ::start
    self.splash_bootstrapped = False

    self.splash_frame = pygui.Frame(self.window)
    self.start_btn = pygui.Button(self.splash_frame, text="Start Game", command=self.connect_to_server)
    self.splash_logo_canvas = pygui.Canvas(self.splash_frame, width=375, height=355)
    # [Splash GUI Init] ::end

    # [Main GUI Init] ::start
    self.main_bootstrapped = False

    self.main_frame = pygui.Frame(self.window)
    self.main_client_frame = pygui.Frame(self.main_frame)
    self.main_server_frame = pygui.Frame(self.main_frame)
    self.main_controls_frame = pygui.Frame(self.main_frame)

    self.stand_btn = pygui.Button(self.main_controls_frame, text="Stand")
    self.hit_btn = pygui.Button(self.main_controls_frame, text="Hit", command=self.hit)
    # [Main GUI Init] ::end

  def bootstrap(self):
    # set window title
    self.window.wm_title(self.window_title)

    # load assets before starting gui
    self.load_assets()

    # show the splash page
    self.splash_gui()

    # set default window size
    self.window.minsize(500, 500)

    # Start the GUI
    self.window.mainloop()

  def switch_context(self, context):
    if context == 'main':
      # hide the splash page
      self.splash_frame.pack_forget()

      # Show the frame for the game
      self.main_gui()
    else:
      # hide the game
      self.main_frame.pack_forget()

      # Show the splash page.
      self.splash_gui()

  def splash_gui(self):
    if self.splash_bootstrapped is False:
      self.splash_logo_canvas.create_image(0, 0, image=self.window.splash_img, anchor=pygui.NW)
      self.splash_logo_canvas.pack()

      # position the start button
      self.start_btn.grid(row=1, column=0)
      self.start_btn.configure()
      self.start_btn.pack()

      # set the bootstrap flag to true
      self.splash_bootstrapped = True

    self.splash_frame.pack(padx=10, pady=25)

  def main_gui(self):
    try:
      player_client = self.game_deck.pluck(2)
      player_server = self.game_deck.pluck(2)
    except SerializeError:
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

    # [client canvas logic] ::start
    label_client = pygui.Label(self.main_client_frame, text="You")
    label_client.pack(side=pygui.LEFT)

    self.load_cards(player_client, self.client_cards, self.main_client_frame)

    self.main_client_frame.pack(padx=10, pady=10)
    # [client canvas logic] ::end

    # [server canvas logic] ::start
    label_computer = pygui.Label(self.main_server_frame, text="Computer")
    label_computer.pack(side=pygui.LEFT)

    self.load_cards(player_server, self.server_cards, self.main_server_frame)

    self.main_server_frame.pack(padx=10, pady=10)
    # [server canvas logic] ::end

    # [controls] ::start
    self.stand_btn.grid(row=0, column=1)
    self.hit_btn.grid(row=0, column=0)

    self.main_controls_frame.pack(padx=10, pady=10)
    # [controls] ::end

    self.main_frame.pack()

  def hit(self):
    try:
      newcard = self.game_deck.pluck(1)
    except SerializeError:
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

    self.load_cards(newcard, self.client_cards, self.main_client_frame)

  def load_cards(self, cards, card_collection, frame):
    for card_text in cards:
      card = TextToCardTransformer(card_text).transform()
      card_img_post = CardToCardImagePositionTransformer(card).transform()

      canvas = pygui.Canvas(frame, width=78, height=120)
      canvas.create_image(card_img_post['x'], card_img_post['y'], image=self.window.card_img, anchor=pygui.NW)
      canvas.card_text = card_text # store the card text as an attribute of the canvas
      canvas.pack(side=pygui.LEFT)

      card_collection.append(canvas)

  def get_card_total(self, card_collection):
    card_total = 0

    ace_counter = 0
    for card in card_collection:
      card_obj = TextToCardTransformer(card.card_text).transform()
      card_value = card_obj.get_normalized_value()

      # increment the ace counter if we enconter one
      if card_obj.get_face_value() == 'A':
        ace_counter += 1
        continue

      card_total += card_value

    if card_total <= 10 and ace_counter == 1:
      # add eleven to the card total when user has 1 ace card if the card total is less than or eq to 10
      card_total += 11
    elif card_total > 10 and ace_counter >= 1:
      # add 1 for each ace the user has when the card total is greater than 10
      card_total += ace_counter
    elif card_total == 0 and ace_counter > 1:
      # if the user's card consists of all aces then add set the initial total to 11
      # and add 1 for each remaining ace card
      card_total += (11 + (ace_counter - 1))
    else:
      pass

    return card_total

  def connect_to_server(self):
    try:
      # create and shuffle the deck
      self.game_deck.create()
      self.game_deck.shuffle()

      # try to check if there are cards generated
      self.game_deck.get_cards()

      # switch to the main page
      self.switch_context('main')
    except (ConnectionRefusedError, CommunicationError):
      # show message to the user
      messagebox.showerror("Black Jack", "Failed to connect to server. Try again later.")

      # show trace to the client
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

  def load_assets(self):
    # [card image] ::start
    card_img = os.path.join(os.getcwd(), "resources/images/cards.png")

    if not os.path.exists(card_img):
      raise GameError("Card Faces sprite does not exist!")

    cards = Image.open(card_img)

    # prevent garbage collection that's why we are storing the reference to the window object
    self.window.card_img = ImageTk.PhotoImage(cards)
    # [card image] ::start

    # [splash image] ::start
    splash_logo_img = os.path.join(os.getcwd(), "resources/images/royal-flush.png")

    if not os.path.exists(splash_logo_img):
      raise GameError("Logo for Splash page not found!")

    # open the image and render it on the canvas
    splash_logo = Image.open(splash_logo_img)

    # prevent garbage collection that's why we are storing the reference to the window object
    self.window.splash_img = ImageTk.PhotoImage(splash_logo)
    # [splash image] ::start


