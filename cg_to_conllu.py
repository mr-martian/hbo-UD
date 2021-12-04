#!/usr/bin/env python3

from tf.app import use
A = use("bhsa", mod="etcbc/trees/tf,etcbc/bridging/tf", hoist=globals(), volume="Torah")

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
    'adjv': 'ADJ',
    'punct': 'PUNCT',
    'prn': 'PRON'
}

MORPH = {
    'perf': ['VerbForm=Fin', 'Mood=Ind', 'Aspect=Perf'],
    'impf': ['VerbForm=Fin', 'Mood=Ind', 'Aspect=Imp'],
    'wayq': ['VerbForm=Fin', 'Mood=Ind', 'Tense=Past'],
    'impv': ['VerbForm=Fin', 'Mood=Imp'],
    'infa': ['VerbForm=Inf'], # absolute
    'infc': ['VerbForm=Inf'], # construct
    'ptca': ['VerbForm=Part'],
    'ptcp': ['VerbForm=Part', 'Voice=Pass'],
    'm': ['Gender=Masc'],
    'f': ['Gender=Fem'],
    'sg': ['Number=Sing'],
    'du': ['Number=Dual'],
    'pl': ['Number=Plur'],
    'p1': ['Person=1'],
    'p2': ['Person=2'],
    'p3': ['Person=3'],
    'hif': ['HebBinyan=HIFIL'],
    'hit': ['HebBinyan=HITPAEL'],
#    'htpo': '???', # hitpo'el
#    'hof': '???', # hof'al
    'nif': ['HebBinyan=NIFAL'],
    'piel': ['HebBinyan=PIEL'],
#    'poal': '???' # po'al
#    'poel': '???' # po'el
    'pual': ['HebBinyan=PUAL'],
    'qal': ['HebBinyan=PAAL'],
}

class Word:
    def __init__(self):
        self.wid = 0
        self.pos = ''
        self.surf = ''
        self.lemma = ''
        self.upos = ''
        self.xpos = ''
        self.feats = []
        self.head = ''
        self.rel = ''
    def from_cg(self, inp):
        self.lemma = inp.split('"')[1]
        parts = inp.split('"')[-1].split()
        self.xpos = parts[0]
        if self.xpos in POS_MAP:
            self.upos = POS_MAP[self.xpos]
        for tg in parts[1:]:
            if tg in MORPH:
                self.feats += MORPH[tg]
            elif tg[0] == 'w':
                self.wid = int(tg[1:])
            elif tg[0] == '#':
                self.pos, self.head = tg[1:].split('->')
                if self.head == self.pos:
                    self.head = ''
            elif tg[0] == '@':
                self.rel = tg[1:]
        if self.xpos == 'conj':
            if self.lemma == 'ו' or self.lemma == 'או':
                self.upos = 'CCONJ'
            elif self.rel == 'mark':
                self.upos = 'SCONJ'
        if self.rel == 'nummod':
            self.upos = 'NUM'
    def to_conllu(self):
        ls = [
            self.pos,
            self.surf or '_',
            self.lemma or '_',
            self.upos or '_',
            self.xpos or '_',
            '|'.join(sorted(self.feats)) or '_',
            self.head or '_',
            self.rel or '_',
            '_',
            '_'
        ]
        return '\t'.join(ls)

class Sentence:
    def __init__(self):
        self.text = ''
        self.sid = ''
        self.real_words = []
        self.all_words = []
    def from_cg(self, stream):
        for line in stream:
            if not line.strip():
                break
            elif line[0] == '\t':
                w = Word()
                w.from_cg(line.strip())
                self.real_words.append(w)
    def process(self):
        in_group = False
        ids = []
        for i, w in enumerate(self.real_words):
            if w.wid != 0:
                ids.append(w.wid)
            if w.wid == 0 or (in_group and F.trailer.v(w.wid)):
                if w.xpos == 'punct':
                    w.surf = w.lemma
                in_group = False
            elif not in_group and not F.trailer.v(w.wid):
                in_group = True
                pos = w.pos + '-'
                surf = T.text(w.wid)
                for j in range(i+1, len(self.real_words)):
                    w2 = self.real_words[j]
                    surf += T.text(w2.wid)
                    t = F.trailer_utf8.v(w2.wid)
                    if t:
                        surf = surf[:-len(t)]
                        k = j
                        if j+1 < len(self.real_words) and self.real_words[j+1].wid == 0 and self.real_words[j+1].xpos != 'punct':
                            k += 1
                        nw = Word()
                        nw.pos = pos + self.real_words[k].pos
                        nw.surf = surf.strip()
                        self.all_words.append(nw)
                        break
            elif not in_group and F.trailer.v(w.wid):
                w.surf = T.text(w.wid).rstrip(F.trailer_utf8.v(w.wid))
            self.all_words.append(w)
        self.text = T.text(ids).strip()
        ws = min(*ids)
        we = max(*ids)
        book = T.bookName(ws)
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
        self.sid = f'Masoretic-{book}-{verse}-hbo'
    def to_conllu(self):
        ret = f'# sent_id = {self.sid}\n# text = {self.text}\n'
        return ret + '\n'.join(w.to_conllu() for w in self.all_words) + '\n'

if __name__ == '__main__':
    import sys
    while True:
        s = Sentence()
        s.from_cg(sys.stdin)
        if not s.real_words:
            break
        s.process()
        print(s.to_conllu())
