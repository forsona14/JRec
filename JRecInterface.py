#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Tkinter import *
import tkFont
import re
from Article import Article
from MasteryRecommender import MasteryRecommender
from JRecRequest import JRecRequest
from JRecResponse import JRecResponse
from Knowledge import *
from Interaction import *

class JRecInterface:

    def __init__(self, fn='Text/nhk_easy.txt'):
        self.articles = JRecInterface.read_articles(fn)
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


###########################################################################################################
###################                                       #################################################
###################    JRecInterface SimpleUI Test Only   #################################################
###################                                       #################################################
###########################################################################################################



def iter(interface, textbox, res):
    interface.response(res)
    req = interface.request()
    article = interface.request().article
    textbox.delete('1.0', END)
    textbox.insert(END, req.id + "\n\n"
                   + "Best: " + str(interface.recommender.recommend_mastery) + "\n\n"
                   + "Current:" + str(interface.recommender.article_mastery(article)) + "\n\n"
                   + "Avg: " + str(interface.recommender.average_mastery) + "\n\n"
                   +  article.text.replace(' ', '\n\n'))

tk = Tk()
tk.title('SimpleUI       NHK_easy     Sona Tithew')
tk.resizable(0, 0)
textbox = Text(tk, font=tkFont.Font(size=12))
interface = JRecInterface()
req = interface.request()
article = interface.request().article
textbox.insert(END, req.id + "\n\n"
               + "Best: " + str(interface.recommender.recommend_mastery) + "\n\n"
               + "Current:" + str(interface.recommender.article_mastery(article)) + "\n\n"
               + "Avg: " + str(interface.recommender.average_mastery) + "\n\n"
               + article.text.replace(' ', '\n\n'))
textbox.grid(row=0, column=0, columnspan=5)
m = IntVar()
m.set(2)
#Radiobutton(tk, text='0%', variable=m, value=4).grid(row=1, column=0, sticky=N + S + E + W)
#Radiobutton(tk, text='25%', variable=m, value=3).grid(row=1, column=1, sticky=N + S + E + W)
#Radiobutton(tk, text='50%', variable=m, value=2).grid(row=1, column=2, sticky=N + S + E + W)
#Radiobutton(tk, text='75%', variable=m, value=1).grid(row=1, column=3, sticky=N + S + E + W)
#Radiobutton(tk, text='100%', variable=m, value=0).grid(row=1, column=4, sticky=N + S + E + W)
#e = IntVar()
#e.set(1)
# Radiobutton(tk, text='I prefer easier articles.', variable=e, value=0).grid(row=2, column=1, sticky=N + S + E + W)
# Radiobutton(tk, text='I enjoy this article!', variable=e, value=1).grid(row=2, column=2, sticky=N + S + E + W)
# Radiobutton(tk, text='I prefer harder articles.', variable=e, value=2).grid(row=2, column=3, sticky=N + S + E + W)
# Button(tk, text='Submit', height=1, width=12, font=tkFont.Font(size=24), command = lambda: self.kb_iter(textbox, m.get(), e.get())).grid(row=3, column=1, columnspan=3)
Button(tk, text='Yes', height=1, width=22, font=tkFont.Font(size=10),
       command=lambda: iter(interface, textbox, True)).grid(row=1, column=1, sticky=N + S + E + W)
Button(tk, text='No', height=1, width=22, font=tkFont.Font(size=10),
       command=lambda: iter(interface, textbox, False)).grid(row=1, column=2, sticky=N + S + E + W)
tk.mainloop()

