# This Python file uses the following encoding: utf-8
# encoding: utf-8

import requests
import json
import codecs
import re
from Article import Article

def read_text_from_web():

    news_root_url = 'http://www3.nhk.or.jp/news/easy/'

    f = codecs.open('Text/nhk_easy.txt','w','utf-8')

    news_list_url = news_root_url + 'news-list.json'
    news_list_json = requests.get(news_list_url).text
    #print news_list_json
    all_list = json.loads(news_list_json)[0]
    all_dates = sorted(all_list.keys())
    for date in all_dates:
        date_list = all_list[date]
        for news in date_list:
            news_id = news["news_id"]
            title = news["title"]
            try:
                text = json.loads(requests.get(news_root_url + news_id + '/' + news_id + '.out.json').text)["text"]
            except:
                f.write(news_id + u'    ERROR\n')
                print news_id, 'error'
            else:
                text.replace('\n',' ')
                f.write(news_id + u'    ' + text + '\n')
                print news_id, 'OK'
    f.close()


def convert_text_to_articles(fn='Text/nhk_easy.txt', if_article=True, if_para=True, if_sentence=False):

    old_articles = read_articles()

    f = open(fn)
    articles = {}
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
            paras = re.split(' ', text)
            for pid in xrange(1, len(paras)):
                news_para_id = news_id + '_para' + str(pid)
                if len(paras[pid].strip()) > 0:
                    articles[news_para_id] = Article(news_para_id, paras[pid].strip())
                    # print news_para_id, paras[pid]
                    if not if_sentence:
                        continue
                    sentences = re.split('。', paras[pid].strip())
                    for sid in xrange(len(sentences)):
                        news_para_sentence_id = news_para_id + '_s' + str(sid + 1)
                        if (len(sentences[sid].strip())) > 0:
                            articles[news_para_sentence_id] = Article(news_para_sentence_id,
                                                                      sentences[sid].strip() + '。')
                            # print news_para_sentence_id, sentences[sid].strip()

    ##############################################
    # Keep old_articles, combine them into new one
    for doc_id in old_articles.keys():
        if not articles.has_key(doc_id):
            articles[doc_id] = old_articles[doc_id]
    ##############################################

    f = codecs.open('Text/nhk_easy_articles.txt','w','utf-8')

    for article in articles.values():
        f.write(json.dumps(article.__dict__)+'\n')
    f.close()

def read_articles():
    try:
        f = open('Text/nhk_easy_articles.txt')
    except:
        return {}
    article_list = []
    for line in f:
        article_list.append(json.loads(line[:-1], object_hook=
                        lambda s:Article(s["doc_id"], s["text"], s["wordlist"], s["uniq_wordlist"])))
    articles = {a.doc_id:a for a in article_list}
    return articles

####################################################################################################################

#read_text_from_web()
convert_text_to_articles()


#
articles = read_articles()
