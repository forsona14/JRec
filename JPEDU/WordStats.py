# This Python file uses the following encoding: utf-8
# encoding: utf-8

import MyCabocha
import CaboCha
import Utl
import Japanese
import random
import math
from math import log10

def work_readability(fns, k = 3):

    STOP = True
    bows = []

    nW = []                 # Number of words in a text
    nS = []                 # Number of sentences in a text
    nWpS = []               # Avg. number of words per sentence
    depths = []             # Avg. parse tree depth
    nNPpS = []              # Avg. number of noun phrases per sentence
    nVPpS = []              # Avg. number of verb phrases per sentence
    nPRONpS = []            # Avg. number of pronouns per sentence
    nCLAUSEpS = []          # Avg. number of clauses per sentence
    cosSim = []             # Avg. cosine similarity between adjacent sentences
    woAll = []              # Avg. word overlap between adjacent sentences
    woNPron = []            # Avg. word overlap (Noun and Pronoun only)
    likelihood =[]          # Artical Likelyhood

    for fn in fns:
        file = open('Text/' + fn + '.txt')
        flag = False
        bows1 = []
        for line in file:
            line = Utl.cleaned_line(line)
            if line != '\n':
                if not flag:
                    flag = True
                    text = ''
                text += line
            else:
                if flag:
                    bows1.append(get_word_list_of_text(text))
                    features = get_readability_features_of_text(text)
                    nW.append(features[0])
                    nS.append(features[1])
                    nWpS.append(features[2])
                    depths.append(features[3])
                    nNPpS.append(features[4])
                    nVPpS.append(features[5])
                    nPRONpS.append(features[6])
                    nCLAUSEpS.append(features[7])
                    cosSim.append(features[8])
                    woAll.append(features[9])
                    woNPron.append(features[10])
                    flag = False
        file.close()

        if flag:
            bows1.append(get_word_list_of_text(text))
            features = get_readability_features_of_text(text)
            nW.append(features[0])
            nS.append(features[1])
            nWpS.append(features[2])
            depths.append(features[3])
            nNPpS.append(features[4])
            nVPpS.append(features[5])
            nPRONpS.append(features[6])
            nCLAUSEpS.append(features[7])
            cosSim.append(features[8])
            woAll.append(features[9])
            woNPron.append(features[10])
        bows.append(bows1)

    dict = []
    for bows1 in bows:
        for v in bows1:
            dict += v

    print 'Dictionary Size:',len(set(dict))

    pw = {w:log10(float(dict.count(w))/len(dict)) for w in dict}

    ans = []
    for j in range(len(bows)):
        bows1 = bows[j]
        for vec in bows1:
            likelihood.append(0)
            for w in vec:
                likelihood[-1] += pw[w]
            ans.append(j)

    v = []
    for i in range(len(nW)):
        v.append([nW[i], nS[i], nWpS[i], depths[i], nNPpS[i], nVPpS[i], nPRONpS[i], nCLAUSEpS[i], cosSim[i], woAll[i], woNPron[i], likelihood[i]])
    # weight of parse tree depth

    file = open('Text/_stats_.txt','w')
    file.write(str(range(len(v[0])))+", Level\n")
    for i in range(len(v)):
        file.write(str(v[i])+", N"+str(ans[i]+1)+"\n")
    return


    total_correct = 0
    for t in range(30):
        cnt_correct = 0
        sd = [i%5 for i in range(len(v))]
        random.shuffle(sd)

        for remain in range(5):
            for i in range(len(v)):
                if sd[i] == remain:
                    testflags[i] = True
                else:
                    testflags[i] = False
            for i in range(len(v)):
                if testflags[i]:
                    vec = Utl.get_weighted_nearestK_with_testflags(v,v[i],testflags,idf,k)
                    #print i+1, vec
                    su = 0.0
                    for j in vec:
                        if ans[j-1] == ans[i]:
                            su += 1.0
                    if su >= 0.5*k:
                        cnt_correct += 1
        print cnt_correct,'/',len(v)
        total_correct += cnt_correct
    print total_correct/30.0/len(v)

# readability
###################################################################################################
# tfidf

def work_tfidf(fns, k = 3):

    STOP = True
    bows = []
    depths = []

    for fn in fns:
        file = open('Text/' + fn + '.txt')
        flag = False
        bows1 = []
        for line in file:
            line = Utl.cleaned_line(line)
            if line != '\n':
                if not flag:
                    flag = True
                    text = ''
                text += line
            else:
                if flag:
                    bows1.append(get_word_list_of_text(text))
                    depths.append(get_depth_of_text(text))
                    flag = False
        file.close()

        if flag:
            bows1.append(get_word_list_of_text(text))
            depths.append(get_depth_of_text(text))
        bows.append(bows1)

#    print sum([float(sum([len(b) for b in bows1]))/len(bows1) for bows1 in bows]) / 5
#    print [float(sum([len(b) for b in bows1]))/len(bows1) for bows1 in bows]
#    return

    dict = []
    for bows1 in bows:
        for v in bows1:
            dict += v

    dict = list(set(dict))

    if STOP:
        d = dict
        dict = []
        for w in d:
            if not (w in Japanese.stoplist):
                dict.append(w)

    dict.sort()

    print 'Dictionary Size:',len(dict)

    dict = {dict[i]:i for i in range(len(dict))}

    v = []
    ans = []

    for j in range(len(bows)):
        bows1 = bows[j]
        vec1 = []
        for i in range(len(bows1)):
            vec1.append([0]*len(dict))
            for w in bows1[i]:
                if w in dict:
                    vec1[-1][dict[w]] += 1
        for vec in vec1:
            v.append(vec)
            ans.append(j)

    testflags = [False]*(len(v))
    idf = [1.0]*len(dict)
    for i in range(len(dict)):
        for j in range(len(v)):
            if v[j][i]>0:
                idf[i] += 1.0
        idf[i] /= (len(dict)+1.0)
        #idf[i] = math.log((len(dict)+1.0)/idf[i])
        idf[i] *= idf[i]# * idf[i]


    # parse tree depth
    for i in range(len(v)):
        v[i].append(depths[i])
    # weight of parse tree depth
    idf.append(1)

    file = open('Text/_stats_.txt','w')
    file.write(str(range(len(v[0])))+", Level\n")
    for i in range(len(v)):
        file.write(str(v[i])+", N"+str(ans[i]+1)+"\n")
    return


    total_correct = 0
    for t in range(30):
        cnt_correct = 0
        sd = [i%5 for i in range(len(v))]
        random.shuffle(sd)

        for remain in range(5):
            for i in range(len(v)):
                if sd[i] == remain:
                    testflags[i] = True
                else:
                    testflags[i] = False
            for i in range(len(v)):
                if testflags[i]:
                    vec = Utl.get_weighted_nearestK_with_testflags(v,v[i],testflags,idf,k)
                    #print i+1, vec
                    su = 0.0
                    for j in vec:
                        if ans[j-1] == ans[i]:
                            su += 1.0
                    if su >= 0.5*k:
                        cnt_correct += 1
        print cnt_correct,'/',len(v)
        total_correct += cnt_correct
    print total_correct/30.0/len(v)

# tfidf
###################################################################################################


def get_depth_of_text(text):
    for c in Japanese.ignores:
        text = Utl.replace(text,c,'')
    l = Utl.split(text,Japanese.delims)
    d = 0
    for s in l:
        d += get_depth(s)
    return float(d) / len(l)

def get_word_list_of_text(text):
    for c in Japanese.ignores:
        text = Utl.replace(text,c,'')
    wl = []
    for s in Utl.split(text,Japanese.delims):
        wl += get_word_list(s)
    return wl

def get_word_list(str):
    cabocha = CaboCha.Parser('--charset=UTF8')
    #sent = str.encode('utf-8')
    sent = str
    dg = MyCabocha.cabocha2depgraph(cabocha.parse(sent).toString(CaboCha.FORMAT_LATTICE))
    wl = []
    for node in dg.nodelist:
        wl += [t[-3] for t in node['tag']]
    return wl

def get_depth(str):
    cabocha = CaboCha.Parser('--charset=UTF8')
    #sent = str.encode('utf-8')
    sent = str
    dg = MyCabocha.cabocha2depgraph(cabocha.parse(sent).toString(CaboCha.FORMAT_LATTICE))
    return Utl.get_dg_depth(dg)

def get_word_list_with_pos(str):
    cabocha = CaboCha.Parser('--charset=UTF8')
    sent = str
    dg = MyCabocha.cabocha2depgraph(cabocha.parse(sent).toString(CaboCha.FORMAT_LATTICE))
    wl = []
    pos = []
    for node in dg.nodelist:
        wl += [t[-3] for t in node['tag']]
        pos += [t[0] + t[1] for t in node['tag']]
    return [wl, pos]

# [#word, depth, #noun, #verb, #pron, #clause]
def get_readability_features(str):
    cabocha = CaboCha.Parser('--charset=UTF8')
    str = Utl.split(str, Japanese.delims)[0]
    sent = str
    dg = MyCabocha.cabocha2depgraph(cabocha.parse(sent).toString(CaboCha.FORMAT_LATTICE))
    [wl, pos] = get_word_list_with_pos(str)
    nN = 0
    nV = 0
    nPron = 0
    for p in pos:
        if Utl.startswith(p, u"動詞"):
            nV += 1
        elif Utl.startswith(p, u"名詞代名詞"):
            nPron += 1
        elif Utl.startswith(p, u"名詞"):
            nN += 1
    return [len(wl), Utl.get_dg_depth(dg), nN, nV, nPron, len(dg.nodelist)]

#
def get_readability_features_of_adjacent(str1, str2):
    [wl1, pos1] = get_word_list_with_pos(str1)
    [wl2, pos2] = get_word_list_with_pos(str2)

    nl1 = []         # noun and pronoun list
    nl2 = []
    for i in range(len(wl1)):
        if Utl.startswith(pos1[i], u"名詞"):
            nl1.append(wl1[i])
    for i in range(len(wl2)):
        if Utl.startswith(pos2[i], u"名詞"):
            nl2.append(wl2[i])

    wl1.sort()
    wl2.sort()
    nl1.sort()
    nl2.sort()

    cosine_sim = 0.0
    overlap_word = 0
    l1 = 0
    l2 = 0
    for s in (set(wl1)):
        c1 = wl1.count(s)
        c2 = wl2.count(s)
        cosine_sim += c1 * c2
        l1 += c1 * c1
        overlap_word += min(c1, c2)
    for s in (set(wl2)):
        c2 = wl2.count(s)
        l2 += c2 * c2
    if l1 * l2 != 0:
        cosine_sim /= math.sqrt(l1 * l2)
    else:
        cosine_sim = 0.0

    overlap_noun_word = 0
    for s in (set(nl1)):
        c1 = nl1.count(s)
        c2 = nl2.count(s)
        overlap_noun_word += min(c1, c2)

    return [cosine_sim, overlap_word, overlap_noun_word]


def get_readability_features_of_text(text):
    nW = 0
    depth = 0
    nN = 0
    nV = 0
    nPron = 0
    nClause = 0
    sim = 0
    nOWpS = 0
    nONpS = 0
    lastText = "LAST_NULL"
    for c in Japanese.ignores:
        text = Utl.replace(text, c, '')
    l = Utl.split(text,Japanese.delims)
    for s in l:
        features = get_readability_features(s)
        nW += features[0]
        depth += features[1]
        nN += features[2]
        nV += features[3]
        nPron += features[4]
        nClause += features[5]
        if lastText != "LAST_NULL":
            adj_features = get_readability_features_of_adjacent(s, lastText)
            sim += adj_features[0]
            nOWpS += adj_features[1]
            nONpS += adj_features[2]
        lastText = s
    if len(l) == 1:
        sim = 0
        nONpS = 0
        nOWpS = 0
    else:
        sim = float(sim) / (len(l) - 1)
        nOWpS = float(nOWpS) / (len(l) - 1)
        nONpS = float(nONpS) / (len(l) - 1)

    return [nW, len(l), float(nW) / len(l), float(depth) / len(l), float(nN) / len(l),
            float(nV) / len(l), float(nPron) / len(l), float(nClause) / len(l),
            sim, nOWpS, nONpS, ]