#!/usr/bin/python
# -*- coding: UTF-8 -*-

from JPEDU.WordStats import get_word_list_of_text
from JPEDU.Japanese import stoplist

class Article:
    def __init__(self, id, text):
        self.id = id
        self.text = text
        wl = get_word_list_of_text(text)
        self.wordlist = [w for w in wl if not w in stoplist]
        self.uniq_wordlist = list(set(self.wordlist))