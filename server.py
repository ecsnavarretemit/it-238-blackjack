#!/usr/bin/env python

# server.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.1

import os
from yaml import load as yaml_load
from app.blackjack.game.server import Server

def main():
  # application configuration
  config = os.path.join(os.getcwd(), "conf/main.yml")

  # create an instance of the server
  server = Server()

  # override the default server settings when yaml file exists
  if os.path.exists(config):
    # open the file and store to the yaml_config variable
    yaml_config = open(config)

    # store the refernce to the config
    config = yaml_load(yaml_config)

    # set the server host
    server.set_host(config['app']['server']['host'])

    # set the server port
    server.set_port(config['app']['server']['port'])

    # close the file since we do not need it anymore
    yaml_config.close()

    # start the server with custom deck name
    server.start(config['app']['deck']['object_name'])
  else:
    # start the server default settings
    server.start()

if __name__ == "__main__":
  main()


