# This Python file uses the following encoding: utf-8
# encoding: utf-8

import Utl
import Japanese

class Component:

    # might need to change num_match and num_restriction to max / min
    def __init__(self, s):

        self.category = ""

        if Utl.startswith(s,'＃'):
            self.type = 'MULTI'
            self.lst = [Component(s0) for s0 in Japanese.synonyms[s]]
            self.num_match = min([c.num_match for c in self.lst])
            self.num_restriction = min([c.num_restriction for c in self.lst])
            self.str = Utl.replace(s,'＃','')

        elif Utl.find(s,'／')>=0:
            self.type = 'MULTI'
            self.lst = [Component(s0) for s0 in Utl.split(s,'／')]
            self.num_match = min([c.num_match for c in self.lst])
            self.num_restriction = min([c.num_restriction for c in self.lst])
            self.str = '['+'/'.join([c.str for c in self.lst])+']'

        elif Utl.find(s,'ー')>=0:
            self.type = 'SUCCESSIVE'
            self.lst = [Component(s0) for s0 in Utl.split(s,'ー')]
            self.num_match = sum([c.num_match for c in self.lst])
            self.num_restriction = sum([c.num_restriction for c in self.lst])
            self.str = ''.join([c.str for c in self.lst])

        else:
            self.type = 'SINGLE'
            self.str = s
            self.num_restriction = 1

            if self.str != '〜':
                self.num_match = 1
            else:
                self.num_match = 0

            if Utl.startswith(self.str,'＃'):
                return

            if Utl.startswith(self.str,'＠'):
                self.str = '〜' + self.str

            if Utl.find(self.str,'＊') >= 0:
                #  ある＊　ー＞　　あり
                self.str = Utl.replace(self.str,'＊','')
                self.morph = True
            else:
                self.morph = False

            if Utl.find(self.str,'＠') >=0:
                #　ご＃接頭詞　〜　！ー＞　５分
                l = Utl.split(self.str,'＠')
                self.str = l[0]
                self.tag = l[1]
                self.num_restriction = 3
            else:
                self.tag = ''

class Template:

    def __init__(self,s):

        if Utl.find(s,'％')>=0:
            l = Utl.split(s,'％\n')
            s = l[0]
            self.str = '{'+l[1]+'}'
        else:
            self.str = ''


        self.components = [Component(s0) for s0 in Utl.split(s,'　\n')]

        if len(self.components)>1 and self.components[1].str=='たい':
            pass

        if self.components[0].str == '＾':
            self.extra = True
            del self.components[0]
        else:
            self.extra = False

        if self.components[-1].str == '＄':
            self.display = False
            del self.components[-1]
        else:
            self.display = True

        self.num_match = 0
        self.num_restriction = 0
        for c in self.components:
            self.num_match += c.num_match
            self.num_restriction += c.num_restriction


        if self.components[0].str == '〜' and self.num_match >= len(self.components)-1 and self.num_match>0:
            self.ed = True
        else:
            self.ed = False

        if self.str == '':
            self.str = self.toString()


    def toString(self):
        if not self.display:
            return ''
        s = ''
        for c in self.components:
            # no space
            if True or s == '' or not (Utl.endswith(s,'〜') or Utl.startswith(c.str,'〜')):
                s += c.str
            else:
                s += ' '+c.str
        return '{' + Utl.replace(s,'〜','~') + '}'



    def match(self,dg,node_id,sid = 0, eid = -1):
        '''
        :return:    [bool_ifMatch, [str_process, [number of items matched]]]
        '''

        node = dg.nodelist[node_id]

        if self.components[0] == '〜を':
            pass


        if eid == -1:
            eid = len(node['deps'])+len(node['word'])

        id = eid - 1


        if self.ed and self.components[0].tag == '':
            tt = 0
        else:
            tt = -1

        ff = True
        i = len(self.components)-1
        while i>tt and id >= sid:
            r = self.match_component(dg,node,id,self.components[i])
            if id >= len(node['deps']):
                if r == 0 and not(Template.if_complement(node,id-len(node['deps']))):
                    ff = False
                    break
            else:
                if r == 0 and not(Template.if_complement(dg.nodelist[node['deps'][id]],-1)):
                    ff = False
                    break
            if r > 0:
                id -= r
            else:
                id -= 1
            if r > 0:
                i -= 1

        if i > tt:
            ff = False

        if self.ed and id < 0 and self.components[0].tag == '':
            ff = False

        if ff:
            if self.ed:
                if self.components[0].tag == '':
                    if Template.num_of_non_complement(dg,node_id,0,id+1) <= 0:
                        return [True,self.str]
                    else:
                        return [True,self.str, eid-id-1]
                else:
                    if Template.num_of_non_complement(dg,node_id,0,id+2) <= 0:
                        return [True,self.str]
                    else:
                        return [True,self.str, eid-id-2]
            else:
                if Template.num_of_non_complement(dg,node_id,0,id+1) == 0:
                    return [True,self.str]


        return [False]
        pass

    def match_component(self, dg, node, id, c):
        '''

        :param dg:
        :param node:
        :param id:
        :param c:
        :return:    number of words/dependents matched
        '''
        #no sid yet
        if c.type == 'SINGLE':
            if id >= len(node['deps']):
                _node, _id = node,id-len(node['deps'])
            else:
                _node, _id = dg.nodelist[node['deps'][id]],-1
            if Template.match_word(dg, _node, _id, c.str, c.morph, c.tag):
                return 1
            else:
                return 0
        elif c.type == 'SUCCESSIVE':
            total_num_match = 0
            for i in range(len(c.lst)):
                if id<i:
                    return 0
                num_match = self.match_component(dg,node,id-i,c.lst[-1-i])
                if num_match < 1:
                    return 0
                else:
                    total_num_match += num_match
            return total_num_match
        elif c.type == 'MULTI':
            for c0 in c.lst:
                num_match = self.match_component(dg,node,id,c0)
                if num_match > 0:
                    return num_match
            return 0


    @staticmethod
    def match_word(dg, node, id, tem_str, morph, tag):
        '''
        :param id: if id == -1 match entire node, else match node['word'][id]
        :return:
        '''

        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

        # match entire node
        if id == -1:
            if tem_str == '〜' and tag == '':
                return True
            if tem_str == '〜が':
                return node['word'][-1] == 'が'
            if tem_str == '〜の':
                return node['word'][-1] == 'の'
            if tem_str == '〜を':
                return node['word'][-1] == 'を'
            if tem_str == '〜は':
                return node['word'][-1] == 'は'
            if tem_str == '〜ば':
                return node['word'][-1] == 'ば'
            if tem_str == '〜に':
                return node['word'][-1] == 'に'
            if tem_str == '〜も':
                return node['word'][-1] == 'も'
            if tem_str == '〜から':
                return node['word'][-1] == 'から'
            if tem_str == '〜まで':
                return node['word'][-1] == 'まで'
            if tem_str == '〜しか':
                return node['word'][-1] == 'しか'
            if tem_str == '〜さえ':
                return node['word'][-1] == 'さえ'
            if tem_str == '〜ない':
                return node['word'][-1] == 'ない'
            if tem_str == '〜ず':
                return node['word'][-1] == 'ず'
            if tem_str == '〜や':
                return node['word'][-1] == 'や'
            if tem_str == '〜いざ':
                return node['word'][-1] == 'いざ'
            if tem_str == '〜た':
                return node['word'][-1] == 'た' or node['word'][-1] == 'だ'
            if tem_str == '〜て':
                return node['word'][-1] == 'て' or node['word'][-1] == 'で'
            if tem_str == '〜で':
                return node['word'][-1] == 'で'
            if tem_str == '〜と':
                return node['word'][-1] == 'と' or node['word'][-1] == 'って'
            if tem_str == '〜という':
                return node['word'][-1] == 'という'
            if tem_str == '〜こと':
                return node['word'][-1] == 'こと'

            if tem_str == '〜には':
                return len(node['word'])>1 and node['word'][-1] == 'は' and\
                       node['word'][-2] == 'に'
            if tem_str == '〜にも':
                return len(node['word'])>1 and node['word'][-1] == 'は' and\
                       node['word'][-2] == 'も'
            if tem_str == '〜とは':
                return len(node['word'])>1 and node['word'][-1] == 'は' and\
                       node['word'][-2] == 'と'
            if tem_str == '〜とも':
                return node['word'][-1] == 'とも' or\
                       (len(node['word'])>1 and node['word'][-1] == 'も' and\
                       node['word'][-2] == 'と')
            if tem_str == '〜覚えは':
                return len(node['word'])>1 and node['word'][-1] == 'は' and\
                       node['word'][-2] in ['覚え','おぼえ']


            if tem_str == '〜かと':
                return len(node['word'])>1 and node['word'][-1] == 'と' and\
                       node['word'][-2] == 'か'
            if tem_str == '〜からと':
                return len(node['word'])>1 and node['word'][-1] == 'と' and\
                       node['word'][-2] == 'から'
            if tem_str == '〜ものと':
                return len(node['word'])>1 and node['word'][-1] == 'と' and\
                       node['word'][-2] == 'もの'
            if tem_str == '〜ては':
                return len(node['word'])>1 and node['word'][-1] == 'は' and\
                       (node['word'][-2] == 'て' or node['word'][-2] == 'で')
            if tem_str == '〜ても':
                return len(node['word'])>1 and node['word'][-1] == 'も' and\
                       (node['word'][-2] == 'て' or node['word'][-2] == 'で')
            if tem_str == '〜ずに':
                return len(node['word'])>1 and node['word'][-1] == 'に' and\
                       node['word'][-2] == 'ず'
            if tem_str == '〜ないで':
                return len(node['word'])>1 and node['word'][-1] == 'で' and\
                       node['word'][-2] == 'ない'
            if tem_str == '〜なくて':
                return len(node['word'])>1 and node['word'][-1] == 'て' and\
                       node['word'][-2] == 'なく'
            if tem_str == '〜ほうが':
                return len(node['word'])>1 and node['word'][-1] == 'が' and\
                       node['word'][-2] in ['ほう','方']
            if tem_str == '〜恐れが':
                return len(node['word'])>1 and node['word'][-1] == 'が' and\
                       node['word'][-2] in ['恐れ','おそれ']
            if tem_str == '〜嫌いが':
                return len(node['word'])>1 and node['word'][-1] == 'が' and\
                       node['word'][-2] in ['嫌い','きらい']
            if tem_str == '〜術が':
                return len(node['word'])>1 and node['word'][-1] == 'が' and\
                       node['word'][-2] in ['術','すべ']
            if tem_str == '〜試しが':
                return len(node['word'])>1 and node['word'][-1] == 'が' and\
                       node['word'][-2] in ['試し','ためし']
            if tem_str == '〜きりが':
                return len(node['word'])>1 and node['word'][-1] == 'が' and\
                       node['word'][-2] == 'きり'
            if tem_str == '〜ものが':
                return len(node['word'])>1 and node['word'][-1] == 'が' and\
                       node['word'][-2] == 'もの'
            if tem_str == '〜んが':
                return len(node['word'])>1 and node['word'][-1] == 'が' and\
                       node['word'][-2] == 'ん'
            if tem_str == '〜なければ':
                return len(node['word'])>1 and node['word'][-1] == 'ば' and\
                       (node['word'][-2] == 'なけれ')
            if tem_str == '〜ことに':
                return len(node['word'])>1 and node['word'][-1] == 'に' and\
                       (node['word'][-2] == 'こと')
            if tem_str == '〜ことは':
                return len(node['word'])>1 and node['word'][-1] == 'は' and\
                       (node['word'][-2] == 'こと')
            if tem_str == '〜ことも':
                return len(node['word'])>1 and node['word'][-1] == 'も' and\
                       (node['word'][-2] == 'こと')
            if tem_str == '〜ことの':
                return len(node['word'])>1 and node['word'][-1] == 'の' and\
                       (node['word'][-2] == 'こと')
            if tem_str == '〜ように':
                return len(node['word'])>1 and node['word'][-1] == 'に' and\
                       (node['word'][-2] == 'よう')
            if tem_str == '〜はめに':
                return len(node['word'])>1 and node['word'][-1] == 'に' and\
                       node['word'][-2] in ['はめ','羽目']
            if tem_str == '〜せてさせて':
                return len(node['word'])>1 and node['word'][-1] == 'て' and\
                       node['word'][-2] in ['せ','させ']
            if tem_str == '〜までの':
                return len(node['word'])>1 and node['word'][-1] == 'の' and\
                       (node['word'][-2] == 'まで')
            if tem_str == '〜以外の':
                return len(node['word'])>1 and node['word'][-1] == 'の' and\
                       (node['word'][-2] in ['以外','いがい'])
            if tem_str == '〜ことが':
                return node['word'][-1] == 'こと' or\
                       ((len(node['word'])>1 and node['word'][-1] in ['が','は','も'] and\
                       (node['word'][-2] == 'こと')))
            if tem_str == '〜はずが':
                return node['word'][-1] in ['はず','筈'] or\
                       ((len(node['word'])>1 and node['word'][-1] in ['が','は','も'] and\
                       (node['word'][-2] in ['はず','筈'])))
            if tem_str == '〜わけが':
                return node['word'][-1] in ['わけ','訳'] or\
                       ((len(node['word'])>1 and node['word'][-1] in ['が','は','も'] and\
                       (node['word'][-2] in ['わけ','訳'])))
            if tem_str == '〜べくも':
                return ((len(node['word'])>1 and node['word'][-1] == 'も' and\
                       (node['word'][-2] == 'べく')))



            if tem_str == '〜おご何に':
                return len(node['word'])>2 and node['word'][-1] == 'に' and\
                       (node['word'][-3] in ['お','ご','御'])
            if tem_str == '〜おご何':
                return len(node['word'])>1 and\
                       (node['word'][-2] in ['お','ご','御'])

            if tem_str == '〜てばかりは':
                return len(node['word'])>2 and node['word'][-1] == 'は' and\
                       node['word'][-2] == 'ばかり' and node['word'][-3] in ['て','で']
            if tem_str == '〜てばかりも':
                return len(node['word'])>2 and node['word'][-1] == 'も' and\
                       node['word'][-2] == 'ばかり' and node['word'][-3] in ['て','で']

            return False


        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        #match id_th word in node

        #match ~

        if tag != '':
            for t in Utl.split(tag,'＆'):
                if not t in node['tag'][id]:
                    return False

        if tem_str == '〜':
            return True

        #match str

        if morph:
            if tem_str == node['tag'][id][-3] or Utl.hirakana(tem_str) == Utl.hirakana(node['tag'][id][-3]):
                return True

        if tem_str == node['word'][id] or Utl.hirakana(tem_str) == Utl.hirakana(node['word'][id]):
            return True

        return False
        pass #match_one

    @staticmethod
    def if_complement(node, id):
        '''
        :param id: if id == -1 test entire node, else test node['word'][id]
        :return:
        '''

        # match entire node
        if id == -1:
            if Utl.multi_in(['係助詞', '格助詞', '副詞', '副詞可能', '副詞化', '連体化', '連体詞'], node['tag'][-1]):
                return True

            #return False
            return True


        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        #match id_th word in node
        if '名詞' in node['tag'][id] and id+1 < len(node['tag']) and '名詞' in node['tag'][id+1]:
            if '数' in node['tag'][id]and '数' in node['tag'][id+1]:
                return True
            if Utl.multi_in(['固有名詞','一般'],node['tag'][id]):
                return True

        if Utl.multi_in(['副詞', '連体詞'], node['tag'][id]):
            return True

        if '名詞' in node['tag'][id] and '副詞可能' in node['tag'][id]:
            if not (node['word'][id] in Japanese.no_adverb_noun):
                return True

        if 'サ変接続' in node['tag'][id] and id+1 < len(node['tag']) and 'する' in node['tag'][id+1]:
            return True

        #exact match


        return False

    @staticmethod
    def num_of_non_complement(dg, node_id, bid = 0, eid = -1):
        '''
        :param id: if node[bid:eid] are all complements
        :return:

        '''

        node = dg.nodelist[node_id]
        if eid == -1:
            eid = len(node['deps'])+len(node['word'])

        cnt = 0
        for i in range(bid,eid):
            if i >= len(node['deps']):
                r = Template.if_complement(node,i-len(node['deps']))
            else:
                r = Template.if_complement(dg.nodelist[node['deps'][i]],-1)
            if not r:
                cnt += 1

        return cnt