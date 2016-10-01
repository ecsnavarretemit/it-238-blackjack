# window.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.1.0

import os
import sys
import datetime
import threading
import tkinter as pygui
from tkinter import messagebox
from PIL import Image, ImageTk
from app.helpers import strip_uid
from app.cards.transformer import CardToCardImagePositionTransformer, BLANK_COORDS, CARD_WIDTH
from app.blackjack.game.error import GameError
from app.blackjack.cards.transformer import TextToCardTransformer
from app.blackjack.cards.deck import SerializableDeck
from Pyro4.errors import SerializeError, CommunicationError
from Pyro4.core import Proxy as PyroProxy
from Pyro4.util import getPyroTraceback as PyroExceptionTraceback, excepthook as PyroExceptHook

# add hooks to exception hooks
sys.excepthook = PyroExceptHook

# TODO: implement cleanup of threads and data storage and game restart
class Window(object):

  def __init__(self, window_title="BlackJack"):
    # create new instance of TK
    self.window = pygui.Tk()

    # create cache for tk card images
    self.window.card_cache = {}

    # save the window title
    self.window_title = window_title

    # blackjack goal number
    self.winning_number = 21

    # Game Manager
    self.game_manager = None

    # Game State storage
    self.game_storage = {}

    # Thread
    self.game_threads = {}

    # [Splash GUI Init] ::start
    self.splash_bootstrapped = False

    # Create dictionary of elements
    self.splash_gui_items = {}
    # [Splash GUI Init] ::end

    # [Main GUI Init] ::start
    self.main_bootstrapped = False

    # Create dictionary of elements
    self.main_gui_items = {}
    # [Main GUI Init] ::end

  def bootstrap(self):
    if self.game_manager is None:
      print("No custom game manager connection provided. Establishing connection with default parameters.")

      self.game_manager = PyroProxy("PYRO:standard.manager@localhost:3000")

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

  def hit(self):
    try:
      card_total = self.game_manager.get_player_card_total(self.game_storage['connection_uid'])

      # show popup box to indicate that the score is already 21 or above
      # and succeeding call to `self.hit()` is not allowed
      if card_total >= self.winning_number:
        messagebox.showinfo(self.window_title,
                            "Your card already sums up %s. Only up to %d points." %
                            (card_total, self.winning_number))

        return

      # get 1 new card
      new_card = self.game_manager.draw_cards(self.game_storage['connection_uid'], 1)

      self.draw_cards_on_canvas(self.game_storage['connection_uid'], new_card)

      # get the new card total after getting new card and rendering it in the canvas
      card_total = self.game_manager.get_player_card_total(self.game_storage['connection_uid'])

      # call `self.stand()` when the card total is greater than or equal to 21
      if card_total >= self.winning_number:
        self.stand()

    except SerializeError:
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

  def stand(self):
    try:
      # lock cards in hand to prevent any modification
      self.game_manager.lock_hand(self.game_storage['connection_uid'], True)

      # Disable hit and stand buttons
      self.main_gui_items['stand_btn'].config(state=pygui.DISABLED)
      self.main_gui_items['hit_btn'].config(state=pygui.DISABLED)

      # TODO: delete this after waiting for other players
      # run thread for listening to others on hand
      self.game_threads['winner_declaration_listener'] = {}

      self.game_threads['winner_declaration_listener']['evt'] = threading.Event()
      self.game_threads['winner_declaration_listener']['thread'] = threading.Thread(
        name="winner_declaration_listener_thread",
        target=self.find_winners,
        args=(self.game_threads['winner_declaration_listener']['evt'], self.game_manager,),
        kwargs={
          'on_identify_winners': self.declare_winners
        }
      )

      # start the listener thread
      self.game_threads['winner_declaration_listener']['thread'].start()
    except SerializeError:
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

  # TODO: reveal cards before showing popup message
  def declare_winners(self, response):
    winner_message = "Player: %s has won the round with the score of %d!"
    status = ""

    if 'winners' in response and len(response['winners']) >= 1:
      if len(response['winners']) > 1:
        winner_message = "Players: %s won the round with the score of %d!"

      winners_str = ', '.join(response['winners'])

      status = winner_message % (winners_str, response['score'])
    elif 'winners' in response and len(response['winners']) == 0:
      winner_message = "No winner!"

      status = winner_message
    else:
      pass

    # show a prompt to start a new game.
    answer = messagebox.askokcancel(self.window_title, "%s Want to start a new game?" % status)

    # if the user answered "OK" to the question, we start a new game session
    if answer is True:
      pass
      # self.init_game_session()

  def switch_context(self, context):
    if context == 'main':
      # hide the splash page
      if self.splash_bootstrapped:
        self.splash_gui_items['splash_frame'].pack_forget()

      # Show the frame for the game
      self.main_gui()
    else:
      # hide the game
      if self.main_bootstrapped:
        self.main_gui_items['main_frame'].pack_forget()

      # Show the splash page.
      self.splash_gui()

  def main_gui(self):
    try:
      player_uids = self.game_manager.get_player_uids()

      # base frame for the game window
      self.main_gui_items['main_frame'] = pygui.Frame(self.window)

      for player_uid in player_uids:
        frame_key = "player_frame_%s" % player_uid
        canvas_key = "player_canvas_%s" % player_uid
        label_key = "player_label_%s" % player_uid

        # strip the UID from the other player
        if player_uid != self.game_storage['connection_uid']:
          label_text = "%s: %d" % (strip_uid(player_uid), 0)
        else:
          label_text = "%s: %d" % ("You", 0)

        # create frame for each player
        self.main_gui_items[frame_key] = pygui.Frame(self.main_gui_items['main_frame'])
        self.main_gui_items[frame_key].pack(padx=10, pady=10)

        # create canvas
        self.main_gui_items[canvas_key] = pygui.Canvas(self.main_gui_items[frame_key], width=500, height=250)
        self.main_gui_items[canvas_key].pack()

        # make label
        self.main_gui_items[label_key] = self.main_gui_items[canvas_key].create_text(10, 0, anchor=pygui.NW)
        self.main_gui_items[canvas_key].itemconfig(self.main_gui_items[label_key], text=label_text)

      # [Controls] ::start
      self.main_gui_items['main_controls_frame'] = pygui.Frame(self.main_gui_items['main_frame'])

      self.main_gui_items['stand_btn'] = pygui.Button(self.main_gui_items['main_controls_frame'],
                                                      text="Stand",
                                                      command=self.stand)

      self.main_gui_items['stand_btn'].grid(row=0, column=1)

      self.main_gui_items['hit_btn'] = pygui.Button(self.main_gui_items['main_controls_frame'],
                                                    text="Hit",
                                                    command=self.hit)

      self.main_gui_items['hit_btn'].grid(row=0, column=0)

      self.main_gui_items['main_controls_frame'].pack(padx=10, pady=10)
      # [Controls] ::end

      # show the base frame
      self.main_gui_items['main_frame'].pack()

      # start the game session
      self.init_game_session()
    except SerializeError:
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

  def splash_gui(self):
    if self.splash_bootstrapped is False:
      # store elements in the dictionary
      self.splash_gui_items['splash_frame'] = pygui.Frame(self.window)

      self.splash_gui_items['splash_logo_canvas'] = pygui.Canvas(self.splash_gui_items['splash_frame'],
                                                                 width=375,
                                                                 height=355)

      self.splash_gui_items['splash_logo_canvas'].create_image(0, 0, image=self.window.splash_img, anchor=pygui.NW)
      self.splash_gui_items['splash_logo_canvas'].pack()

      self.splash_gui_items['name_label'] = pygui.Label(self.splash_gui_items['splash_frame'], text="Your Name:")
      self.splash_gui_items['name_label'].pack()

      self.splash_gui_items['name_input'] = pygui.Entry(self.splash_gui_items['splash_frame'])
      self.splash_gui_items['name_input'].pack()

      self.splash_gui_items['start_btn'] = pygui.Button(self.splash_gui_items['splash_frame'],
                                                        text="Start Game",
                                                        command=self.connect_to_server)
      self.splash_gui_items['start_btn'].pack()

      # set the bootstrap flag to true
      self.splash_bootstrapped = True

    self.splash_gui_items['splash_frame'].pack(padx=10, pady=25)

  def init_game_session(self):
    try:
      # initialize cards on hand of all players
      player_uids = self.game_manager.get_player_uids()

      for player_uid in player_uids:
        on_hand_key = "cards_on_hand_%s" % player_uid
        self.game_storage[on_hand_key] = []

      drawn_cards = self.game_manager.draw_cards(self.game_storage['connection_uid'], 2)

      self.draw_cards_on_canvas(self.game_storage['connection_uid'], drawn_cards)

      # TODO: delete this after waiting for other players
      # run thread for listening to others on hand
      self.game_threads['on_hand_listener'] = {}

      self.game_threads['on_hand_listener']['evt'] = threading.Event()
      self.game_threads['on_hand_listener']['thread'] = threading.Thread(
        name="on_hand_listener_thread",
        target=self.draw_player_cards,
        args=(self.game_threads['on_hand_listener']['evt'], self.game_manager,),
        kwargs={
          'on_hand': self.draw_cards_on_canvas,
          'excluded_uids': [
            self.game_storage['connection_uid']
          ]
        }
      )

      # start the listener thread
      self.game_threads['on_hand_listener']['thread'].start()
    except SerializeError:
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

  def toggle_name_input(self, hide=False):
    if hide is True:
      self.splash_gui_items['name_label'].config(text="Looking and waiting for other players...")
      self.splash_gui_items['name_input'].pack_forget()
      self.splash_gui_items['start_btn'].pack_forget()
    else:
      self.splash_gui_items['name_label'].config(text="Your Name:")
      self.splash_gui_items['name_input'].pack()
      self.splash_gui_items['start_btn'].pack()

      # Empty the input box
      self.splash_gui_items['name_input'].delete(0, pygui.END)

  def reflect_score(self, canvas, label, player_name, score):
    canvas.itemconfig(label, text="%s: %d" % (player_name, score))

  def connect_to_server(self):
    try:
      nameval = self.splash_gui_items['name_input'].get().strip()

      if nameval == '':
        messagebox.showerror(self.window_title, "Please provide your name.")
        return

      # temporarily save the connection uid
      connection_uid = self.game_manager.connect(nameval)

      # check if the game room is locked or not
      if connection_uid is False:
        messagebox.showerror(self.window_title, "Game already started. Cannot join a locked room.")
        return

      # save the connection uid
      self.game_storage['connection_uid'] = connection_uid

      # save the plain name
      self.game_storage['current_name'] = nameval

      # set the player to ready status
      self.game_manager.make_ready(self.game_storage['connection_uid'])

      # [Debug Statement] ::start
      print("Connection UID: %s" % self.game_storage['connection_uid'])
      # [Debug Statement] ::end

      # hide the input/start_btn and change the label
      self.toggle_name_input(True)

      # assemble card cache
      self.assemble_card_cache()

      # create thread for waiting for other players
      self.game_threads['wait_for_players'] = {}

      # TODO: delete this after waiting for other players
      self.game_threads['wait_for_players']['evt'] = threading.Event()
      self.game_threads['wait_for_players']['thread'] = threading.Thread(
        name="wait_for_players_thread",
        target=self.check_if_ready,
        args=(self.game_threads['wait_for_players']['evt'], self.game_manager,),
        kwargs={
          'on_room_destroyed': lambda: self.disconnect(True),
          'on_room_completed': lambda: self.switch_context('main')
        }
      )

      # start the waiting thread
      self.game_threads['wait_for_players']['thread'].start()
    except (ConnectionRefusedError, CommunicationError):
      # show message to the user
      messagebox.showerror(self.window_title, "Failed to connect to server. Try again later.")

      # show trace to the client
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

  # TODO: implement game disconnection when inside the game
  def disconnect(self, force=False):
    try:
      # disconnect to the server
      self.game_manager.disconnect(self.game_storage['connection_uid'])

      if force is True:
        self.toggle_name_input(False)

        # show message when there are not enough players connected
        messagebox.showerror(self.window_title, "Not enough players to connected to the server.")
      else:
        # implement switching from main gui to splash gui
        pass

      # delete the connection UID
      del self.game_storage['connection_uid']

      # delete the name
      del self.game_storage['current_name']
    except SerializeError:
      print("Pyro traceback:")
      print("".join(PyroExceptionTraceback()))

  def draw_cards_on_canvas(self, identifier, cards):
    # resolve the canvas id
    canvas_id = "player_canvas_%s" % identifier
    player_on_hand_key = "cards_on_hand_%s" % identifier

    resolved_label = "You"
    has_hidden_card = False

    if identifier != self.game_storage['connection_uid']:
      resolved_label = strip_uid(identifier)
      has_hidden_card = True

    # load the cards on the player canvas
    if player_on_hand_key in self.game_storage:
      self.load_cards(cards, self.game_storage[player_on_hand_key], self.main_gui_items[canvas_id], has_hidden_card)

      # resolve the label key
      label_key = "player_label_%s" % identifier

      # get the total of the draw cards
      initial_score = 0

      try:
        initial_score = self.game_manager.get_player_card_total(identifier, has_hidden_card)
      except SerializeError:
        print("Pyro traceback:")
        print("".join(PyroExceptionTraceback()))

      # show the new score on the canvas
      self.reflect_score(self.main_gui_items[canvas_id], self.main_gui_items[label_key], resolved_label, initial_score)

    print('Drawing Complete')

  def load_cards(self, cards, card_collection, canvas, has_hidden_card=False):
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

      if has_hidden_card is True and new_idx == (num_cards - 1):
        is_hidden = True

        resolved_cache_item = self.window.card_cache['blank']

      if resolved_cache_item is None:
        resolved_cache_item = self.window.card_cache[card_text]

         # resolve the new x_position
      x_pos = ((new_idx * (CARD_WIDTH + 2)) + 5)

      # draw image on the canvas
      img_item = canvas.create_image(x_pos,
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

      # # store the hidden card
      # if is_hidden:
      #   self.server_hidden_card = card_metadata

      card_collection.append(card_metadata)

  def assemble_card_cache(self):
    tmp_deck = SerializableDeck()
    tmp_deck.create()

    cards = tmp_deck.get_cards()

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

  def set_game_manager(self, game_manager: PyroProxy):
    self.game_manager = game_manager

  def check_if_ready(self, stop_event, game_manager, **kwargs):
    end_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
    room_is_complete = False

    while not stop_event.is_set():
      # stop infinite loop when it passed the time delta
      if datetime.datetime.now() >= end_time:
        if game_manager.is_room_ready() is True:
          room_is_complete = True
        break

      if game_manager.is_room_ready() is True and game_manager.player_ready_count() == 4:
        room_is_complete = True
        break

    if stop_event.is_set():
      print('Thread terminated')

      if 'on_thread_terminated' in kwargs and callable(kwargs['on_thread_terminated']):
        kwargs['on_thread_terminated']()
    else:
      if room_is_complete is True:
        print('Go to main game screen')

        # lock the game to prevent other players from joining
        game_manager.lock_game(True)

        if 'on_room_completed' in kwargs and callable(kwargs['on_room_completed']):
          kwargs['on_room_completed']()
      else:
        print("Destroy Game Room. Player count is %s" % game_manager.player_ready_count())

        if 'on_room_destroyed' in kwargs and callable(kwargs['on_room_destroyed']):
          kwargs['on_room_destroyed']()

  def draw_player_cards(self, stop_event, game_manager, **kwargs):
    excluded_uids = []

    # TODO: add check if the passwd argument is list
    if 'excluded_uids' in kwargs:
      excluded_uids = kwargs['excluded_uids']

    while not stop_event.is_set():
      on_hands = game_manager.get_player_cards(excluded_uids)

      # no more to draw
      if len(on_hands) == 0:
        break

      for identifier, hand in on_hands.items():
        if len(hand) > 0:
          print(identifier)
          print(hand)

          # exclude the identifier for the next iteration
          excluded_uids.append(identifier)

          if 'on_hand' in kwargs and callable(kwargs['on_hand']):
            kwargs['on_hand'](identifier, hand)

    if stop_event.is_set():
      print('Thread terminated')

      if 'on_thread_terminated' in kwargs and callable(kwargs['on_thread_terminated']):
        kwargs['on_thread_terminated']()
    else:
      print('Draw complete')

      if 'on_draw_complete' in kwargs and callable(kwargs['on_draw_complete']):
        kwargs['on_draw_complete']()

  def find_winners(self, stop_event, game_manager, **kwargs):
    response = []

    while not stop_event.is_set():
      response = game_manager.determine_winners()

      if response is not None:
        break

    if stop_event.is_set():
      print('Thread terminated')

      if 'on_thread_terminated' in kwargs and callable(kwargs['on_thread_terminated']):
        kwargs['on_thread_terminated']()
    else:
      if 'on_identify_winners' in kwargs and callable(kwargs['on_identify_winners']):
        kwargs['on_identify_winners'](response)


