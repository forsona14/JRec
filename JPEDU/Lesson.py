# This Python file uses the following encoding: utf-8
# encoding: utf-8

import Utl
import Japanese

class Lesson:

    def __init__(self,lesson_id,text):
        self.lesson_id = lesson_id
        for c in Japanese.ignores:
            text = Utl.replace(text,c,'、')
        self.sentences = Utl.split(text,Japanese.delims)
        self.numSentences = len(self.sentences)
        self.processes = ['']*self.numSentences
        self.wordLists = [0]*self.numSentences
        self.node_ids = [-1]*self.numSentences

    def parse(self,tem_parser):
        for i in range(self.numSentences):
            res = tem_parser.parse(self.sentences[i])
            self.wordLists[i] = res[0]
            self.processes[i] = res[1]
