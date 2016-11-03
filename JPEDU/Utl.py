# This Python file uses the following encoding: utf-8
# encoding: utf-8

from jTransliterate import JapaneseTransliterator
import CaboCha
import MyCabocha
import math
import Japanese

maxint = 9999

omit_lines = [  '１９９１','１９９２','１９９３','１９９４','１９９５',
                '１９９６','１９９７','１９９８','１９９９','２０００',
                '２００１', '２００２', '２００３', '２００４', '２００５',
                '２００６', '２００７', '２００８', '２００９．７', '２００９．１２',
                '２０１０．７','２０１０．１２','２０１１．７','２０１１．１２',
                '２０１２．７','２０１２．１２','２０１３．７','２０１３．１２']

def transKH(s):
    return JapaneseTransliterator(s).transliterate_from_kana_to_hira()

def hirakana(s):
    cabocha = CaboCha.Parser('--charset=UTF8')
    #sent = str.encode('utf-8')
    sent = s
    dg = MyCabocha.cabocha2depgraph(cabocha.parse(sent).toString(CaboCha.FORMAT_LATTICE))
    p = ''
    for node in dg.nodelist:
        for tag in node['tag']:
            p += tag[-2]
    return p

def split(s,delims):
    s = s.decode('utf-8')
    l = []
    i = 0
    while i < len(s) and s[i] in delims.decode('utf-8'):
        i += 1
    while i<len(s):
        j = i
        while j < len(s) and (not s[j] in delims.decode('utf-8')):
            j += 1
        if j != i:            #no null string
            l.append(s[i:j].encode('utf-8'))
        i = j
        while i < len(s) and s[i] in delims.decode('utf-8'):
            i += 1
    return l

def find(s,sub):
    return s.decode('utf-8').find(sub.decode('utf-8'))

def replace(s, ori, src):
    return s.decode('utf-8').replace(ori.decode('utf-8'),src.decode('utf-8')).encode('utf-8')

def startswith(s,s0):
    return s.decode('utf-8').startswith(s0.decode('utf-8'))

def endswith(s,s0):
    return s.decode('utf-8').endswith(s0.decode('utf-8'))

def multi_in(l,list):
    for i in l:
        if i in list:
            return True
    return False

def cleaned_line(line):
    line = line[:-1]
    if line in omit_lines:
        return '\n'
    for c in Japanese.ignores:
        line = replace(line,c,'')
    line = line + '\n'
    return line


def cosine(a,b):
    if len(a)!=len(b):
        print 'WRONG LENGTH in COSINE(a,b)'
        return -maxint
    s = 0
    sa = 0
    sb = 0
    for i in range(len(a)):
        s += a[i]*b[i]
        sa += a[i]*a[i]
        sb += b[i]*b[i]
    if s<0:
        s = 0 - s
    return s / math.sqrt(sa) / math.sqrt(sb)

def weighted_cosine(a,b,weights):
    if len(a)!=len(b):
        print 'WRONG LENGTH in COSINE(a,b)'
        return -maxint
    s = 0
    sa = 0
    sb = 0
    for i in range(len(a)):
        s += a[i]*b[i]*weights[i]
        sa += a[i]*a[i]*weights[i]
        sb += b[i]*b[i]*weights[i]
    if s<0:
        s = 0 - s
    return s / math.sqrt(sa) / math.sqrt(sb)

def get_nearestK(fs,f,k = 3):
    mp = [[i,cosine(fs[i],f)] for i in range(len(fs))]
    mp.sort(key=lambda x:x[1],reverse = True)
    mp = [t[0]+1 for t in mp]
    return mp[:k]

def get_nearestK_with_testflags(fs,f,testflags,k = 3):
    mp = [[i,cosine(fs[i],f)] for i in range(len(fs)) if testflags[i] == False]
    mp.sort(key=lambda x:x[1],reverse = True)
    mp = [t[0]+1 for t in mp]
    return mp[:k]

def get_weighted_nearestK_with_testflags(fs,f,testflags,weights,k = 3):
    mp = [[i,weighted_cosine(fs[i],f,weights)] for i in range(len(fs)) if testflags[i] == False]
    mp.sort(key=lambda x:x[1],reverse = True)
    mp = [t[0]+1 for t in mp]
    return mp[:k]

def get_dg_depth(dg):
    r = dg.root['address']
    return _get_depth(dg, r)

def _get_depth(dg, n):
    if len(dg.nodelist[n]['deps']) == 0:
        return 1
    return 1 + max([_get_depth(dg,m) for m in dg.nodelist[n]['deps']])