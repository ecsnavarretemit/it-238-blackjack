#!/usr/bin/env python

# server.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

from app.blackjack.game.server import Server

def main():
  Server().start()

if __name__ == "__main__":
  main()

