#!/usr/bin/python
# -*- coding: UTF-8 -*-

from math import exp, log, fabs, sqrt
from random import *

class Recommender:

    INIT_MASTERY = 2
    MAX_MASTERY = 4
    MIN_MASTERY = 0

    ML_RATE = 0.7

    def __init__(self):

        # mastery = -log(P_understand)
        self.mastery = {}
        self.random = Random()
        self.article_history = []
        self.m_history = []
        self.e_history = []
        self.recommend_mastery = Recommender.INIT_MASTERY


    def article_mastery(self, article):
        for w in article.uniq_wordlist:
            if self.mastery.has_key(w):
                pass
                #self.mastery[w] = min(self.mastery[w], Recommender.MIN_MASTERY)
            else:
                self.mastery[w] = Recommender.INIT_MASTERY
        #return float(sum([self.mastery[w] for w in article.uniq_wordlist])) / sqrt(len(article.uniq_wordlist))
        return float(sum([self.mastery[w] for w in article.uniq_wordlist])) / len(article.uniq_wordlist)

    # articles:  {id : article}
    # return article
    def feed(self, articles):
        res = [[id,self.article_mastery(articles[id])] for id in articles.keys() if not id in self.article_history]
        if len(res) == 0:
            return None
        self.random.shuffle(res)
        res.sort(key=lambda x:fabs(self.recommend_mastery - x[1]))
        print self.recommend_mastery, res[0][1], [t[1] for t in res]
        return articles[res[0][0]]

    # m: -log(percentage_understand)
    def feedback(self, article, m, e):
        expected_response = self.article_mastery(article) / len(article.uniq_wordlist)
        step = (m - expected_response) * self.ML_RATE
        #step = step / len(article.uniq_wordlist)
        num_change = len([w for w in article.uniq_wordlist \
                   if self.mastery[w] > Recommender.MIN_MASTERY and self.mastery[w] < Recommender.MAX_MASTERY])
        if num_change > 0:
            step = step * len(article.uniq_wordlist) / num_change
        for w in article.uniq_wordlist:
            if self.mastery[w] > Recommender.MIN_MASTERY and self.mastery[w] < Recommender.MAX_MASTERY:
                self.mastery[w] += step
            if self.mastery[w] > Recommender.MAX_MASTERY:
                self.mastery[w] = Recommender.MAX_MASTERY
            if self.mastery[w] < Recommender.MIN_MASTERY:
                self.mastery[w] = Recommender.MIN_MASTERY

        if len(self.article_history) < 2:
            self.recommend_mastery += (e - 1) * 1.0
        elif len(self.article_history) < 6:
            self.recommend_mastery += (e - 1) * 0.3
        else:
            self.recommend_mastery += (e - 1) * 0.1
        if self.recommend_mastery > Recommender.MAX_MASTERY:
            self.recommend_mastery = Recommender.MAX_MASTERY
        if self.recommend_mastery < Recommender.MIN_MASTERY:
            self.recommend_mastery = Recommender.MIN_MASTERY

        self.article_history.append(article.id)
        self.m_history.append(m)
        self.e_history.append(e)
