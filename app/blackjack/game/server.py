# server.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.1.0

# from app.blackjack.cards.deck import SerializableDeck
from app.blackjack.game.manager import Manager
# from app.cards.deck import Deck
from Pyro4.core import Daemon as PyroDaemon

class Server(object):

  def __init__(self):
    # initialize game manager
    self.game_manager = Manager()

    # store connection details
    self.server_host = "localhost"
    self.server_port = 3000

  def start(self, managerlabel=None):
    if managerlabel is None:
      managerlabel = "standard.manager"

    PyroDaemon.serveSimple({
      self.game_manager: managerlabel
    }, ns=False, host=self.server_host, port=self.server_port)

  def get_game_manager(self):
    return self.game_manager

  def set_game_manager(self, game_manager: Manager):
    self.game_manager = game_manager

  def get_host(self):
    return self.server_host

  def set_host(self, host: str):
    self.server_host = host

  def get_port(self):
    return self.server_port

  def set_port(self, port: int):
    self.server_port = port


