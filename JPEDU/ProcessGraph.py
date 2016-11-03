# This Python file uses the following encoding: utf-8
# encoding: utf-8

import Utl
import os
from Lesson import Lesson

class ProcessGraphNode:
    '''
	process
	example
	lesson_id
	depth
    numTemplates;
	flag
	'''

    def __init__(self,p,e,lid=Utl.maxint):
        self.process = p
        self.example = e
        self.lesson_id = lid
        self.flag = False
        self.numTemplates = len(Utl.split(p,'{}'))
        if self.numTemplates == 1:
            self.depth = 0
        else:
            self.depth = Utl.maxint

    def if_easier(self,pgn):
        if self.process == pgn.process:
            return False
        tps1 = Utl.split(self.process,'{}')
        tps2 = Utl.split(pgn.process,'{}')
        return not False in [i in tps2 for i in tps1]

    def toString(self):
        if self.example == '':
            return self.process
        else:
            return self.example + '\n' + self.process

class ProgressionEdge:
    '''
    id1
    id2
    lesson_id
    label
    '''
    def __init__(self, _1, _2, lid, l = ''):
        self.id1 = _1
        self.id2 = _2
        self.lesson_id = lid
        self.label = l



class ProcessGraph:
    '''
    nodes
    edges
    bgraph
    '''

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.graph = [[]]

    def add_node(self, process, example = '', lid = Utl.maxint):
        if process == '':
            return -1
        for i in range(len(self.nodes)):
            if self.nodes[i].process == process:
                if self.nodes[i].example == '':
                    self.nodes[i].example = example
                return i
        self.nodes.append(ProcessGraphNode(process,example,lid))
        return len(self.nodes)-1

    def add_edge(self, _1, _2, lid, l = ''):
        self.edges.append(ProgressionEdge(_1, _2, lid, l))

    def add_lesson(self, lesson):
        for i in range(lesson.numSentences):
            if lesson.processes[i] != '':
                lesson.node_ids[i] = self.add_node(lesson.processes[i],lesson.sentences[i],lesson.lesson_id)
                l = Utl.split(lesson.processes[i],'()')
                for p in l:
                    p = '(' + p + ')'
                    self.add_node(p)

        last_node = -1
        cnt = 0
        for i in range(lesson.numSentences):
            if lesson.node_ids[i] != -1 and (not lesson.node_ids[i] in lesson.node_ids[0:i]):
                if last_node != -1:
                    self.add_edge(last_node, lesson.node_ids[i], lesson.lesson_id, str(cnt))
                last_node = lesson.node_ids[i]
                cnt += 1

    def add_lessons(self, lessons, bid = 0, eid = -1):
        if eid == -1:
            eid = len(lessons)
        for i in range(bid,eid):
            self.add_lesson(lessons[i])

    def create_graph(self, dot_filename = 'unnamed'):

        nodeColor = ["white","gold", "cyan", "skyblue", "yellow", "pink", "green"]
        edgeColor = ["gray", "gold", "cyan","skyblue","yellow","pink","green"]


        os.chdir('Dot')
        file = open(dot_filename + '.dot', 'w')
        file.write('digraph\n{\noverlap=scale\nsplines=true\nsep=0.1\n\n');

        n = len(self.nodes)
        easygraph =[[self.nodes[i].if_easier(self.nodes[j]) for j in range(n)] for i in range(n)]
        graph = [[False]*n for i in range(n)]

        for i in range(n):
            for j in range(n):
                if easygraph[i][j]:
                    ff = True
                    for k in range(n):
                        if easygraph[i][k] and easygraph[k][j]:
                            ff = False
                            break
                    if ff:
                        graph[i][j] = True

        if_change = True
        while if_change:
            if_change = False
            for i in range(n):
                for j in range(n):
                    if graph[i][j] and self.nodes[i].lesson_id > self.nodes[j].lesson_id:
                        self.nodes[i].lesson_id = self.nodes[j].lesson_id
                    if graph[i][j] and \
                            (self.nodes[i].depth != Utl.maxint and \
                                 (self.nodes[j].depth == Utl.maxint or self.nodes[j].depth > self.nodes[i].depth+1)):
                        self.nodes[j].depth = self.nodes[i].depth+1
                        if_change = True


        xsep = [3,4,5,6]
        ysep = [0,5,5,5]
        rk = 0
        y = 0

        #draw nodes
        while True:
            tv = []
            for i in range(n):
                if self.nodes[i].depth == rk and self.nodes[i].lesson_id != Utl.maxint:
                    tv.append(i)
            if tv == []:
                break
            for i in range(len(tv)-1):
                for j in range(len(tv)-1, i, -1):
                    if self.nodes[tv[j]].lesson_id < self.nodes[tv[j-1]].lesson_id:
                        tv[j], tv[j-1] = tv[j-1], tv[j]
                    elif self.nodes[tv[j]].lesson_id < self.nodes[tv[j-1]].lesson_id and \
                                    self.nodes[tv[j]].numTemplates < self.nodes[tv[j-1]].numTemplates:
                        tv[j], tv[j-1] = tv[j-1], tv[j]

            x = 0
            y -= ysep[rk]
            for i in range(len(tv)):
                file.write('"'+self.nodes[tv[i]].toString()+'" [color='+nodeColor[self.nodes[tv[i]].lesson_id])
                if self.nodes[tv[i]].numTemplates == 1:
                    file.write(' pos="'+str(x)+','+str(y)+\
                               '!" shape=box fontname="times-bold" fontsize=100.0 style="bold" style="filled"];\n')
                else:
                    file.write(' pos="'+str(x)+','+str(y)+\
                               '!" fontname="times-bold" fontsize=100.0 style="bold" style="filled"];\n')
                x += xsep[rk]

            rk += 1

        for e in self.edges:
            if edgeColor[e.lesson_id] != 'white':
                if e.label == '':
                    file.write('"'+self.nodes[e.id1].toString()+'" ->"'+self.nodes[e.id2].toString()+ \
                               '" [color='+edgeColor[e.lesson_id]+' arrowhead=vee arrowsize=15 penwidth=30];\n')
                else:
                    file.write('"'+self.nodes[e.id1].toString()+'" -> "'+self.nodes[e.id2].toString()+ \
                               '" [color='+edgeColor[e.lesson_id]+' fontname="times-bold" fontsize=100 label="'+\
                               e.label+'" arrowhead=vee arrowsize=15 penwidth=30];\n')
            else:
                file.write('"'+self.nodes[e.id1].toString()+'" -> "'+self.nodes[e.id2].toString()+ \
                           '" [color='+edgeColor[e.lesson_id]+' style=invis];\n')


        #draw partial ordering edges
        for i in range(n):
            for j in range(n):
                if graph[i][j]:
                    if edgeColor[0]!="white":
                        file.write('"'+self.nodes[i].toString()+'" -> "'+self.nodes[j].toString()+\
                                   '" [color='+edgeColor[0]+' arrowhead=vee arrowsize=3 penwidth=5];\n')
                    else:
                        file.write('"'+self.nodes[i].toString()+'" -> "'+self.nodes[j].toString()+\
                                   '" [color='+edgeColor[0]+' style=invis];\n');

        file.write('}\n')
        file.close()
        os.system('dot -Kneato -Tjpg -o '+dot_filename+'.jpg '+dot_filename+'.dot')
        os.system('open /Applications/Preview.app '+dot_filename+'.jpg')
        os.chdir('..')

