# card.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

from blackjack.error import Error

class CardError(Error):
  """Error class for related in processing cards."""

  def __init__(self, message):
    self.message = message

