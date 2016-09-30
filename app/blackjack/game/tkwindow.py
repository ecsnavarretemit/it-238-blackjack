# window.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.2

import os
import sys
import tkinter as pygui
from tkinter import messagebox
from PIL import Image, ImageTk
from app.cards.transformer import CardToCardImagePositionTransformer, BLANK_COORDS, CARD_WIDTH
from app.blackjack.game.error import GameError
from app.blackjack.cards.transformer import TextToCardTransformer
from Pyro4.errors import SerializeError, CommunicationError
from Pyro4.core import Proxy as PyroProxy
from Pyro4.util import getPyroTraceback as PyroExceptionTraceback, excepthook as PyroExceptHook

# add hooks to exception hooks
sys.excepthook = PyroExceptHook

class Window(object):

  def __init__(self, window_title="BlackJack"):
    # create new instance of TK
    self.window = pygui.Tk()

    # create cache for tk card images
    self.window.card_cache = {}

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

    # Create dictionary of elements
    self.splash_gui_items = {}

    # store elements in the dictionary
    self.splash_gui_items['splash_frame'] = pygui.Frame(self.window)

    self.splash_gui_items['start_btn'] = pygui.Button(self.splash_gui_items['splash_frame'],
                                                      text="Start Game",
                                                      command=self.connect_to_server)

    self.splash_gui_items['splash_logo_canvas'] = pygui.Canvas(self.splash_gui_items['splash_frame'],
                                                               width=375,
                                                               height=355)
    # [Splash GUI Init] ::end

    # [Main GUI Init] ::start
    # Create dictionary of elements
    self.main_gui_items = {}

    # store elements in the dictionary
    self.main_gui_items['main_frame'] = pygui.Frame(self.window)
    self.main_gui_items['main_client_frame'] = pygui.Frame(self.main_gui_items['main_frame'])
    self.main_gui_items['main_server_frame'] = pygui.Frame(self.main_gui_items['main_frame'])
    self.main_gui_items['main_controls_frame'] = pygui.Frame(self.main_gui_items['main_frame'])

    self.main_gui_items['canvas_player'] = pygui.Canvas(self.main_gui_items['main_client_frame'], width=500, height=250)
    self.main_gui_items['canvas_computer'] = pygui.Canvas(self.main_gui_items['main_server_frame'],
                                                          width=500,
                                                          height=250)

    self.main_gui_items['stand_btn'] = pygui.Button(self.main_gui_items['main_controls_frame'],
                                                    text="Stand",
                                                    command=self.stand)

    self.main_gui_items['hit_btn'] = pygui.Button(self.main_gui_items['main_controls_frame'],
                                                  text="Hit",
                                                  command=self.hit)
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
      self.splash_gui_items['splash_frame'].pack_forget()

      # Show the frame for the game
      self.main_gui()
    else:
      # hide the game
      self.main_gui_items['main_frame'].pack_forget()

      # Show the splash page.
      self.splash_gui()

  def splash_gui(self):
    if self.splash_bootstrapped is False:
      self.splash_gui_items['splash_logo_canvas'].create_image(0, 0, image=self.window.splash_img, anchor=pygui.NW)
      self.splash_gui_items['splash_logo_canvas'].pack()

      # position the start button
      self.splash_gui_items['start_btn'].pack()

      # set the bootstrap flag to true
      self.splash_bootstrapped = True

    self.splash_gui_items['splash_frame'].pack(padx=10, pady=25)

  def main_gui(self):
    # [client canvas logic] ::start
    self.main_gui_items['label_client'] = self.main_gui_items['canvas_player'].create_text(10, 0, anchor=pygui.NW)
    self.main_gui_items['canvas_player'].itemconfig(self.main_gui_items['label_client'], text="You: 0")

    self.main_gui_items['canvas_player'].pack(side=pygui.RIGHT)
    self.main_gui_items['main_client_frame'].pack(padx=10, pady=10)
    # [client canvas logic] ::end

    # [server canvas logic] ::start
    self.main_gui_items['label_computer'] = self.main_gui_items['canvas_computer'].create_text(10, 0, anchor=pygui.NW)
    self.main_gui_items['canvas_computer'].itemconfig(self.main_gui_items['label_computer'], text="Computer: 0")

    self.main_gui_items['canvas_computer'].pack(side=pygui.RIGHT)
    self.main_gui_items['main_server_frame'].pack(padx=10, pady=10)
    # [server canvas logic] ::end

    # [controls] ::start
    self.main_gui_items['stand_btn'].grid(row=0, column=1)
    self.main_gui_items['hit_btn'].grid(row=0, column=0)

    self.main_gui_items['main_controls_frame'].pack(padx=10, pady=10)
    # [controls] ::end

    # start the game session
    self.init_game_session()

    self.main_gui_items['main_frame'].pack()

  def init_game_session(self):
    remaining_cards = self.game_deck.get_remaining_cards()

    # recreate the deck and shuffle it once it reaches less than or equal to 10
    if remaining_cards <= 10:
      self.game_deck.create()
      self.game_deck.shuffle()

    # clean up old session if existing
    if len(self.client_cards) > 0:
      # destroy all canvas instances
      self.clean_player_cards(self.client_cards, self.main_gui_items['canvas_player'])

      # show the score of the client
      self.reflect_score(self.main_gui_items['canvas_player'], self.main_gui_items['label_client'], "You", 0)

    if len(self.server_cards) > 0:
      # remove the reference to the hidden card
      self.clean_player_cards(self.server_cards, self.main_gui_items['canvas_computer'])

      # show the score of the client
      self.reflect_score(self.main_gui_items['canvas_computer'], self.main_gui_items['label_computer'], "Computer", 0)

    # start new session
    try:
      player_client = self.game_deck.pluck(2)
      player_server = self.game_deck.pluck(2)
    except SerializeError:
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

    # load the client's cards
    self.load_cards(player_client, self.client_cards, self.main_gui_items['canvas_player'])

    # show the score of the client
    self.reflect_score(self.main_gui_items['canvas_player'], self.main_gui_items['label_client'], "You", self.get_card_total(self.client_cards))

    # load the server's cards
    self.load_cards(player_server, self.server_cards, self.main_gui_items['canvas_computer'], True)

    # get the first card since we only need to display the initial score of the server/dealer
    first_card = self.server_cards[0]

    # show the initial score of the computer
    self.reflect_score(self.main_gui_items['canvas_computer'], self.main_gui_items['label_computer'], "Computer", self.get_card_total([first_card]))

  def reflect_score(self, canvas, label, player_type, score):
    canvas.itemconfig(label, text="%s: %d" % (player_type, score))

  def hit(self):
    card_total = self.get_card_total(self.client_cards)

    # show popup box to indicate that the score is already 21 or above
    # and succeeding call to `self.hit()` is not allowed
    if card_total >= self.winning_number:
      messagebox.showinfo(self.window_title,
                          "Your card already sums up %s. Only up to %d points." %
                          (card_total, self.winning_number))

      return

    try:
      newcard = self.game_deck.pluck(1)
    except SerializeError:
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

    # load the player's cards
    self.load_cards(newcard, self.client_cards, self.main_gui_items['canvas_player'])

    # show the new score for the client
    self.reflect_score(self.main_gui_items['canvas_player'], self.main_gui_items['label_client'], "You", self.get_card_total(self.client_cards))

    # call `self.stand()` when the card total is greater than or equal to 21
    if self.get_card_total(self.client_cards) >= self.winning_number:
      self.stand()

  def stand(self):
    hidden_card = self.server_hidden_card['text']

    # reveal the hidden card
    self.main_gui_items['canvas_computer'].itemconfig(self.server_hidden_card['canvas_img'],
                                                      image=self.window.card_cache[hidden_card]['tk_img'])

    # locally copy the list
    server_cards = self.server_cards[:]
    server_new_cards = []

    while self.get_card_total(server_cards) < self.winning_number:
      try:
        server_newcard = self.game_deck.pluck(1)
      except SerializeError:
        print("Pyro traceback:")
        print("".join(PyroExceptionTraceback()))
        break

      # store new cards in a separate list
      server_new_cards.append(server_newcard[0])

      # append the new cards to emulate behavior
      server_cards.append({
        'text': server_newcard[0]
      })

    # load the player's cards
    self.load_cards(server_new_cards, self.server_cards, self.main_gui_items['canvas_computer'])

    # show the score of the computer
    self.reflect_score(self.main_gui_items['canvas_computer'], self.main_gui_items['label_computer'], "Computer", self.get_card_total(self.server_cards))

    client_difference = self.winning_number - self.get_card_total(self.client_cards)
    server_difference = self.winning_number - self.get_card_total(self.server_cards)

    if client_difference >= 0 and server_difference >= 0:
      if client_difference == server_difference:
        status = "Tie!"
      elif client_difference < server_difference:
        status = "Player wins!"
      else:
        status = "Dealer wins!"
    elif client_difference >= 0 and server_difference < 0:
      status = "Player wins!"
    elif client_difference < 0 and server_difference >= 0:
      status = "Dealer wins!"
    else:
      status = "No winner!"

    # show a prompt to start a new game.
    answer = messagebox.askokcancel(self.window_title, "%s Want to start a new game?" % status)

    # if the user answered "OK" to the question, we start a new game session
    if answer is True:
      self.init_game_session()

  def load_cards(self, cards, card_collection, canvas, server_deck=False):
    num_cards = len(cards)

    # if card cache is empty populate it
    if not self.window.card_cache:
      self.assemble_card_cache()

    # get the starting index to prevent placing card over another
    start_idx = len(card_collection)

    for index, card_text in enumerate(cards):
      resolved_cache_item = None
      is_hidden = False
      new_idx = index + start_idx

      if server_deck is True and new_idx == (num_cards - 1):
        is_hidden = True

        resolved_cache_item = self.window.card_cache['blank']

      if resolved_cache_item is None:
        resolved_cache_item = self.window.card_cache[card_text]

      # draw image on the canvas
      img_item = canvas.create_image((new_idx * (CARD_WIDTH + 2)),
                                     20,
                                     image=resolved_cache_item['tk_img'],
                                     anchor=pygui.NW)

      # assemble card metadata
      card_metadata = {
        'canvas_img': img_item,
        'text': card_text,
        'orig_coords': self.window.card_cache[card_text]['coords'],
        'is_hidden': is_hidden
      }

      # store the hidden card
      if is_hidden:
        self.server_hidden_card = card_metadata

      card_collection.append(card_metadata)

  def assemble_card_cache(self):
    cards = self.game_deck.get_cards()

    for card_text in cards:
      card = TextToCardTransformer(card_text).transform()
      card_img_coords = CardToCardImagePositionTransformer(card).transform()

      # crop the image
      resolved_face_and_shape = self.window.cards_img.crop(card_img_coords)

      # cache it inside the window
      self.window.card_cache[card_text] = {
        'tk_img': ImageTk.PhotoImage(resolved_face_and_shape),
        'coords': card_img_coords
      }

    # crop the blank card
    resolved_blank = self.window.cards_img.crop(BLANK_COORDS)

    # cache blank card
    self.window.card_cache['blank'] = {
      'tk_img': ImageTk.PhotoImage(resolved_blank),
      'coords': BLANK_COORDS
    }

  def clean_player_cards(self, card_collection, canvas):
    # clean up old session if existing
    if len(card_collection) > 0:
      # destroy all canvas instances
      for card in card_collection:
        # remove internal references
        card['text'] = None
        card['orig_pos'] = None

        canvas.delete(card['canvas_img'])

      # empty the list since all canvas instance have been destroyed
      card_collection.clear()

  def get_card_total(self, card_collection):
    card_total = 0

    ace_counter = 0
    for card in card_collection:
      card_obj = TextToCardTransformer(card['text']).transform()
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

      # assemble card cache
      self.assemble_card_cache()

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

    self.window.cards_img = Image.open(card_img)
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


