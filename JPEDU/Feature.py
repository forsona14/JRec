# This Python file uses the following encoding: utf-8
# encoding: utf-8

import Utl
from TemMatch import TemMatch



class FeatureExtractor:

    def __init__(self):

        tm = TemMatch()
        self.dic = tm.template_strings()
        self.categories = tm.template_categories()

    def get_features(self,book_name):

        features = []
        file = open('Process/' + book_name + '.txt')
        lesson_id = 0
        flag = False
        for line in file:
            line = Utl.cleaned_line(line)
            if line != '\n':
                if not flag:
                    flag = True
                    lesson_id += 1
                    num_Sentences = 1.0
                    pros = [0]*len(self.dic)
                else:
                    num_Sentences += 1.0
                if line != 'NULL\n':
                    ps = Utl.split(line,'{}\n')
                    for p in ps:
                        p = '{' + p + '}'
                        pros[self.dic.index(p)] += 1
            else:
                if flag:
                    pros = [float(p)/num_Sentences for p in pros]
                    features.append(pros)
                    flag = False
        file.close()
        return features
