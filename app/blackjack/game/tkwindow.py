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
from app.cards.transformer import CardToCardImagePositionTransformer, BLANK_X, BLANK_Y
from app.blackjack.game.error import GameError
from app.blackjack.cards.transformer import TextToCardTransformer
from Pyro4.errors import SerializeError, CommunicationError
from Pyro4.core import Proxy as PyroProxy
from Pyro4.util import getPyroTraceback as PyroExceptionTraceback, excepthook as PyroExceptHook

# add hooks to exception hooks
sys.excepthook = PyroExceptHook

# TODO: Hide 1 of the server's card
class Window(object):

  def __init__(self, window_title="BlackJack"):
    # create new instance of TK
    self.window = pygui.Tk()

    # save the window title
    self.window_title = window_title

    # initialize remote connection
    self.remote_connection = None

    # Initialize game deck
    self.game_deck = None

    # blackjack goal number
    self.winning_number = 21

    # client cards
    self.client_cards = []

    # server cards
    self.server_cards = []
    self.server_hidden_card = None

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

    self.label_client = pygui.Label(self.main_client_frame, text="You")
    self.label_computer = pygui.Label(self.main_server_frame, text="Computer")

    self.stand_btn = pygui.Button(self.main_controls_frame, text="Stand", command=self.stand)
    self.hit_btn = pygui.Button(self.main_controls_frame, text="Hit", command=self.hit)
    # [Main GUI Init] ::end

  def bootstrap(self):
    if self.game_deck is None:
      print("No custom deck connection provided. Establishing connection with default parameters.")

      self.game_deck = PyroProxy("PYRO:standard.deck@localhost:3000")

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
    # [client canvas logic] ::start
    self.label_client.pack(side=pygui.LEFT)

    self.main_client_frame.pack(padx=10, pady=10)
    # [client canvas logic] ::end

    # [server canvas logic] ::start
    self.label_computer.pack(side=pygui.LEFT)

    self.main_server_frame.pack(padx=10, pady=10)
    # [server canvas logic] ::end

    # [controls] ::start
    self.stand_btn.grid(row=0, column=1)
    self.hit_btn.grid(row=0, column=0)

    self.main_controls_frame.pack(padx=10, pady=10)
    # [controls] ::end

    # start the game session
    self.init_game_session()

    self.main_frame.pack()

  def init_game_session(self):
    remaining_cards = self.game_deck.get_remaining_cards()

    # recreate the deck and shuffle it once it reaches less than or equal to 10
    if remaining_cards <= 10:
      self.game_deck.create()
      self.game_deck.shuffle()

    # clean up old session if existing
    if len(self.client_cards) > 0:
      # destroy all canvas instances
      self.clean_player_cards(self.client_cards)

      # show the score of the client
      self.reflect_score(self.label_client, "You", 0)

    if len(self.server_cards) > 0:
      # remove the reference to the hidden card
      self.clean_player_cards(self.server_cards)

      # show the score of the client
      self.reflect_score(self.label_computer, "Computer", 0)

    # start new session
    try:
      player_client = self.game_deck.pluck(2)
      player_server = self.game_deck.pluck(2)
    except SerializeError:
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

    # load the client's cards
    self.load_cards(player_client, self.client_cards, self.main_client_frame)

    # show the score of the client
    self.reflect_score(self.label_client, "You", self.get_card_total(self.client_cards))

    # load the server's cards
    self.load_cards(player_server, self.server_cards, self.main_server_frame, True)

    # show the score of the computer
    self.reflect_score(self.label_computer, "Computer", self.get_card_total(self.server_cards))

  def reflect_score(self, label, player_type, score):
    label.configure(text="%s: %d" % (player_type, score))

  # TODO: when client card hits 21 or greater, invoke self.stand()
  def hit(self):
    card_total = self.get_card_total(self.client_cards)

    if card_total >= self.winning_number:
      messagebox.showinfo(self.window_title, "Your card already sums up %s. Only up to 21 points." % card_total)
      return

    try:
      newcard = self.game_deck.pluck(1)
    except SerializeError:
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

    # load the player's cards
    self.load_cards(newcard, self.client_cards, self.main_client_frame)

    # show the new score for the client
    self.reflect_score(self.label_client, "You", self.get_card_total(self.client_cards))

  def stand(self):
    # get the card position for the hidden card
    hidden_card_new_pos = self.server_hidden_card.orig_pos

    # move the card to the original position
    self.server_hidden_card.coords(self.server_hidden_card.img_item, hidden_card_new_pos['x'], hidden_card_new_pos['y'])

    while self.get_card_total(self.server_cards) < self.winning_number:
      try:
        server_newcard = self.game_deck.pluck(1)
      except SerializeError:
        print("Pyro traceback:")
        print("".join(PyroExceptionTraceback()))
        break

      # load the player's cards
      self.load_cards(server_newcard, self.server_cards, self.main_server_frame)

    # show the score of the computer
    self.reflect_score(self.label_computer, "Computer", self.get_card_total(self.server_cards))

    server_card_total = self.get_card_total(self.server_cards)
    client_card_total = self.get_card_total(self.client_cards)

    answer = False

    if client_card_total == server_card_total and client_card_total == self.winning_number:
      answer = messagebox.askokcancel(self.window_title, "Tie! Want to start a new game?")
    elif client_card_total == self.winning_number:
      answer = messagebox.askokcancel(self.window_title, "Player wins! Want to start a new game?")
    elif server_card_total == self.winning_number:
      answer = messagebox.askokcancel(self.window_title, "Dealer wins! Want to start a new game?")
    else:
      client_difference = self.winning_number - client_card_total
      server_difference = self.winning_number - server_card_total

      if client_difference == server_difference:
        answer = messagebox.askokcancel(self.window_title, "Tie! Want to start a new game?")
      elif client_difference > server_difference:
        answer = messagebox.askokcancel(self.window_title, "Player wins! Want to start a new game?")
      else:
        answer = messagebox.askokcancel(self.window_title, "Dealer wins! Want to start a new game?")

    # if the user answered "OK" to the question, we start a new game session
    if answer is True:
      self.init_game_session()

  def load_cards(self, cards, card_collection, frame, server_deck=False):
    num_cards = len(cards)

    for index, card_text in enumerate(cards):
      card = TextToCardTransformer(card_text).transform()
      card_img_pos = CardToCardImagePositionTransformer(card).transform()
      new_card_img_pos = None
      is_hidden = False

      if server_deck is True and index == (num_cards - 1):
        is_hidden = True

        new_card_img_pos = {
          'x': BLANK_X,
          'y': BLANK_Y
        }

      if new_card_img_pos == None:
        new_card_img_pos = card_img_pos

      canvas = pygui.Canvas(frame, width=78, height=120)
      canvas.img_item = canvas.create_image(new_card_img_pos['x'], new_card_img_pos['y'], image=self.window.card_img, anchor=pygui.NW)
      canvas.card_text = card_text # store the card text as an attribute of the canvas
      canvas.orig_pos = card_img_pos
      canvas.pack(side=pygui.LEFT)

      # store the reference to the hidden card so that we can move its coordinates
      # for revealing the true value of the card
      if is_hidden is True:
        self.server_hidden_card = canvas

      card_collection.append(canvas)

  def clean_player_cards(self, card_collection):
    # clean up old session if existing
    if len(card_collection) > 0:
      # destroy all canvas instances
      for card in card_collection:
        # remove internal references
        card.img_item = None
        card.card_text = None
        card.orig_pos = None

        # destroy the card canvass
        card.destroy()

      # empty the list since all canvas instance have been destroyed
      card_collection.clear()

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
      messagebox.showerror(self.window_title, "Failed to connect to server. Try again later.")

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

  def set_game_deck(self, game_deck: PyroProxy):
    self.game_deck = game_deck


