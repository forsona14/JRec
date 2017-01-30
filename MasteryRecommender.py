#!/usr/bin/python
# -*- coding: UTF-8 -*-

from math import exp, log, fabs, sqrt
from random import *
from JRecRequest import JRecRequest

class MasteryRecommender:

    INIT_MASTERY = 2.0
    MAX_MASTERY = 4.0
    MIN_MASTERY = 0.0

    ML_RATE = 0.7

    def __init__(self, articles):

        # mastery = -log(P_understand)

        self.articles = articles

        self.mastery = {}
        self.average_mastery = MasteryRecommender.INIT_MASTERY
        self.random = Random()
        self.request_history = []
        self.response_history = []
        self.recommend_mastery = MasteryRecommender.INIT_MASTERY


    def article_mastery(self, article):
        for w in article.uniq_wordlist:
            if self.mastery.has_key(w):
                pass
                #self.mastery[w] = min(self.mastery[w], Recommender.MIN_MASTERY)
            else:
                self.mastery[w] = self.average_mastery
        #return float(sum([self.mastery[w] for w in article.uniq_wordlist])) / sqrt(len(article.uniq_wordlist))
        return float(sum([self.mastery[w] for w in article.uniq_wordlist])) / len(article.uniq_wordlist)

    def request(self):
        if len(self.response_history) < len(self.request_history):
            return JRecRequest(self.articles[self.request_history[-1]])
        res = [[id,self.article_mastery(self.articles[id])] for id in self.articles.keys() if not id in self.request_history]
        if len(res) == 0:
            return None
        self.random.shuffle(res)
        res.sort(key=lambda x:fabs(self.recommend_mastery - x[1]))
        #print self.recommend_mastery, res[0][1], [t[1] for t in res]
        self.request_history.append(res[0][0])
        return JRecRequest(self.articles[self.request_history[-1]])

    def response(self, res):
        article = self.articles[self.request_history[-1]]
        self.response_history.append(res)

        expected_response = self.article_mastery(article) # / len(article.uniq_wordlist)
        if res.understood:
            actual_response = 3
            recommend_mastery_offset = -1
        else:
            actual_response = 1
            recommend_mastery_offset = 1
        step = (actual_response - expected_response) * self.ML_RATE
        #step = step / len(article.uniq_wordlist)
        num_change = len([w for w in article.uniq_wordlist \
                          if self.mastery[w] > MasteryRecommender.MIN_MASTERY and self.mastery[w] < MasteryRecommender.MAX_MASTERY])

        if num_change > 0:
            step = step * len(article.uniq_wordlist) / num_change
        for w in article.uniq_wordlist:
            if self.mastery[w] > MasteryRecommender.MIN_MASTERY and self.mastery[w] < MasteryRecommender.MAX_MASTERY:
                self.mastery[w] += step
            if self.mastery[w] > MasteryRecommender.MAX_MASTERY:
                self.mastery[w] = MasteryRecommender.MAX_MASTERY
            if self.mastery[w] < MasteryRecommender.MIN_MASTERY:
                self.mastery[w] = MasteryRecommender.MIN_MASTERY

        if len(self.response_history) < 2:
            self.recommend_mastery += recommend_mastery_offset * 0.6
        elif len(self.response_history) < 6:
            self.recommend_mastery += recommend_mastery_offset * 0.3
        else:
            self.recommend_mastery += recommend_mastery_offset * 0.1
        if self.recommend_mastery > MasteryRecommender.MAX_MASTERY:
            self.recommend_mastery = MasteryRecommender.MAX_MASTERY
        if self.recommend_mastery < MasteryRecommender.MIN_MASTERY:
            self.recommend_mastery = MasteryRecommender.MIN_MASTERY

        self.average_mastery = sum(self.mastery.values()) / len(self.mastery.values())
