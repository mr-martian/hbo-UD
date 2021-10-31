#!/usr/bin/env python3

from tf.app import use
A = use("bhsa", mod="etcbc/trees/tf,etcbc/bridging/tf", hoist=globals(), volume="Torah")

class Node:
    def __init__(self):
        self.pos = None
        self.w = None
        self.ch = None
    def from_ls(ls):
        N = Node()
        N.pos = ls[1]
        if len(ls) == 4 and ls[2].isnumeric():
            N.w = int(ls[2])
        else:
            N.ch = []
            start = 2
            c = 1
            for i in range(3, len(ls)-1):
                if ls[i] == '(':
                    c += 1
                elif ls[i] == ')':
                    c -= 1
                    if c == 0:
                        N.ch.append(Node.from_ls(ls[start:i+1]))
                        start = i + 1
            assert start == len(ls) - 1
        return N
    def from_str(s):
        print(s)
        return Node.from_ls(s.replace('(', ' ( ').replace(')', ' ) ').split())
    def iter(self):
        yield self
        for c in (self.ch or []):
            yield from c.iter()
            
POS_MAP = {
    'art': 'DET',
    'verb': 'VERB',
    'subs': 'NOUN',
    'nmpr': 'PROPN',
    'advb': 'ADV',
    'prep': 'ADP',
    'prps': 'PRON',
    'prde': 'PRON',
    'prin': 'PRON',
    'intj': 'INTJ',
    'nega': 'ADV', # TODO?
    'inrg': 'PART', # TODO?
    'adjv': 'ADJ'
}

BINYAN_MAP = {
    'hif': 'HIFIL',
    'hit': 'HITPAEL',
#    'htpo': '???', # hitpo'el
#    'hof': '???', # hof'al
    'nif': 'NIFAL',
    'piel': 'PIEL',
#    'poal': '???' # po'al
#    'poel': '???' # po'el
    'pual': 'PUAL',
    'qal': 'PAAL'
}

TENSE_MAP = {
    'perf': ['VerbForm=Fin', 'Mood=Ind', 'Aspect=Perf'],
    'impf': ['VerbForm=Fin', 'Mood=Ind', 'Aspect=Imp'],
    'wayq': ['VerbForm=Fin', 'Mood=Ind', 'Tense=Past'],
    'impv': ['VerbForm=Fin', 'Mood=Imp'],
    'infa': ['VerbForm=Inf'], # absolute
    'infc': ['VerbForm=Inf'], # construct
    'ptca': ['VerbForm=Part'],
    'ptcp': ['VerbForm=Part', 'Voice=Pass']
}

def word_cols(w):
    ret = []
    ret.append(T.text(w).strip())
    if len(F.trailer.v(w)) > 1:
        ret[0] = ret[0][:-1]
    ret.append(F.lex_utf8.v(w))
    pos = F.sp.v(w)
    if pos in POS_MAP:
        ret.append(POS_MAP[pos])
    elif pos == 'conj' and ret[1] == 'ו':
        ret.append('CCONJ')
    else:
        ret.append('_')
    ret.append(pos)
    morph = []

    if pos == 'prps':
        morph.append('PronType=Prs')
    elif pos == 'prde':
        morph.append('PronType=Dem')
    elif pos == 'prin':
        morph.append('PronType=Int')

    if F.gn.v(w) == 'm':
        morph.append('Gender=Masc')
    elif F.gn.v(w) == 'f':
        morph.append('Gender=Fem')

    if F.nu.v(w) == 'sg':
        morph.append('Number=Sing')
    elif F.nu.v(w) == 'du':
        morph.append('Number=Dual')
    elif F.nu.v(w) == 'pl':
        morph.append('Number=Plur')

    if F.ps.v(w).startswith('p'):
        morph.append('Person=' + F.ps.v(w)[1])

    if F.vs.v(w) in BINYAN_MAP:
        morph.append('HebBinyan=' + BINYAN_MAP[F.vs.v(w)])

    if F.vt.v(w) in TENSE_MAP:
        morph += TENSE_MAP[F.vt.v(w)]

    ret.append('|'.join(morph) or '_')
    return ret

class SentenceTree:
    def __init__(self, sid):
        self.sid = sid
        self.nodes = Node.from_str(F.tree.v(sid))
        self.words = list(L.d(self.sid, otype="word"))
        self.heads = [None] * len(self.words)
        self.rels = [None] * len(self.words)
        self.pos = {}
    def get_label(self):
        book = T.bookName(self.sid)
        ws = L.d(self.sid, otype="word")[0]
        we = L.d(self.sid, otype="word")[-1]
        chs = F.chapter.v(L.u(ws, otype="chapter")[0])
        che = F.chapter.v(L.u(we, otype="chapter")[0])
        vs = F.verse.v(L.u(ws, otype="verse")[0])
        ve = F.verse.v(L.u(we, otype="verse")[0])
        verse = ''
        if chs != che:
            verse = f'{chs}:{vs}-{che}:{ve}'
        elif vs != ve:
            verse = f'{chs}:{vs}-{ve}'
        else:
            verse = f'{chs}:{vs}'
        # TODO: this isn't unique if there are multiple sentences in a verse
        return f'Masoretic-{book}-{verse}-hbo'
    def add_rel(self, h, d, r):
        h_lab = '0' if h == 0 else str(self.words.index(h) + 1)
        idx_d = self.words.index(d)
        self.rels[idx_d] = r
        self.heads[idx_d] = h_lab
    def gen_rels(self):
        def phrase(w):
            loc = L.u(w, otype="phrase")
            if loc:
                return loc[0]
        def ptype(w):
            return F.typ.v(phrase(w))
        def words(w):
            return list(L.d(phrase(w), otype="word"))
        for i, w in enumerate(self.words):
            pos = F.sp.v(w)
            wls = words(w)
            print(w, pos, ptype(w), phrase(w))
            if pos == 'prep' and ptype(w) == 'PP':
                if len(wls) == 2 and wls[0] == w and F.sp.v(wls[1]) == 'subs':
                    self.add_rel(wls[1], w, 'case')
            elif pos == 'verb' and F.lex_utf8.v(w) != 'היה':
                l = [x for x in self.words if F.sp.v(x) == 'verb']
                if len(l) == 1:
                    # TODO: what if it's a participle modifying subj or obj?
                    self.add_rel(0, w, 'root')
    def get_pos(self):
        for c in self.nodes.iter():
            if not c.ch:
                self.pos[c.w] = [c.pos, None]
    def conllu(self):
        self.gen_rels()
        ret = '# sent_id = ' + self.get_label() + '\n'
        ret += '# text = ' + T.text(self.sid).strip() + '\n'
        words = list(L.d(self.sid, otype="word"))
        last_group = 0
        for i, w in enumerate(words, start=1):
            if i > last_group and F.trailer.v(w) == '':
                t = T.text(words[i-1])
                for j in range(i+1, len(words)+1):
                    t += T.text(words[j-1])
                    if F.trailer.v(words[j-1]) != '':
                        t = t.strip()
                        if F.trailer.v(words[j-1]) == '00 ':
                            t = t[:-1]
                        ret += f'{i}-{j}\t{t}\t' + '\t'.join(['_']*8) + '\n'
                        last_group = j
                        break
            ls = [str(i)]
            ls += word_cols(w)
            ls.append(self.heads[i-1] or '_')
            ls.append(self.rels[i-1] or '_')
            while len(ls) < 10:
                ls.append('_')
            ret += '\t'.join(ls) + '\n'
        ret += '\n'
        return ret

for s in list(F.otype.s('sentence'))[:4]:
    st = SentenceTree(s)
    print(st.conllu())
    #break
