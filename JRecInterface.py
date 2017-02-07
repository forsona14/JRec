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

    @staticmethod
    def read_articles(fn='Text/nhk_easy.txt', if_article=True, if_para=True, if_sentence=False):
        f = open(fn)
        articles ={}
        line_match = re.compile(r'(k\d{14})\s{4}(.*)\n')
        for line in f:
            match = line_match.match(line)
            if match:
                news_id = match.group(1)
                text = match.group(2)
                if if_article:
                    articles[news_id] = Article(news_id, text)
                if not if_para:
                    continue
                paras = re.split(' ',text)
                for pid in xrange(1, len(paras)):
                    news_para_id = news_id + '_para' + str(pid)
                    if len(paras[pid].strip()) > 0:
                        articles[news_para_id] = Article(news_para_id, paras[pid].strip())
                        #print news_para_id, paras[pid]
                        if not if_sentence:
                            continue
                        sentences = re.split('。', paras[pid].strip())
                        for sid in xrange(len(sentences)):
                            news_para_sentence_id = news_para_id + '_s' + str(sid + 1)
                            if (len(sentences[sid].strip())) > 0:
                                articles[news_para_sentence_id] = Article(news_para_sentence_id, sentences[sid].strip() + '。')
                                #print news_para_sentence_id, sentences[sid].strip()
        print "Articles Read Complete."
        return articles

    #
    def request(self):
        return self.recommender.request()

    def response(self, res):
        if type(res) == bool:
            res = JRecResponse(res)
        self.recommender.response(res)

