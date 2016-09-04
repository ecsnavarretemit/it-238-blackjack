# deck.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

from random import shuffle
from collections import deque
from app.cards.card import Card
from app.cards.error import DeckError

class Deck(object):

  def __init__(self):
    self.cards = deque([])

    # card face values 2-10, J, Q, K, A
    self.face_values = [str(i) for i in list(range(2, 11))] + ['J', 'Q', 'K', 'A']

    # card shapes
    self.shapes = ["diamond", "heart", "spade", "clover"]

  def create(self):
    self.cards.clear()

    for shape in self.shapes:
      for face_value in self.face_values:
        self.cards.append(Card(shape, face_value))

  def shuffle(self):
    if len(self.cards) == 0:
      raise DeckError("No cards in deck. call Deck.create()")

    shuffle(self.cards)

  def pluck(self, number_of_cards):
    if number_of_cards <= 0:
      raise DeckError("Can't get cards from the deck. Please specify an integer value greater than 0.")

    try:
      cards = []

      for _ in list(range(0, number_of_cards)):
        cards.append(self.cards.popleft())

    except ValueError:
      raise DeckError("Can't get cards from the deck. Please specify an integer value.")

    return cards

  def get_cards(self):
    if len(self.cards) == 0:
      raise DeckError("No cards in deck. call Deck.create()")

    return self.cards


