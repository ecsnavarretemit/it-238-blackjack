# error.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.2

from app.error import Error

class GameError(Error):
  """Error class for the game submodule."""

  def __init__(self, message):
    # call the parent class __init__
    Error.__init__(self)

    # store the message
    self.message = message

