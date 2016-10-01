# manager.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.1.0

import Pyro4
from app.helpers import rand_uid
from app.blackjack.cards.deck import SerializableDeck

MAX_PLAYERS = 4

class State(object):

  def __init__(self, name, ip, socket):
    # save the name
    self.name = name

    # save the IP address
    self.ip = ip

    # save the socket
    self.socket = socket

@Pyro4.expose
class Manager(object):

  def __init__(self):
    # create deck object
    self.deck = SerializableDeck()

    # save state
    self.states = {}

    # boolean to determine whether a game is on going or not
    self.room_locked = False

    # create the game deck
    self.init_deck()

  def get_states(self):
    return self.states

  def init_deck(self):
    # create the deck
    self.deck.create()

    # shuffle the deck
    self.deck.shuffle()

  # TODO: throw error when number_of_cards is less than 1
  def draw_cards(self, identifier, number_of_cards=2):
    drawn_cards = self.deck.pluck(number_of_cards)

    if identifier in self.states and not 'cards_on_hand' in self.states[identifier]:
      self.states[identifier]['cards_on_hand'] = []

    if identifier in self.states:
      for card in drawn_cards:
        self.states[identifier]['cards_on_hand'].append(card)

      print("Drawn card. State of %s modified" % identifier)
      print(self.states[identifier])

    return drawn_cards

  def get_player_cards(self, exclude_uids=None):
    result = {}

    for identifier, state in self.states.items():
      # skip to the next iteration when the identifier needs to be excluded
      if exclude_uids is not None and identifier in exclude_uids:
        continue

      on_hand = []

      if 'cards_on_hand' in state:
        on_hand = state['cards_on_hand']

      result[identifier] = on_hand

    return result

  def lock_game(self, lock=True):
    self.room_locked = lock

  def make_ready(self, identifier):
    if identifier in self.states:
      self.states[identifier]['is_ready'] = True

  def is_room_ready(self):
    player_ready_count = self.player_ready_count()

    if player_ready_count > 1:
      return True

    return False

  def player_ready_count(self):
    counter = 0

    for _, state in self.states.items():
      if state['is_ready'] is True:
        counter += 1

    return counter

  def get_player_uids(self):
    key_list = []

    for key, state in self.states.items():
      if state['is_ready'] is True:
        key_list.append(key)

    return key_list

  def disconnect(self, identifier):
    if identifier in self.states:
      del self.states[identifier]

      print("player left the game: %s" % identifier)
      print(self.states)

      return True

    return False

  def connect(self, name):
    if self.room_locked is True:
      print("Player: %s is trying to connect a locked game.")
      return False

    key = name + ':uid-' + rand_uid(10)

    self.states[key] = {
      'games_played': 0,
      'total_wins': 0,
      'total_losses': 0,
      'is_ready': False
    }

    print("joined player: %s" % key)
    print(self.states[key])

    return key


