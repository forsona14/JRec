# This Python file uses the following encoding: utf-8
# encoding: utf-8

import requests
import json
import codecs

news_root_url = 'http://www3.nhk.or.jp/news/easy/'

f = codecs.open('nhk_easy.txt','w','utf-8')

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