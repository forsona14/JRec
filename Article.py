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


    def inter(self, article):
        inter = 0
        j = 0
        wl1 = sorted(self.wordlist)
        wl2 = sorted(article.wordlist)
        for i in xrange(len(wl1)):
            while j < len(wl2) and wl2[j] < wl1[i]:
                j += 1
            if j < len(wl2) and wl1[i] == wl2[j]:
                inter += 1
                j += 1
        return inter
