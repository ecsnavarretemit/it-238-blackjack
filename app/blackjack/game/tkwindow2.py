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
from app.cards.transformer import CardToCardImagePositionTransformer, BLANK_COORDS, CARD_WIDTH
from app.blackjack.game.error import GameError
from app.blackjack.cards.transformer import TextToCardTransformer
from app.blackjack.cards.deck import SerializableDeck
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
      print("No custom deck connection provided. Establishing connection with default parameters.")

      self.game_manager = PyroProxy("PYRO:standard.deck@localhost:3000")

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
    pass

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

  def toggle_name_input(self, hide=False):
    if hide is True:
      self.splash_gui_items['name_label'].config(text="Looking and waiting for other players...")
      self.splash_gui_items['name_input'].pack_forget()
      self.splash_gui_items['start_btn'].pack_forget()
    else:
      self.splash_gui_items['name_label'].config(text="Your Name:")
      self.splash_gui_items['name_input'].pack()
      self.splash_gui_items['start_btn'].pack()

  def connect_to_server(self):
    try:
      nameval = self.splash_gui_items['name_input'].get().strip()

      if nameval == '':
        messagebox.showerror(self.window_title, "Please provide your name.")
        return

      # save the connection uid
      connection_uid = self.game_manager.connect(nameval)

      # check if the game room is locked or not
      if connection_uid is False:
        messagebox.showerror(self.window_title, "Game already started. Cannot join a locked room.")
        return

      self.game_storage['connection_uid'] = connection_uid

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

      self.game_threads['wait_for_players']['evt'] = threading.Event()
      self.game_threads['wait_for_players']['thread'] = threading.Thread(
        name="wait_for_players_thread",
        target=self.check_if_ready,
        args=(self.game_threads['wait_for_players']['evt'], self.game_manager, ),
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

  def disconnect(self, force=False):
    # disconnect to the server
    self.game_manager.disconnect(self.game_storage['connection_uid'])

    if force is True:
      self.toggle_name_input(False)

      # show message when there are not enough players connected
      messagebox.showerror(self.window_title, "Not enough players to connected to the server.")
    else:
      # implement switching from main gui to splash gui
      pass

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


