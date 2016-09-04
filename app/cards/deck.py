# deck.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

from random import shuffle
from app.cards.card import Card
from app.cards.carderror import CardError

class Deck(object):

  def __init__(self):
    self.cards = []

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
      raise CardError("No cards in deck. call Deck.create()")

    shuffle(self.cards)

  def get_cards(self):
    if len(self.cards) == 0:
      raise CardError("No cards in deck. call Deck.create()")

    return self.cards


