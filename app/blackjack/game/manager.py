# manager.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.1.0

import Pyro4
from app.logger import Logger
from app.helpers import rand_uid, strip_uid
from app.blackjack.cards.deck import SerializableDeck
from app.blackjack.cards.transformer import TextToCardTransformer

MAX_PLAYERS = 4

# TODO: implement logic for incrementing 'games_played', 'total_wins' and 'total_losses'
@Pyro4.expose
class Manager(object):

  def __init__(self):
    # create deck object
    self.deck = SerializableDeck()

    # save state
    self.states = {}

    # message logging
    self.logger = Logger("BlackJack State Manager")

    # boolean to determine whether a game is on going or not
    self.room_locked = False

    # boolean if new game is requested
    self.is_new_game_requested = False

    # blackjack goal number
    self.winning_number = 21

    # create the game deck
    self.init_deck()

  def get_states(self):
    return self.states

  def init_deck(self):
    # create the deck
    self.deck.create()

    # shuffle the deck
    self.deck.shuffle()

  # def new_game(self):
  #   for _, state in self.states.items():
  #     state['games_played'] += 1

  #     # unlock hand
  #     state['hand_locked'] = False

  #     # make sure player is ready
  #     state['is_ready'] = True

  #     # empty the cards on hand
  #     state['cards_on_hand'] = []

  #     if self.logger != None:
  #       self.logger.log('new_game', "reset state")

  def new_game(self, identifier):
    if self.is_new_game_requested is False:
      for _, state in self.states.items():
        # make sure player is not ready
        state['is_ready'] = False

      self.is_new_game_requested = True

    # increment the number of games played
    self.states[identifier]['games_played'] += 1

    # unlock hand
    self.states[identifier]['hand_locked'] = False

    # empty the cards on hand
    self.states[identifier]['cards_on_hand'] = []

    if self.logger != None:
      self.logger.log('new_game', "Starting a new game.")

  # TODO: throw error when number_of_cards is less than 1
  # TODO: implement card refresh when the number of remaining cards in the deck is less than 10
  def draw_cards(self, identifier, number_of_cards=2):
    drawn_cards = []

    # do not invoke pluck when hand is locked
    if self.states[identifier]['hand_locked'] is False:
      drawn_cards = self.deck.pluck(number_of_cards)

    if identifier in self.states and not 'cards_on_hand' in self.states[identifier]:
      self.states[identifier]['cards_on_hand'] = []

    if identifier in self.states:
      for card in drawn_cards:
        self.states[identifier]['cards_on_hand'].append(card)

      if self.logger != None:
        self.logger.log("Drawn card. State of %s modified" % identifier, self.states[identifier])

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

  def get_player_card_total(self, identifier, count_only_first=False):
    card_total = 0
    ace_counter = 0

    if identifier in self.states:
      card_collection = self.states[identifier]['cards_on_hand']

      # extract the first card
      if count_only_first is True and len(card_collection) > 0:
        card_collection = [card_collection[0]]

      for card in card_collection:
        card_obj = TextToCardTransformer(card).transform()
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

  def determine_winners(self):
    is_all_locked = True

    # reset the flag
    self.is_new_game_requested = False

    scores_dict = {}
    for identifier, state in self.states.items():
      if state['hand_locked'] is False:
        is_all_locked = False
        break

      card_total = self.get_player_card_total(identifier, False)

      tmp_score = self.winning_number - card_total

      # store identifiers and scores which is greater than or equal to 0
      if tmp_score >= 0:
        scores_dict[identifier] = tmp_score

    # before we determine the actual winner, all states must be hand_locked!
    if is_all_locked is False:
      return None

    min_val = 0

    if len(scores_dict) > 0:
      min_val = min(scores_dict.values())

    winners = []
    matching_score = 0
    for f_identifier, score in scores_dict.items():
      if score == min_val:
        winners.append(strip_uid(f_identifier))
        matching_score = self.get_player_card_total(f_identifier, False)

    return {
      'winners': winners,
      'score': matching_score
    }

  def lock_hand(self, identifier, lock=True):
    if identifier in self.states:
      self.states[identifier]['hand_locked'] = lock

  def lock_game(self, lock=True):
    self.room_locked = lock

  def make_ready(self, identifier, ready=True):
    if identifier in self.states:
      self.states[identifier]['is_ready'] = ready

  def is_room_ready(self):
    player_ready_count = self.player_ready_count()

    if player_ready_count > 1:
      return True

    return False

  def player_count(self):
    return len(self.states)

  def player_ready_count(self):
    counter = 0

    for _, state in self.states.items():
      if state['is_ready'] is True:
        counter += 1

    return counter

  def get_player_uids(self):
    identifiter_list = []

    for identifier, _ in self.states.items():
      identifiter_list.append(identifier)

    return identifiter_list

  def disconnect(self, identifier):
    if identifier in self.states:
      del self.states[identifier]

      if self.logger != None:
        self.logger.log("Player left: %s" % identifier, self.states)

      return True

    return False

  def connect(self, name):
    if self.room_locked is True:
      if self.logger != None:
        self.logger.log("connect", "Player: %s is trying to connect a locked game." % name)
      return False

    key = name + ':uid-' + rand_uid(10)

    self.states[key] = {
      'games_played': 0,
      'total_wins': 0,
      'total_losses': 0,
      'is_ready': False,
      'hand_locked': False
    }

    if self.logger != None:
      self.logger.log("Player Joined: %s" % key, self.states[key])

    return key


