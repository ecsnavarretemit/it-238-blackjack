# blackjackcard.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

from app.cards.card import Card

class BlackJackCard(Card):

  def __init__(self, shape=None, face_value=None):
    Card.__init__(self, shape, face_value)

  def get_normalized_value(self):
    try:
      self.normalized_value = int(self.face_value)
    except ValueError:
      if self.face_value in ['J', 'Q', 'K']:
        self.normalized_value = 10
      else:
        # In BlackJack, A can have a value of 1 or 11
        # If the total value of cards is less than or equal to 10,
        # the value is changed to 11 else it will defaulted to 1
        #
        # We will set it to 1 and override the value on the game logic
        self.normalized_value = 1

    return self.normalized_value

