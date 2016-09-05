# transformer.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

import re
from app.cards.card import Card, SHAPES, FACE_VALUES
from app.cards.error import TransformerError

MOVE_X = 78
MOVE_Y = 120

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

class CardImagePositionToCardTransformer(Transformer):
  """Transformer class for x and y coordinates back to Card Instance"""

  def __init__(self, position=None):
    Transformer.__init__(self)

    # Initialize coordinates to None
    self.position = None

    if position != None:
      self.set_position(position)

  def set_position(self, position):
    self.position = position

  def transform(self):
    if self.position is None:
      raise TransformerError("Set coordinates first before transforming it.")

    card_attrs = get_card_attrs(self.position)

    return Card(card_attrs['shape'], card_attrs['face'])

class CardToCardImagePositionTransformer(Transformer):
  """Transformer class for cards to be converted to x and y coordinates"""

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

    return get_card_coords(self.card.get_face_value(), self.card.get_shape())

# utility functions

# [Initialize Position Values] ::start
x_positions = {}
y_positions = {}

for x in range(0, len(FACE_VALUES)):
  resolved_face = FACE_VALUES[x]

  x_positions[resolved_face] = x * MOVE_X * -1

for y in range(0, len(SHAPES)):
  resolved_shape = SHAPES[y]

  y_positions[resolved_shape] = y * MOVE_Y * -1
# [Initialize Position Values] ::end

def get_card_attrs(position):
  found_face = None
  found_shape = None

  for face_value, x_position in x_positions.items():
    if x_position == position['x']:
      found_face = face_value
      break

  for shape, y_position in y_positions.items():
    if y_position == position['y']:
      found_shape = shape
      break

  if found_face is None or found_shape is None:
    raise TransformerError("Cant transform to card by its position")

  return {
    'face': found_face,
    'shape': found_shape
  }

def get_card_coords(face_value, shape):
  if not face_value in FACE_VALUES:
    raise TransformerError("Set a card first before transforming it")

  if not shape in SHAPES:
    raise TransformerError("Set a card first before transforming it")

  return {
    'x': x_positions[face_value],
    'y': y_positions[shape]
  }


