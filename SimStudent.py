import re
import random
from math import fabs
from JRecInterface import JRecInterface
from MasteryRecommender import MasteryRecommender


class SimStudent:

    def __init__(self):
        self.interface = JRecInterface()
        self.random = random.Random()
        self.random.seed()
        self.mastery = {}

    def sim_mastery(self):
        self.mastery = {w: self.random.random() * 4.0 for w in self.interface.all_uniq_wordlist}
        for w in self.mastery.keys():
            if self.mastery[w] > 2.0:
                self.mastery[w] = 4.0
            else:
                self.mastery[w] = 0.0

    def article_mastery(self, article):
        return float(sum([self.mastery[w] for w in article.uniq_wordlist])) / len(article.uniq_wordlist)

    def cal_error(self):
        err = 0.0
        for article in self.interface.articles.values():
            expected_response = self.interface.recommender.article_mastery(article)
            actual_response = self.article_mastery(article)
            err += fabs(expected_response - actual_response)
        return err / len(self.interface.articles)

    def one_test(self):
        err = []
        while True:
            self.display_article = self.interface.request()
            if self.display_article == None:
                return err
            self.display_article = self.display_article.article
            err.append(self.cal_error())
            actual_response = self.article_mastery(self.display_article)
            if actual_response > 2:
                response = True
            else:
                response = False
            #response= actual_response
            self.interface.response(response)


    def mul_test(self):
        errs = []
        for i in xrange(10):
            if i%2==0:
                print 'iteration',i
            self.interface.recommender = MasteryRecommender(self.interface.articles)
            self.sim_mastery()
            errs.append(self.one_test())
        avg_err = [sum([e[i] for e in errs if len(e) > i])/len(errs) for i in xrange(len(errs[0]))]
        print avg_err

######################################################################################################################
stu = SimStudent()
stu.mul_test()