import Knowledge
import random


def eva(k2, seq):
    k2.squared_error(seq, lambda x:x, lambda x:x)


def ProcessConceptPerSentence(bookname):
    k = Knowledge.Knowledge(bookname, False)
    print 'Edge Density in Partial Ordering Graph: ', k.EdgeDensity()
    seq = range(k.num())
    k.ProcessConceptPerSentence(seq)


def print_all(book_name, char=False):
    print '****************************************************************'
    print
    print book_name
    print

    k = Knowledge.Knowledge(book_name, char)

    print float(len(k.UniqueProcesses)) / k.num(), float(len(k.UniqueConcepts)) / k.num()

    seq = range(k.num())
    _textbook = k.progress(seq)
    random.shuffle(seq)
    _random = k.progress(seq)
    seq = k.bfs()
    _topsort = k.progress(seq)
    seq = k.greedy1_gradual()
    _gradual = k.progress(seq)

    for i in range(len(_textbook)):
        print _textbook[i][1], _textbook[i][2], _random[i][1], _random[i][2], \
            _topsort[i][1], _topsort[i][2], _gradual[i][1], _gradual[i][2]

    print

#ProcessConceptPerSentence('SJ12')
#ProcessConceptPerSentence('Genki12')
#print_all('SJ12', False)
#print_all('Genki12', False)

#k = Knowledge.Knowledge('Genki12')
#seq = range(k.num())
#status = k.proportion(seq)
#print len(status)
#i = 0
#while i<len(status):
#    x = 0
#    y = 0
#    z = 0
#    p = i
#    for j in range(4):
#        if i < len(status):
#            x += status[i][0]
#            y += status[i][1]
#            z += status[i][2]
#            i += 1
#        else:
#            break

#    print x/(i-p), y/(i-p), z/(i-p)

k = Knowledge.Knowledge('test',True)
print k.num()
#RI
#seq = k.greedys(10,[0.3, 0.7, 0.2])
#NK
#seq = k.greedys(10,[1.8, 0.2, 0.5])
#RC
#seq = k.greedys(10,[1.2, 0.2, 0.3])
seq = k.greedys(10,[0.465, 0.581, 0.214])
print seq
for i in seq:
    print k.data[i].sentence
print k.proportion_pace(seq)