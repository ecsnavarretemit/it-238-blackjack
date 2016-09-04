# carderror.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

from app.error import Error

class CardError(Error):
  """Error class for related in processing cards."""

  def __init__(self, message):
    # call the parent class __init__
    Error.__init__(self)

    # store the message
    self.message = message

