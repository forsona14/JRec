# This Python file uses the following encoding: utf-8
# encoding: utf-8
import MyCabocha
import CaboCha
import WordStats
from TemMatch import TemMatch


class TemParse:

    def __init__(self):
        self.tm = TemMatch()

    # returns [[words], [process_str]]
    def parse(self, str):
        if str == '':
            return [False,'']
        cabocha = CaboCha.Parser('--charset=UTF8')
        #sent = str.encode('utf-8')
        sent = str
        self.dg = MyCabocha.cabocha2depgraph(cabocha.parse(sent).toString(CaboCha.FORMAT_LATTICE))
        MyCabocha.set_head_form(self.dg)
        for node in self.dg.nodelist:
            node['deps'].sort()
        # tm.match returns [bool_match, [process_str]], the first argument of which is depreciated.
        res = self.tm.match(self.dg,len(self.dg.nodelist)-1)
        # Directly fill the first argument with wordlist in str
        res[0] = []
        for node in self.dg.nodelist:
            res[0] += [t[-3] for t in node['tag']]
        return res

    def __del__(self):
        pass
