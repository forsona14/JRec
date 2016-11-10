#!/usr/bin/python
# -*- coding: UTF-8 -*-

from math import exp, log, fabs, sqrt
from random import *

class Recommender:

    INIT_MASTERY = 2

    ML_RATE = 0.7

    def __init__(self):

        # mastery = -log(P_understand)
        self.mastery = {}
        self.random = Random()
        self.article_history = []
        self.response_history = []


    def article_mastery(self, article):
        for w in article.uniq_wordlist:
            if self.mastery.has_key(w):
                pass
                #self.mastery[w] = min(self.mastery[w], Recommender.MIN_MASTERY)
            else:
                self.mastery[w] = Recommender.INIT_MASTERY
        return float(sum([self.mastery[w] for w in article.uniq_wordlist])) / sqrt(len(article.uniq_wordlist))
        #return float(sum([self.mastery[w] for w in article.uniq_wordlist])) / len(article.uniq_wordlist)


    def expected_response(self):
        # Consider local (4) average response
        if len(self.response_history) == 0:
            avg_res = Recommender.INIT_MASTERY
        elif len(self.response_history) < 4:
            avg_res = float(sum(self.response_history)) / len(self.response_history)
        else:
            avg_res = float(sum(self.response_history[-4:])) / 4
        # N+1 heuristic
        expected_res = (4 - avg_res) + 0.3
        return expected_res

    # articles:  {id : article}
    # return article
    def feed(self, articles):
        res = [[id,self.article_mastery(articles[id])] for id in articles.keys() if not id in self.article_history]
        if len(res) == 0:
            return None
        self.random.shuffle(res)
        exp_res = self.expected_response()
        res.sort(key=lambda x:fabs(exp_res - x[1]))
        print exp_res, res[0][1], [t[1] for t in res]
        return articles[res[0][0]]

    # response: -log(percentage_understand)
    def feedback(self, article, response):
        expected_response = self.article_mastery(article) / sqrt(len(article.uniq_wordlist))
        step = (response - expected_response) * self.ML_RATE
        #step = step / len(article.uniq_wordlist)
        for w in article.uniq_wordlist:
            self.mastery[w] += step
        self.article_history.append(article.id)
        self.response_history.append(response)
