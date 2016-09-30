# deck.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.1.0

from app.blackjack.cards.card import Card
from app.cards.card import FACE_VALUES, SHAPES
from app.cards.deck import Deck as BaseDeck
from app.cards.transformer import CardToTextTransformer
import Pyro4

class Deck(BaseDeck):

  def __init__(self):
    BaseDeck.__init__(self)

  def create(self):
    self.cards.clear()

    for shape in SHAPES:
      for face_value in FACE_VALUES:
        self.cards.append(Card(shape, face_value))

@Pyro4.expose
class SerializableDeck(Deck):

  def __init__(self):
    Deck.__init__(self)

  def create(self):
    Deck.create(self)

  def shuffle(self):
    Deck.shuffle(self)

  def pluck(self, number_of_cards):
    plucked = Deck.pluck(self, number_of_cards)

    serialized = []

    for card in plucked:
      serialized.append(CardToTextTransformer(card).transform())

    return serialized

  def get_cards(self):
    cards = Deck.get_cards(self)

    serialized = []

    for card in cards:
      serialized.append(CardToTextTransformer(card).transform())

    return serialized

  def get_remaining_cards(self):
    return Deck.get_remaining_cards(self)


