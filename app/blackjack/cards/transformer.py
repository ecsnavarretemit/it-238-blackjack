# transformer.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

from app.blackjack.cards.card import Card
from app.cards.transformer import TextToCardTransformer as BaseTextToCardTransformer
from app.cards.error import TransformerError
import re

class TextToCardTransformer(BaseTextToCardTransformer):
  """Transformer class for deserializing text back to black jack card instances"""

  def __init__(self, text=None):
    BaseTextToCardTransformer.__init__(self, text)

  def transform(self):
    if self.text == None or self.text == '':
      raise TransformerError("Set a serialized text of the card first before transforming it")

    matches = re.search('([0-9JQKA]+) of (diamond|heart|spade|clover)', self.text)

    if not matches:
      raise TransformerError("Cant deserialize card: %s" % self.text)

    return Card(matches.group(2), matches.group(1))


