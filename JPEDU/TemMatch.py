# This Python file uses the following encoding: utf-8
# encoding: utf-8
import os
import glob
from Template import Template
import Utl

TemplateFileNames = ["N5","N4","N3","N2","N1"]

class TemMatch:
    '''
    :param
    templates
    '''

    def __init__(self):
        self.templates = []
        self.extra_templates = []
        self.category_nums = {}
        os.chdir('Template')
        #for e in glob.glob('*.txt'):
        for e in TemplateFileNames:
            cnt_e = 0
            file = open(e+".txt")
            for line in file:
                if line != '\n' and not Utl.startswith(line,'％％％％％'):
                    t = Template(line)
                    t.category = e
                    cnt_e += 1
                    if t.extra:
                        self.extra_templates.append(t)
                    else:
                        self.templates.append(t)
            self.category_nums[e] = cnt_e
            file.close()

        self.templates.sort(key=lambda x:x.num_match * 100 + x.num_restriction, reverse=True)
        os.chdir('..')
        pass # __init__

    def template_strings(self):
        return [t.str for t in self.templates if t.str != '']

    def template_categories(self):
        return [t.category for t in self.templates if t.str != '']

    def match(self,dg,node_id,bid = 0, eid = -1):
        '''
        :param node:
        :param bid:
        :param eid:
        :return: [bool_match, [process_str]]
        '''

        node = dg.nodelist[node_id]
        if eid == -1:
            eid = len(node['word']) + len(node['deps'])

        fdeps = True
        deps_process = ''
        if eid == len(node['word']) + len(node['deps']):
            for i in range(bid,len(node['deps'])):
                r = self.match(dg,node['deps'][i])
                deps_process += r[1]
                if not r[0]:
                    fdeps = False
                # just ignore dependent that can't be parsed


        for t in self.templates:
            if t.str == '{[お/ご]~になる}':
                pass
            r = t.match(dg,node_id,bid,eid)
            if not r[0]:
                continue
            if len(r)>2:        # not full match
                r1 = self.match(dg,node_id,bid,eid-r[2])
                if r1[0]:
                    return [fdeps,deps_process+r1[1]+r[1]]
                else:
                    return [False,deps_process+r1[1]+r[1]]
            else:
                return [fdeps, deps_process+r[1]]

        return [False,deps_process]

        pass

