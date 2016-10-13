# logger.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.1.3

class Logger(object):

  def __init__(self, title="Logger"):
    self.title = title

  def log(self, label, message):
    print("%s - %s:" % (self.title, label))
    print(message)
    print("")


