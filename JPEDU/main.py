# This Python file uses the following encoding: utf-8
# encoding: utf-8
import sys
from TemParse import TemParse
import TemplateStats
import WordStats


reload(sys)
sys.setdefaultencoding('utf-8')


#tp = TemParse()
#r=tp.parse('この目に見えない水の輸入量によって成り立ち')
#print r[0],r[1]
#r=tp.parse('ここをよぎなくされている')
#print r[0],r[1]
#r=tp.parse('ここを余所に')
#print r[0],r[1]

TemplateStats.txt2pks('SJ12',48)
TemplateStats.txt2pks('Genki12',23)

#TemplateStats.lessons2process('temp',1,1)
#TemplateStats.process2knowledge('Genki12')