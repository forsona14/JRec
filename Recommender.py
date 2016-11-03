#!/usr/bin/python
# -*- coding: UTF-8 -*-

from math import exp, log
from random import *

class Recommender:

    INIT_MASTERY = 2

    ML_RATE = 1

    def __init__(self):

        # mastery = -log(P_understand)
        self.mastery = {}
        self.seen = set([])
        self.random = Random()


    def article_mastery(self, article):
        for w in article.uniq_wordlist:
            if self.mastery.has_key(w):
                pass
                #self.mastery[w] = min(self.mastery[w], Recommender.MIN_MASTERY)
            else:
                self.mastery[w] = Recommender.INIT_MASTERY
        return float(sum([self.mastery[w] for w in article.uniq_wordlist])) / len(article.uniq_wordlist)


    # articles:  {id : article}
    # return article
    def feed(self, articles):
        res = [[id,self.article_mastery(articles[id])] for id in articles.keys() if not id in self.seen]
        if len(res) == 0:
            return None
        self.random.shuffle(res)
        res.sort(key=lambda x:x[1])
        return articles[res[0][0]]

    # response: -log(percentage_understand)
    def feedback(self, article, response):
        expected_response = self.article_mastery(article)
        step = (response - expected_response) * self.ML_RATE
        #step = step / len(article.uniq_wordlist)
        for w in article.uniq_wordlist:
            self.mastery[w] += step
        self.seen.add(article.id)
