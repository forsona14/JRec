#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Tkinter import *
import tkFont
import re
from Article import Article
from Recommender import Recommender
from JPEDU.WordStats import get_word_list_of_text
from JPEDU.Japanese import stoplist

class SimpleUI:

    def __init__(self, fn='Text/nhk_easy.txt'):
        self.articles = SimpleUI.read_articles(fn)
        self.all_wordlist = []
        self.all_uniq_wordlist = []
        for a in self.articles.values():
            self.all_wordlist += a.wordlist
        self.all_wordlist = sorted(self.all_wordlist)
        self.all_uniq_wordlist = list(set(self.all_wordlist))
        #zipf = {w:self.all_wordlist.count(w) for w in self.all_uniq_wordlist}
        #print sorted(zipf.values())
        #print sum([len(a.wordlist) for a in self.articles]), len(self.all_wordlist)
        self.recommender = Recommender()
        self.display_article = 0

    @staticmethod
    def read_articles(fn='Text/nhk_easy.txt'):
        f = open(fn)
        articles ={}
        line_match = re.compile(r'(k\d{14})\s{4}(.*)\n')
        for line in f:
            match = line_match.match(line)
            if match:
                news_id = match.group(1)
                text = match.group(2)
                # articles[news_id] = Article(news_id, text)
                paras = re.split(' ',text)
                for pid in xrange(len(paras)):
                    news_para_id = news_id + '_para' + str(pid + 1)
                    if len(paras[pid].strip()) > 0:
                        articles[news_para_id] = Article(news_para_id, paras[pid].strip())
                        print news_para_id, paras[pid]
        return articles

    def process(self, textbox, raw_response):
        response = 4-raw_response
        self.recommender.feedback(self.display_article, response)
        self.display_article = self.recommender.feed(self.articles)

        textbox.delete('1.0', END)
        textbox.insert(END, self.display_article.text.replace(' ', '\n\n'))
        #textbox.insert(END, self.iter_news.next().replace(' ', '\n\n'))

    def main(self):
        tk = Tk()
        tk.title('SimpleUI       NHK_easy     Sona Tithew')
        tk.resizable(0,0)
        textbox = Text(tk, font=tkFont.Font(size=12))
        self.display_article = self.recommender.feed(self.articles)
        textbox.insert(END, self.display_article.text.replace(' ', '\n\n'))
        textbox.grid(row=0, column=0, columnspan=5)
        Button(text='0%', command=lambda: self.process(textbox, 0)).grid(row=1, column=0, sticky=N + S + E + W)
        Button(text='25%', command=lambda: self.process(textbox, 1)).grid(row=1, column=1, sticky=N + S + E + W)
        Button(text='50%', command=lambda: self.process(textbox, 2)).grid(row=1, column=2, sticky=N + S + E + W)
        Button(text='75%', command=lambda: self.process(textbox, 3)).grid(row=1, column=3, sticky=N + S + E + W)
        Button(text='100%', command=lambda: self.process(textbox, 4)).grid(row=1, column=4, sticky=N + S + E + W)
        tk.mainloop()


######################################################################################################################
ui = SimpleUI()
ui.main()