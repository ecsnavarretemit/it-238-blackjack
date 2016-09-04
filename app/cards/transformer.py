# transformer.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

import re
from app.cards.card import Card, SHAPES
from app.cards.error import TransformerError

class Transformer(object):
  """Base class for card transformers in this module."""
  pass

class CardToTextTransformer(Transformer):
  """Transformer class for cards to text for sending over the network"""

  def __init__(self, card=None):
    Transformer.__init__(self)

    # Initialize card to None
    self.card = None

    if card != None:
      self.set_card(card)

  def set_card(self, card: Card):
    self.card = card

  def transform(self):
    if self.card is None:
      raise TransformerError("Set a card first before transforming it")

    return "%s of %s" % (self.card.get_face_value(), self.card.get_shape())

class TextToCardTransformer(Transformer):
  """Transformer class for deserializing text back to card instances"""

  def __init__(self, text=None):
    Transformer.__init__(self)

    # Initialize card to None
    self.text = None

    if text != None:
      self.set_text(text)

  def set_text(self, text):
    self.text = text

  def transform(self):
    if self.text is None or self.text == '':
      raise TransformerError("Set a serialized text of the card first before transforming it")

    matches = re.search('([0-9JQKA]+) of (' + '|'.join(SHAPES) + ')', self.text)

    if not matches:
      raise TransformerError("Cant deserialize card: %s" % self.text)

    return Card(matches.group(2), matches.group(1))


