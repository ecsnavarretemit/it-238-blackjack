# deck.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

from random import shuffle
from collections import deque
from app.cards.card import Card, FACE_VALUES, SHAPES
from app.cards.error import DeckError

class Deck(object):

  def __init__(self):
    self.cards = deque([])

  def create(self):
    self.cards.clear()

    for shape in SHAPES:
      for face_value in FACE_VALUES:
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

  def get_remaining_cards(self):
    return len(self.get_cards())


