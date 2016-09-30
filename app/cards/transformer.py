# transformer.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.2

import os
import re
from PIL import Image
from app.cards.card import Card, SHAPES, FACE_VALUES
from app.cards.error import TransformerError
from app.blackjack.game.error import GameError

MOVE_X = 78
MOVE_Y = 120

BLANK_COORDS = (158, 492, 237, 615)

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

# [Image Position Resolution] ::start
card_img_path = os.path.join(os.getcwd(), "resources/images/cards.png")

if not os.path.exists(card_img_path):
  raise GameError("Card Faces sprite does not exist!")

# open the image file
card_img = Image.open(card_img_path)

# destructure list
width, height = card_img.size

CARD_WIDTH = int(width / 13)
CARD_HEIGHT = int(height / 5)

top = 0
right = CARD_WIDTH
bottom = CARD_HEIGHT
left = 0

# create tmp coordinates
tmp_top = top
tmp_right = right
tmp_bottom = bottom
tmp_left = left

# prevent garbage collection that's why we are storing the reference to the window object
resolved_cards = {}

for shape_idx in range(0, len(SHAPES)):
  for face_idx in range(0, len(FACE_VALUES)):
    # assemble dictionary key
    key = "%s of %s" % (FACE_VALUES[face_idx], SHAPES[shape_idx])

    # store the position
    resolved_cards[key] = (tmp_left, tmp_top, tmp_right, tmp_bottom)

    # adjust left and right coordinates
    tmp_left += right
    tmp_right += right

  # reset top and left coordinates
  tmp_left = 0
  tmp_right = right

  # adjust top and bottom coordinates
  tmp_top += bottom
  tmp_bottom += bottom

# close the file pointer
card_img.close()
# [Image Position Resolution] ::end

# utility functions
def get_card_attrs(coords):
  found_card = None

  for card, card_coords in resolved_cards.items():
    if set(coords) == set(card_coords) and len(coords) == len(card_coords):
      found_card = card
      break

  if found_card is None:
    raise TransformerError("Cant transform to card by its position")

  # convert to card instance to extract face and shape
  transformed_card = TextToCardTransformer(found_card).transform()

  return {
    'face': transformed_card.get_face_value(),
    'shape': transformed_card.get_shape()
  }

def get_card_coords(face_value, shape):
  if not face_value in FACE_VALUES:
    raise TransformerError("Face Value: %s is not a valid face." % face_value)

  if not shape in SHAPES:
    raise TransformerError("Shape: %s is not a valid card shape." % shape)

  # assemble dictionary key
  card_key = "%s of %s" % (face_value, shape)

  # throw error when card_key does not exist
  if not card_key in resolved_cards:
    raise TransformerError("Card coordinates not found.")

  return resolved_cards[card_key]


