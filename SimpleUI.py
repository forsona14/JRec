#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Tkinter import *
import tkFont
import re
from Article import Article
from MasteryRecommender import MasteryRecommender
from Knowledge import *
from Interaction import *
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
        self.word_index = {self.all_uniq_wordlist[i]:i for i in xrange(len(self.all_uniq_wordlist))}
        #zipf = {w:self.all_wordlist.count(w) for w in self.all_uniq_wordlist}
        #print sorted(zipf.values())
        #print sum([len(a.wordlist) for a in self.articles]), len(self.all_wordlist)
        self.recommender = MasteryRecommender()
        self.hci = Interaction(self)
        print 'Edge Density:', self.hci.knowledge.EdgeDensity()
        self.display_article = 0

    @staticmethod
    def read_articles(fn='Text/nhk_easy.txt', if_article=True, if_para=True, if_sentence=True):
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
                for pid in xrange(len(paras)):
                    news_para_id = news_id + '_para' + str(pid + 1)
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
        return articles

    def mastery_iter(self, textbox, m, e):
        self.recommender.response(self.display_article, m, e)
        self.display_article = self.recommender.request(self.articles)

        textbox.delete('1.0', END)
        textbox.insert(END, self.display_article.text.replace(' ', '\n\n'))
        #textbox.insert(END, self.iter_news.next().replace(' ', '\n\n'))

    def kb_iter(self, textbox, m, e):
        if e > 0:
            self.hci.response(StudentResponse.UNDERSTOOD)
        else:
            self.hci.response(StudentResponse.NOT_UNDERSTOOD)
        res = self.hci.request()
        if res.process:
            self.display_article = self.articles[res.process.doc_id]
        else:
            return
        kb = self.hci.knowledge_boundary()
        print sum([kb.ProcessStatus[up.uniq_id] for up in kb.Knowledge.UniqueProcesses]),'/', len(kb.Knowledge.UniqueProcesses)
        textbox.delete('1.0', END)
        textbox.insert(END, self.display_article.text.replace(' ', '\n\n'))


    def build_graph(self):
        INTER_RATE = 0.6
        graph = [[False] * len(self.articles) for i in xrange(len(self.articles))]
        cnt = 0
        for i in xrange(len(self.articles)):
            for j in xrange(i+1, len(self.articles)):
                inter = self.articles.values()[i].inter(self.articles.values()[j])
                l1 = len(self.articles.values()[i].wordlist)
                l2 = len(self.articles.values()[j].wordlist)
                if l1 < l2 and inter >= l1 * INTER_RATE:
                    graph[i][j] = True
                    cnt += 1
                if l2 < l1 and inter >= l2 * INTER_RATE:
                    graph[j][i] = True
                    cnt += 1
        #print cnt, len(self.articles)
        return graph


    def main(self):

        #k = Knowledge(self)
        #return

        #self.build_graph()
        #return


        tk = Tk()
        tk.title('SimpleUI       NHK_easy     Sona Tithew')
        tk.resizable(0,0)
        textbox = Text(tk, font=tkFont.Font(size=12))
        self.display_article = self.recommender.request(self.articles)
        textbox.insert(END, self.display_article.text.replace(' ', '\n\n'))
        textbox.grid(row=0, column=0, columnspan=5)
        m = IntVar()
        m.set(2)
        Radiobutton(tk, text='0%', variable=m, value=4).grid(row=1, column=0, sticky=N + S + E + W)
        Radiobutton(tk, text='25%', variable=m, value=3).grid(row=1, column=1, sticky=N + S + E + W)
        Radiobutton(tk, text='50%', variable=m, value=2).grid(row=1, column=2, sticky=N + S + E + W)
        Radiobutton(tk, text='75%', variable=m, value=1).grid(row=1, column=3, sticky=N + S + E + W)
        Radiobutton(tk, text='100%', variable=m, value=0).grid(row=1, column=4, sticky=N + S + E + W)
        e = IntVar()
        e.set(1)
        #Radiobutton(tk, text='I prefer easier articles.', variable=e, value=0).grid(row=2, column=1, sticky=N + S + E + W)
        #Radiobutton(tk, text='I enjoy this article!', variable=e, value=1).grid(row=2, column=2, sticky=N + S + E + W)
        #Radiobutton(tk, text='I prefer harder articles.', variable=e, value=2).grid(row=2, column=3, sticky=N + S + E + W)
        #Button(tk, text='Submit', height=1, width=12, font=tkFont.Font(size=24), command = lambda: self.kb_iter(textbox, m.get(), e.get())).grid(row=3, column=1, columnspan=3)
        Button(tk, text='I prefer easier articles.', height=1, width=22, font=tkFont.Font(size=10),
               command=lambda: self.kb_iter(textbox, m.get(), 0)).grid(row=2, column=1, sticky=N + S + E + W)
        Button(tk, text='I enjoy this article.', height=1, width=18, font=tkFont.Font(size=10),
               command=lambda: self.kb_iter(textbox, m.get(), 1)).grid(row=2, column=2, sticky=N + S + E + W)
        Button(tk, text='I prefer harder articles.', height=1, width=22, font=tkFont.Font(size=10),
               command=lambda: self.kb_iter(textbox, m.get(), 2)).grid(row=2, column=3, sticky=N + S + E + W)
        tk.mainloop()


######################################################################################################################
ui = SimpleUI()
ui.main()