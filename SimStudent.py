import re
import random
from math import fabs
from Article import Article
from Recommender import Recommender
from JPEDU.WordStats import get_word_list_of_text
from JPEDU.Japanese import stoplist

class SimStudent:

    def __init__(self, fn='Text/nhk_easy.txt'):
        self.articles = SimStudent.read_articles(fn)
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

        self.random = random.Random()
        self.random.seed()
        self.mastery = {}

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
                articles[news_id] = Article(news_id, text)
            wl = get_word_list_of_text(text)
            wl = [w for w in wl if not w in stoplist]
        return articles

    def sim_mastery(self):
        self.mastery = {w: self.random.random() * 4.0 for w in self.all_uniq_wordlist}

    def article_mastery(self, article):
        for w in article.uniq_wordlist:
            if self.mastery.has_key(w):
                pass
                #self.mastery[w] = min(self.mastery[w], Recommender.MIN_MASTERY)
            else:
                self.mastery[w] = Recommender.INIT_MASTERY
        return float(sum([self.mastery[w] for w in article.uniq_wordlist])) / len(article.uniq_wordlist)

    def cal_error(self):
        err = 0.0
        for article in self.articles.values():
            expected_response = self.recommender.article_mastery(article)
            response = self.article_mastery(article)
            err += fabs(expected_response - response)
        return err / len(self.articles)

    def one_test(self):
        err = []
        while True:
            self.display_article = self.recommender.feed(self.articles)
            if self.display_article == None:
                return err
            err.append(self.cal_error())
            self.recommender.feedback(self.display_article, self.article_mastery(self.display_article))


    def mul_test(self):
        errs = []
        for i in xrange(100):
            if i%10==0:
                print 'iteration',i
            self.recommender = Recommender()
            self.sim_mastery()
            errs.append(self.one_test())
        avg_err = [sum([e[i] for e in errs if len(e) > i])/len(errs) for i in xrange(len(errs[0]))]
        print avg_err

######################################################################################################################
stu = SimStudent()
stu.mul_test()