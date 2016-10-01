# helpers.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.1.3

import string
import random

def rand_uid(length):
  str_pool = string.ascii_lowercase + string.ascii_uppercase + string.digits
  random_str = ''.join((random.SystemRandom().choice(str_pool) for _ in range(length)))

  return random_str

def strip_uid(text_with_uid, identifier_prefix=":uid-"):
  return text_with_uid[0:text_with_uid.rfind(identifier_prefix)]

def extract_uid(text_with_uid, identifier_prefix=":uid-"):
  start = len(identifier_prefix) + text_with_uid.rfind(identifier_prefix)

  return text_with_uid[start:]


