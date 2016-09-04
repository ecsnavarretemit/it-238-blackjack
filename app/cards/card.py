# card.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

from app.cards.error import CardError

FACE_VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
SHAPES = ["diamond", "heart", "spade", "clover"]

class Card(object):

  def __init__(self, shape=None, face_value=None):
    # translated value of the face value for example
    # A of Hearts = 1
    self.normalized_value = None

    # store the shape if provided
    if shape != None:
      self.set_shape(shape)

    # store the face_value if provided
    if face_value != None:
      self.set_face_value(face_value)

  def get_shape(self):
    return self.shape

  def set_shape(self, shape):
    if shape in SHAPES:
      self.shape = shape
    else:
      raise CardError("Shape: %s does not exist" % shape)

  def get_face_value(self):
    return self.face_value

  def set_face_value(self, face_value):
    if face_value in FACE_VALUES:
      self.face_value = face_value
    else:
      raise CardError("Face Value: %s does not exist" % face_value)

  def get_normalized_value(self):
    try:
      self.normalized_value = int(self.face_value)
    except ValueError:
      if self.face_value == 'J':
        self.normalized_value = 11
      elif self.face_value == 'Q':
        self.normalized_value = 12
      elif self.face_value == 'K':
        self.normalized_value = 13
      else:
        #value for Ace
        self.normalized_value = 1

    return self.normalized_value


