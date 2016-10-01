#!/usr/bin/env python

# game.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.1.0

import os
from yaml import load as yaml_load
from Pyro4.core import Proxy as PyroProxy
from app.blackjack.game.tkwindow2 import Window as GameWindow

def main():
  # application configuration
  config = os.path.join(os.getcwd(), "conf/main.yml")

  window = GameWindow()

  # override the default server settings when yaml file exists
  if os.path.exists(config):
    # open the file and store to the yaml_config variable
    yaml_config = open(config)

    # store the refernce to the config
    config = yaml_load(yaml_config)

    # PYRO:standard.deck@localhost:3000
    game_manager = PyroProxy("PYRO:%s@%s:%d" % (config['app']['manager']['object_name'],
                             config['app']['server']['host'],
                             config['app']['server']['port']))

    # set the game deck
    window.set_game_manager(game_manager)

    # close the file since we do not need it anymore
    yaml_config.close()

  # start application
  window.bootstrap()

if __name__ == "__main__":
  main()


