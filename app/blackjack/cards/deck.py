# deck.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

from app.blackjack.cards.card import Card
from app.cards.deck import Deck as BaseDeck

class Deck(BaseDeck):

  def __init__(self):
    BaseDeck.__init__(self)

  def create(self):
    self.cards.clear()

    for shape in self.shapes:
      for face_value in self.face_values:
        self.cards.append(Card(shape, face_value))


