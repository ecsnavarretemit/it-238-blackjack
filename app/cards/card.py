# card.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

from app.cards.carderror import CardError

class Card(object):
  shapes = ["diamond", "heart", "spade", "clover"]

  def __init__(self, shape=None, face_value=None):
    # define the face values 2-10, J, Q, K, A
    self.face_values = [str(i) for i in list(range(2, 11))] + ['J', 'Q', 'K', 'A']

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
    if shape in self.shapes:
      self.shape = shape
    else:
      raise CardError("Shape: %s does not exist" % shape)

  def get_face_value(self):
    return self.face_value

  def set_face_value(self, face_value):
    if face_value in self.face_values:
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


