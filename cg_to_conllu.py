#!/usr/bin/env python3

import sys
import unicodedata
import utils
BOOK = sys.argv[1]
utils.load_volume(BOOK, globals())
BOOK_ABBR = utils.load_book_data('Ref')[BOOK]
BOOK_OFFSET = int(utils.load_book_data('BHSA-start')[BOOK])

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
    'nega': 'ADV',
    'inrg': 'PART', # TODO?
    'adjv': 'ADJ',
    'punct': 'PUNCT',
    'prn': 'PRON',
    'aux': 'AUX',
    'SCONJ': 'SCONJ'
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
    #'htpo': ['HebBinyan=HITPOEL'], #TODO
    'hof': ['HebBinyan=HUFAL'], # TODO: rename?
    'nif': ['HebBinyan=NIFAL'],
    'piel': ['HebBinyan=PIEL'],
    'poal': ['HebBinyan=PUAL'], # TODO: separate?
    'poel': ['HebBinyan=PIEL'], # TODO: separate?
    'pual': ['HebBinyan=PUAL'],
    'qal': ['HebBinyan=PAAL'],
    'nega': ['Polarity=Neg'],
    'prn': ['PronType=Prs'],
    'prps': ['PronType=Prs'],
    'prde': ['PronType=Dem'],
    'prin': ['PronType=Int'],
    'card': ['NumType=Card'],
    'ordn': ['NumType=Ord'],
    'art': ['PronType=Art'],
    'dir_he': ['Case=Loc'],
    #'uvf:H': ['Case=Loc'], # TODO
}

MISC = {
    'sdbh': 'LId[SDBH]',
    'ld': 'LexDomain[SDBH]',
    'mid': 'Ref[MACULA]',
    'strong': 'LId[Strongs]',
}

def norm(s):
    return unicodedata.normalize('NFC', s)

class Word:
    def __init__(self):
        self.wid = 0
        self.seg = 0

        # conllu collumns
        self.pos = ''
        self.surf = ''
        self.lemma = ''
        self.upos = ''
        self.xpos = ''
        self.feats = []
        self.head = ''
        self.rel = ''
        self.misc = []

        # helper data, filled by self.get_info()
        self.text = ''
        self.tail = ''
        self.is_end = True
    def get_info(self):
        last_wid = self.wid
        if isinstance(self.wid, list):
            last_wid = self.wid[-1]
        if last_wid != 0:
            self.text = norm(T.text(self.wid))
            self.tail = norm(F.trailer_utf8.v(last_wid))
            if last_wid == 15747 and T.bookName(last_wid) == 'Genesis':
                self.tail = ' '
            if self.tail:
                self.text = self.text.rstrip(self.tail)
            if last_wid == 12311 and T.bookName(last_wid) == 'Exodus':
                self.tail = self.tail.strip()
                self.text += 'ס'
                self.misc.append('SpaceAfter=No')
            if (' ' in self.text or '־' in self.text) and self.seg != 0:
                if self.seg == 1:
                    self.tail = ' ' if ' ' in self.text else '־'
                    self.wid = 0
                self.text = self.text.replace('־', ' ').split()[self.seg-1]
                self.surf = self.text
            if last_wid == 6450 and BOOK_ABBR == 'DEUT' and self.seg == 2:
                self.misc.append('SpaceAfter=No')
            if (F.prs.v(last_wid) and F.prs.v(last_wid) not in ['absent', 'n/a']):
                self.is_end = False
            ch = F.chapter.v(L.u(last_wid, otype='verse')[0])
            vs = F.verse.v(L.u(last_wid, otype='verse')[0])
            self.misc.append(f'Ref={BOOK_ABBR}_{ch}.{vs}')
            self.misc.append(f'Ref[BHSA]={last_wid+BOOK_OFFSET}')
            lex = L.u(last_wid, otype='lex')
            if lex:
                gloss = F.gloss.v(lex[0])
                if gloss:
                    self.misc.append(f'Gloss={gloss}')
        if self.xpos not in ['punct', 'prn'] and not self.tail:
            self.is_end = False
        cant = utils.get_cantillation(self.surf)
        if cant:
            self.misc.append('Cantillation=' + ','.join(cant))
    def from_cg(self, inp):
        self.lemma = inp.split('"')[1]
        parts = inp.split('"')[-1].split()
        self.xpos = parts[0]
        if self.xpos in POS_MAP:
            self.upos = POS_MAP[self.xpos]
            if self.upos == 'VERB' and self.lemma == 'היה':
                self.upos = 'AUX'
        elif self.lemma == 'עד' and self.xpos == 'conj':
            self.upos = 'ADP'
        for tg in parts:
            if tg in MORPH:
                self.feats += MORPH[tg]
            elif tg.startswith('ExtPos='):
                self.feats.append(tg)
            elif tg.startswith('wp'):
                self.seg = int(tg[2:])
            elif tg[0] == 'w' and tg[-1] != 'p':
                self.wid = int(tg[1:])
                #self.misc.append('BHSA=' + str(self.wid))
                if self.xpos == 'SCONJ':
                    self.wid = [self.wid-1, self.wid]
                    self.xpos = 'verb'
            elif tg[0] == '#':
                self.pos, self.head = tg[1:].split('->')
                if self.head == self.pos:
                    self.head = ''
            elif tg[0] == '@':
                self.rel = tg[1:]
                if self.rel == 'advmod' and self.upos == 'VERB':
                    self.upos = 'ADV'
                elif self.rel == 'mark' and self.xpos == 'prep' and 'ExtPos=SCONJ' not in self.feats:
                    self.upos = 'SCONJ'
                elif self.rel == 'fixed' and self.xpos == 'conj':
                    self.upos = 'SCONJ'
            elif tg.startswith('retag:'):
                if self.xpos == 'conj' and tg in ['retag:art', 'retag:subs']:
                    self.upos = 'SCONJ'
                self.xpos = tg[6:]
                if self.xpos == 'nmpr' and 'subs' in parts:
                    self.upos = 'NOUN'
            elif tg == 'has_prn':
                self.is_end = False
            if tg in ['card', 'ordn']:
                self.upos = 'NUM'
            for pfx in MISC:
                if tg.startswith(pfx+':'):
                    self.misc.append(MISC[pfx] + '=' + tg[len(pfx)+1:])
        if self.xpos == 'conj':
            if self.lemma == 'ו' or self.lemma == 'או':
                self.upos = 'CCONJ'
            elif self.rel == 'mark':
                self.upos = 'SCONJ'
        if self.upos in ['ADP', 'SCONJ']:
            self.feats = [x for x in self.feats if 'ExtPos' in x]
        elif self.upos == 'ADV':
            self.feats = [x for x in self.feats if 'Polarity' in x]
        elif self.upos == 'VERB' and self.lemma in ['ישׁ', 'אין']:
            self.feats = ['VerbForm=Fin', 'Mood=Ind']
        if self.rel == 'cop':
            self.upos = 'AUX'
            if self.lemma == 'הוה':
                self.lemma = 'היה'
        self.get_info()
    def to_conllu(self):
        ls = [
            self.pos,
            self.surf or '_',
            self.lemma or '_',
            self.upos or '_',
            self.xpos or '_',
            '|'.join(sorted(set(self.feats), key=lambda x: x.lower())) or '_',
            self.head or '_',
            self.rel or '_',
            '_',
            '|'.join(sorted(set(self.misc), key=lambda x: x.lower())) or '_'
        ]
        return '\t'.join(ls)

class Sentence:
    def __init__(self):
        self.text = ''
        self.sid = ''
        self.real_words = []
        self.all_words = []
    def from_cg(self, stream):
        surf = ''
        for line in stream:
            if not line.strip() or '<svb>' in line:
                break
            elif line[0] == '"':
                surf = line.strip()[2:-2]
                if surf == 'blah':
                    surf = '_'
            elif line[0] == '\t':
                if line[1] == '\t':
                    # no idea what happened here
                    # but see psalms 1896
                    continue
                w = Word()
                w.surf = surf
                w.from_cg(line.strip())
                self.real_words.append(w)
    def get_ids(self):
        ret = []
        for w in self.real_words:
            if isinstance(w.wid, list):
                ret += w.wid
            elif w.wid != 0:
                ret.append(w.wid)
        return sorted(set(ret))
    def get_verses(self):
        ret = set()
        for i in self.get_ids():
            ret.update(L.u(i, otype='verse'))
        return sorted(ret)
    def add_compounds(self):
        gps = []
        cur = []
        for w in self.real_words:
            cur.append(w)
            if w.is_end:
                gps.append(cur)
                cur = []
        for i, g in enumerate(gps):
            if len(g) > 1:
                surf = ''.join(w.text for w in g)
                tail = ''.join(w.tail for w in g)
                nw = Word()
                nw.surf = surf
                nw.pos = g[0].pos + '-' + g[-1].pos
                if not tail or tail[0] != ' ':
                    nw.misc.append('SpaceAfter=No')
                self.all_words.append(nw)
                self.all_words += g
                #for w in g:
                #    w.surf = '_'
            else:
                w = g[0]
                w.surf = w.lemma if w.xpos == 'punct' else w.text
                if w.xpos == 'punct' and w.lemma == '־':
                    w.misc.append('SpaceAfter=No')
                elif w.tail and w.tail[0] != ' ':
                    w.misc.append('SpaceAfter=No')
                self.all_words.append(w)
    def process(self):
        last_misc = ''
        for w in self.real_words:
            for m in w.misc:
                if m.startswith('Ref='):
                    last_misc = m
                    break
            else:
                if last_misc:
                    w.misc.append(last_misc)
        self.add_compounds()
        ids = self.get_ids()
        self.text = norm(T.text(self.get_verses()).strip())
        ws = min(ids)
        we = max(ids)
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
        for w in self.all_words:
            if w.xpos != 'punct':
                tr = utils.transliterate_loc(w.surf, False)
                w.misc.append('Translit=' + tr)
        ret = f'# sent_id = {self.sid}\n# text = {self.text}\n'
        ret += '# translit = ' + utils.transliterate_loc(self.text, False) + '\n'
        return ret + '\n'.join(w.to_conllu() for w in self.all_words) + '\n'

if __name__ == '__main__':
    while True:
        s = Sentence()
        s.from_cg(sys.stdin)
        if not s.real_words:
            break
        s.process()
        print(s.to_conllu())
