# server.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

from app.blackjack.cards.deck import SerializableDeck
from app.cards.deck import Deck
from Pyro4.core import Daemon as PyroDaemon

class Server(object):

  def __init__(self):
    # create deck object
    self.deck = SerializableDeck()

    # store connection details
    self.server_host = "localhost"
    self.server_port = 3000

  def start(self, decklabel=None):
    if decklabel is None:
      decklabel = "standard.deck"

    PyroDaemon.serveSimple({
      self.deck: decklabel
    }, ns=False, host=self.server_host, port=self.server_port)

  def get_deck(self):
    return self.deck

  def set_deck(self, deck: Deck):
    self.deck = deck

  def get_host(self):
    return self.server_host

  def set_host(self, host: str):
    self.server_host = host

  def get_port(self):
    return self.server_port

  def set_port(self, port: int):
    self.server_port = port


