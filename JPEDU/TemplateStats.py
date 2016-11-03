# This Python file uses the following encoding: utf-8
# encoding: utf-8

import os
from Lesson import Lesson
from TemParse import TemParse
from ProcessGraph import ProcessGraph
from Feature import FeatureExtractor
from TemMatch import TemMatch
import Japanese
import Utl

def kNN(fn1,fn2,num = 5):
    fe = FeatureExtractor()
    print 'Dictionary Size:',len(fe.dic)
    fs = fe.get_features(fn1)
    f = fe.get_features(fn2)
    for t in f:
        vec = Utl.get_nearestK(fs,t,num)
        su = 0.0
        for i in vec:
            if i>21:
                su += 1.0
        if su >= 0.5*num:
            s = 'N4'
        else:
            s = 'N5'
        print s

def kFold_kNN(fn1,fn2,LevelWeights, k = 3):

    fe = FeatureExtractor()
    f1 = fe.get_features(fn1)
    f2 = fe.get_features(fn2)
    f = f1 + f2
    weights = [LevelWeights[i] for i in fe.categories]
    cnt_correct = 0
    for remain in range(5):
        testflags = [False] * len(f)
        for t in range(len(f)):
            if t % 5 == remain:
                testflags[t] = True
        for t in range(len(f)):
            if testflags[t] == True:
                vec = Utl.get_weighted_nearestK_with_testflags(f,f[t],testflags,weights,k)
                print t+1, vec
                su = 0.0
                for i in vec:
                    if i>len(f1):
                        su += 1.0
                if (su >= 0.5*k) == (t + 1 > len(f1)) :
                    cnt_correct += 1
                    print 'CORRECT'

    print "Correctness: ",cnt_correct,"/",len(f),":   "
    return cnt_correct


def txt2process(book_name,lesson_count=9999):

    tp = TemParse()
    lessons = []
    file = open('Text/' + book_name + '.txt')
    lesson_id = 0
    flag = False
    for line in file:
        line = Utl.cleaned_line(line)
        if line != '\n':
            if not flag:
                flag = True
                lesson_id += 1
                text = ''
            text += line
        else:
            if flag:
                lessons.append(Lesson(lesson_id,text))
                flag = False
    file.close()

    if flag:
        lessons.append(Lesson(lesson_id,text))

    print 'Start parsing.'

    os.chdir('Process')
    file = open(book_name + '.txt', 'w')
    for lid in range(1,min(lesson_count+1, len(lessons)+1)):
        lid -= 1
        lessons[lid].parse(tp)
        for i in range(lessons[lid].numSentences):
            p = lessons[lid].processes[i]
            if p != '':
                file.write(lessons[lid].processes[i] + '\n')
            else:
                file.write('NULL\n')
        file.write('\n')
        print 'Lesson',lessons[lid].lesson_id,'end.'
    file.close()
    os.chdir('..')

    pg = ProcessGraph()
    #pg.add_lessons(Lessons,eid=2)
    #pg.create_graph(book_name)

    return lessons


# Produce process, knowledge and sentences
def txt2pks(book_name,lesson_count=9999):

    ###################################################################################
    ###################################################################################

    # Dynamic Vocabulary Dictionary (currently)
    # Maybe we can use static Vocabulary Dictionary in the future
    # Note that Grammar Templates  are static, stored in '/Template'

    wordDict = set([])

    ###################################################################################
    ###################################################################################

    tp = TemParse()
    dic = tp.tm.template_strings()
    lessons = []
    file = open('Text/' + book_name + '.txt')
    lesson_id = 0
    flag = False
    for line in file:
        # Always clean before put it into any lesson
        line = Utl.cleaned_line(line)
        if line != '\n':
            if not flag:
                flag = True
                lesson_id += 1
                text = ''
            text += line
        else:
            if flag:
                lessons.append(Lesson(lesson_id,text))
                flag = False
    file.close()

    if flag:
        lessons.append(Lesson(lesson_id,text))

    print len(lessons), ' Lessons in total.'

    # no blank line between lessons
    os.chdir('Sentence')
    file = open(book_name + '.txt', 'w')
    for lid in range(1,min(lesson_count+1, len(lessons)+1)):
        lid -= 1
        for s in lessons[lid].sentences:
            file.write(s + '\n')
    file.close()
    os.chdir('..')

    cnt = 0
    lesson_size = []
    # with blank lines between lessons
    print 'Start parsing.'
    os.chdir('Process')
    file = open(book_name + '.txt', 'w')
    for lid in range(1,min(lesson_count+1, len(lessons)+1)):
        lid -= 1
        cnt += lessons[lid].numSentences
        lesson_size.append(cnt)
        lessons[lid].parse(tp)
        for i in range(lessons[lid].numSentences):
            p = lessons[lid].processes[i]
            if p != '':
                file.write(lessons[lid].processes[i] + '\n')
            else:
                file.write('NULL\n')
            ###########################################################################
            wordDict |= set(lessons[lid].wordLists[i])
            ###########################################################################
        file.write('\n')
        print 'Lesson',lessons[lid].lesson_id,'end.'
    file.close()
    os.chdir('..')

    ###################################################################################
    wordDict = list(wordDict)
    ###################################################################################

    # no blank line between lessons
    #os.chdir('Knowledge')
    os.chdir('KnowledgeGV')    # ####################################################
    file = open(book_name + '.txt', 'w')
    write_list(file, lesson_size)
    for lid in range(1,min(lesson_count+1, len(lessons)+1)):
        lid -= 1
        for i in range(lessons[lid].numSentences):
            ps = Utl.split(lessons[lid].processes[i], '{}\n')
            graList = [dic.index('{' + p + '}') for p in ps]
            ###########################################################################
            vocList = [10000 + wordDict.index(w) for w in lessons[lid].wordLists[i]]
            ###########################################################################
            # write_list(file, graList)
            write_list(file, graList + vocList)   # ###################################
    file.close()
    os.chdir('..')

    #pg = ProcessGraph()
    #pg.add_lessons(Lessons,eid=2)
    #pg.create_graph(book_name)

    return lessons

def lessons2process(book_name,begin_id=1,end_id = -1):

    tp = TemParse()
    lessons = []
    file = open('Text/' + book_name + '.txt')
    lesson_id = 0
    flag = False
    for line in file:
        line = Utl.cleaned_line(line)
        if line != '\n':
            if not flag:
                flag = True
                lesson_id += 1
                text = ''
            text += line
        else:
            if flag:
                lessons.append(Lesson(lesson_id,text))
                flag = False
    file.close()

    if flag:
        lessons.append(Lesson(lesson_id,text))

    if end_id == -1:
        end_id = begin_id

    for lid in range(begin_id,end_id+1):
        print 'Lesson',lid,':'
        lid -= 1
        lessons[lid].parse(tp)
        for i in range(lessons[lid].numSentences):
            print lessons[lid].sentences[i],lessons[lid].processes[i]
        print 'Lesson',lessons[lid].lesson_id,'end.'
        print

    pg = ProcessGraph()
    #pg.add_lessons(Lessons,eid=2)
    #pg.create_graph(book_name)

    return lessons


def write_list(f, l):
    if len(l) == 0:
        f.write('\n')
        return
    for i in range(len(l)-1):
        f.write(str(l[i]) + ' ')
    f.write(str(l[-1]) + '\n')


def process2knowledge(book_name):
    tm = TemMatch()
    dic = tm.template_strings()
    file = open('Process/' + book_name + '.txt')
    knowledge = []
    lesson_size = []
    flag = False
    for line in file:
        if line != '\n':
            if not flag:
                flag = True
            if line != 'NULL\n':
                ps = Utl.split(line,'{}\n')
                knowledge.append([dic.index('{' + p + '}') for p in ps])
            else:
                knowledge.append([])
        else:
            if flag:
                flag = False
                lesson_size.append(len(knowledge))
    file.close()
    if flag:
        lesson_size.append(len(knowledge))

    file = open('Knowledge/' + book_name + '.txt', 'w')
    write_list(file, lesson_size)
    for l in knowledge:
        write_list(file, l)


def book_stats(book_name):
    tm = TemMatch()
    dic = tm.template_strings()
    category = tm.template_categories()
    count = {"N1":0,"N2":0,"N3":0,"N4":0,"N5":0}
    file = open('Process/' + book_name + '.txt')
    numSentence = 0
    for line in file:
        if line != '\n':
            if line != 'NULL\n':
                numSentence += 1
                ps = Utl.split(line,'{}\n')
                for p in ps:
                    p = '{' + p + '}'
                    if p == '{~[うが/うと]}':
                        continue
                    count[category[dic.index(p)]] += 1
                    if category[dic.index(p)] == 'N2':
                        print p
    allnum = count['N1'] + count['N2'] + count['N3'] + count['N4'] + count['N5']
    count['N1'] = round(100.0 * count['N1'] / numSentence, 3)
    count['N2'] = round(100.0 * count['N2'] / numSentence, 3)
    count['N3'] = round(100.0 * count['N3'] / numSentence, 3)
    count['N4'] = round(100.0 * count['N4'] / numSentence, 3)
    count['N5'] = round(100.0 * count['N5'] / numSentence, 3)
    print numSentence


def lesson_stats(book_name):

    STANDARD_N1 = {'N1': 1.033, 'N2': 2.385, 'N3': 4.511, 'N4': 16.464, 'N5': 75.608}


    STANDARD_N2 = {'N1': 0.754, 'N2': 1.823, 'N3': 4.294, 'N4': 15.846, 'N5': 77.283}

    tm = TemMatch()
    dic = tm.template_strings()
    category = tm.template_categories()
    count = {"N1":0,"N2":0,"N3":0,"N4":0,"N5":0}
    numSentence = 0;
    file = open('Process/' + book_name + '.txt')
    flag = False
    cnt1 = 0
    cnt2 = 0
    features = []
    for line in file:
        line = Utl.cleaned_line(line)
        if line != '\n':
            if not flag:
                count = {"N1":0,"N2":0,"N3":0,"N4":0,"N5":0}
                cnt =[0]*len(dic)
                numSentence = 0
                flag = True
            if line!= 'NULL\n':
                numSentence += 1
                ps = Utl.split(line,'{}\n')
                for p in ps:
                    p = '{' + p + '}'
                    #if p == '{~[うが/うと]}':
                    #   continue
                    cnt[dic.index(p)] += 1
                    #count[category[dic.index(p)]] += 1
        else:
            if flag:
                flag = False
                for i in range(len(dic)):
                    #if cnt[i]>1 and category[i]=='N3':
                    #    print dic[i], cnt[i]
                    if cnt[i] > 0:
                        count[category[i]] += cnt[i]#min(cnt[i],2)#cnt[i]
                allnum = count['N1'] + count['N2'] + count['N3'] + count['N4'] + count['N5']
                #count['N1'] = '' + str(round(100.0 * count['N1'] / allnum, 3)) + '%'
                #count['N2'] = '' + str(round(100.0 * count['N2'] / allnum, 3)) + '%'
                #count['N3'] = '' + str(round(100.0 * count['N3'] / allnum, 3)) + '%'
                #count['N4'] = '' + str(round(100.0 * count['N4'] / allnum, 3)) + '%'
                #count['N5'] = '' + str(round(100.0 * count['N5'] / allnum, 3)) + '%'

                count['N1'] = round(100.0 * count['N1'] / numSentence, 3)
                count['N2'] = round(100.0 * count['N2'] / numSentence, 3)
                count['N3'] = round(100.0 * count['N3'] / numSentence, 3)
                count['N4'] = round(100.0 * count['N4'] / numSentence, 3)
                count['N5'] = round(100.0 * count['N5'] / numSentence, 3)

                #print count
                #print count['N1'], count['N2']
                #print count['N1'] + count['N2'], count['N3']
                #print count['N1'] + count['N2'] + count['N3'], count['N4']
                #print count['N1'] + count['N2'] + count['N3']+ count['N4'], count['N5']

                features.append(count.values())

    #print cnt1,cnt2
    file.close()
    return features

def test_classify():
    cnt_err = 0
    cnt = 0
    for lvl in range(1,6):
        features = lesson_stats(str(lvl)+"c")
        cnt += len(features)
        for feature in features:
            lvl1 = classify_level(feature)
            #print "N"+str(lvl)+"->N"+str(lvl1)
            print feature[0],feature[1],feature[2],feature[3],feature[4]
            if lvl != lvl1:
                cnt_err += 1
        print
    print cnt_err, cnt, float(cnt-cnt_err) / cnt * 100, "%"

def classify_level(feature):
    for lvl in range(5, 1, -1):
        if (within_level(feature, lvl)):
            return lvl
    return 1



# classify feature vector into `within N_lvl' or 'beyond N_lvl'
# feature: [N1, N2, N3, N4, N5], lvl = 2,3,4,5
def within_level(feature, lvl):
    p = [
        [6.0, 16.3],        # N1/N2
        [11.2, 19.0],       # N2/N3
        [17.0, 98.0],       # N3/N4
        [33.0, 780.0]       # N4/N5
    ]
    if len(feature) != 5 or lvl > 5 or lvl<2:
        print 'beyond_level input error!'
        return False
    f1 = sum(feature[0:lvl-1])           # over the Knowledge Boundary
    f2 = feature[lvl - 1]                   # on   the Knowledge Boundary
    return f1 / p[lvl-2][0] + f2 / p[lvl-2][1] - 1 < 0      # x/a + y/b = 1

