# This Python file uses the following encoding: utf-8
# encoding: utf-8
import sys
import CaboCha

from MyCabocha import *
import TemplateStats
import WordStats

reload(sys)
sys.setdefaultencoding('utf-8')

#TemplateStats.txt2process('3');
#TemplateStats.txt2process('temp');

#LevelWeights = {"N1":50, "N2":40, "N3":20, "N4":3, "N5":1}
#max_cnt_correct = 0

#for LevelWeights['N1'] in range(100):
#    for LevelWeights['N2'] in range(100):
#        print LevelWeights['N1'],LevelWeights['N2'],
#        cnt_correct = TemplateStats.kFold_kNN("1","2",LevelWeights)
#        max_cnt_correct = max(cnt_correct, max_cnt_correct)

#print TemplateStats.kFold_kNN("1","2",LevelWeights)

#TemplateStats.lesson_stats("3")
#print
#print
#TemplateStats.lesson_stats("1c")
#print
#TemplateStats.lesson_stats("2c")
#print
#TemplateStats.lesson_stats("3c")
#print
#TemplateStats.lesson_stats("4c")
#print
#TemplateStats.lesson_stats("5c")
#WordStats.work('SJ12','N4N5test',3)
#TemplateStats.work('SJ12','N4N5test',10)

TemplateStats.book_stats("5c")


#WordStats.work_tfidf(['1c','2c','3c', '4', '5'],3)
#WordStats.work_readability(['1c','2c','3c', '4', '5'],3)

#WordStats.get_readability_features_of_text(u"私は彼に手紙を書いて送った。彼は彼女に手紙を書いて送った。")
#print WordStats.get_word_list_of_text(u"私はがれに手紙を書いて送った")

#TemplateStats.test_classify()
