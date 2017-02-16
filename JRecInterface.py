#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
from Article import Article
from MasteryRecommender import MasteryRecommender
from JRecResponse import JRecResponse
import nhk_easy

class JRecInterface:

    def __init__(self, fn='Text/nhk_easy.txt'):
        #self.articles = JRecInterface.read_articles(fn)
        self.articles = nhk_easy.read_articles()
        self.all_wordlist = []
        self.all_uniq_wordlist = []
        for a in self.articles.values():
            self.all_wordlist += a.wordlist
        self.all_wordlist = sorted(self.all_wordlist)
        self.all_uniq_wordlist = list(set(self.all_wordlist))
        self.word_index = {self.all_uniq_wordlist[i]:i for i in xrange(len(self.all_uniq_wordlist))}
        self.recommender = MasteryRecommender(self.articles)
        self.display_article = 0

    def request(self):
        return self.recommender.request()

    def response(self, res):
        if type(res) == bool or type(res) == int or type(res) == float:
            res = JRecResponse(res)
        self.recommender.response(res)

