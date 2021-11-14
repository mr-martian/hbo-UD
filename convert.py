#!/usr/bin/env python3

# TODO LIST
# - maybe retag (e.g.) שם, פה

from tf.app import use
A = use("bhsa", mod="etcbc/trees/tf,etcbc/bridging/tf", hoist=globals(), volume="Torah")

from functools import reduce

PUNCT = reduce(lambda x,y: x.union(y), [set(x[0].split()) for x in F.trailer_utf8.freqList()])

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
        #print(s)
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
    if isinstance(w, int):
        ret.append(T.text(w).strip())
        if len(F.trailer.v(w)) > 1:
            ret[0] = ret[0][:-1]
        ret.append(F.lex_utf8.v(w))
    elif w in PUNCT:
        return [w, w, 'PUNCT', '_', '_']
    else:
        ret += [w, w] # TODO: is this what should be there?
    pos = F.sp.v(w)
    if not isinstance(w, int):
        pos = 'prps'
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

    if F.gn.v(w) == 'm' or w in ['הוא', 'הם']:
        morph.append('Gender=Masc')
    elif F.gn.v(w) == 'f' or w in ['היא', 'הן']:
        morph.append('Gender=Fem')

    if F.nu.v(w) == 'sg' or w in ['הוא', 'היא']:
        morph.append('Number=Sing')
    elif F.nu.v(w) == 'du':
        morph.append('Number=Dual')
    elif F.nu.v(w) == 'pl' or w in ['הם', 'הן']:
        morph.append('Number=Plur')

    if w in ['הוא', 'היא', 'הם', 'הן']:
        morph.append('Person=p3')
    elif F.ps.v(w).startswith('p'):
        morph.append('Person=' + F.ps.v(w)[1])

    if F.vs.v(w) in BINYAN_MAP:
        morph.append('HebBinyan=' + BINYAN_MAP[F.vs.v(w)])

    if F.vt.v(w) in TENSE_MAP:
        morph += TENSE_MAP[F.vt.v(w)]

    ret.append('|'.join(morph) or '_')
    return ret

PHRASE_RULES = [
    # [ phrase_type, [ POS... ], [ [head, dep, rel] ... ] ]
    #['VP', ['prep', 'verb'], []],
    ['PP', ['prep', ['prde', 'prin']], [[1, 0, 'case']]],
    ['PP', ['prep', 'art', 'adjv'], [[2, 0, 'case']]],
    ['PP', ['prep', 'adjv'], [[1, 0, 'case']]]
]

def match_single(pos, pat):
    if isinstance(pat, str):
        return pat == pos
    elif isinstance(pat, list):
        return any(match_single(pos, p) for p in pat)
    else:
        return False # TODO: tuple conditions

def match(posls, pat):
    if len(posls) != len(pat):
        return False
    return all(match_single(x,y) for x,y in zip(posls, pat))

def get_prn(w):
    pers = F.prs_ps.v(w)
    gen = F.prs_gn.v(w)
    num = F.prs_nu.v(w)
    key = f'{pers}-{gen}-{num}'
    dct = {
        'p3-m-sg': 'הוא',
        'p3-f-sg': 'היא',
        'p3-m-pl': 'הם',
        'p3-f-pl': 'הן'
    }
    return dct.get(key)

HEADED = set()

class SentenceTree:
    def __init__(self, sids):
        self.sids = sids
        self.nodes = []
        self.words = []
        for sid in self.sids:
            self.nodes.append(Node.from_str(F.tree.v(sid)))
            for w in L.d(sid, otype="word"):
                self.words.append(w)
                p = get_prn(w)
                if p:
                    self.words.append(p)
                self.words += F.trailer_utf8.v(w).split()
        self.heads = [None] * len(self.words)
        self.rels = [None] * len(self.words)
        self.pos = {}
    def get_label(self):
        book = T.bookName(self.sids[0])
        ws = L.d(self.sids[0], otype="word")[0]
        we = L.d(self.sids[-1], otype="word")[-1]
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
        return f'Masoretic-{book}-{verse}-hbo'
    def add_rel(self, h, d, r):
        global HEADED
        if isinstance(d, int):
            if d in HEADED:
                f = T.text(d)
                #print(f'Word {d} ({f}) assigned a head multiple times!')
            HEADED.add(d)
        h_lab = '0' if h == 0 else str(self.words.index(h) + 1)
        idx_d = self.words.index(d)
        self.rels[idx_d] = r
        self.heads[idx_d] = h_lab
    def phrases(self):
        for s in self.sids:
            yield from L.d(s, otype="phrase")
    def gen_rels(self):
        def phrase(w):
            loc = L.u(w, otype="phrase")
            if loc:
                return loc[0]
        def ptype(w):
            return F.typ.v(phrase(w))
        def words(w):
            return list(L.d(phrase(w), otype="word"))
        def is_noun(w):
            pos = F.sp.v(w)
            if pos in ['subs', 'nmpr']:
                return True
            elif pos == 'verb' and F.vt.v(w) in ['ptca', 'ptcp', 'infa', 'infc']:
                return True
            return False
        def is_NP(w):
            if is_noun(w):
                return True
            elif F.sp.v(w) in ['prps', 'prde', 'adjv']: # TODO: adj?
                return True
            return False
        phrase_heads = {}
        for phr in self.phrases():
            wdls = list(L.d(phr, otype="word"))
            posls = [F.sp.v(x) for x in wdls]
            for typ, pat, rels in PHRASE_RULES:
                if typ == F.typ.v(phr) and match(posls, pat):
                    for h, d, r in rels:
                        self.add_rel(wdls[h], wdls[d], r)
            nouns = ['subs', 'nmpr']
            for i, p in enumerate(posls):
                if p == 'prep':
                    if i+1 < len(posls) and is_noun(wdls[i+1]):
                        self.add_rel(wdls[i+1], wdls[i], 'case')
                    elif i+2 < len(posls) and posls[i+1] in ['art', 'prep'] and is_noun(wdls[i+2]):
                        # TODO: double check prep prep
                        self.add_rel(wdls[i+2], wdls[i], 'case')
                    elif i+3 < len(posls) and posls[i+1] == 'prep' and posls[i+2] == 'art' and is_noun(wdls[i+3]):
                        self.add_rel(wdls[i+3], wdls[i], 'case')
                elif p == 'art':
                    if i+1 < len(posls) and (is_noun(wdls[i+1]) or posls[i+1] in ['adjv', 'prps', 'prde']):
                        self.add_rel(wdls[i+1], wdls[i], 'det')
                    elif i+1 < len(posls) and posls[i+1] == 'prde':
                        self.add_rel(wdls[i+1], wdls[i], 'det')
                elif is_noun(wdls[i]) and F.st.v(wdls[i]) == 'c':
                    if i+1 < len(posls) and is_noun(wdls[i+1]):
                        self.add_rel(wdls[i], wdls[i+1], 'compound:smixut')
                    elif i+2 < len(posls) and posls[i+1] == 'art' and is_noun(wdls[i+2]):
                        self.add_rel(wdls[i], wdls[i+2], 'compound:smixut')
                elif p == 'adjv':
                    for j in reversed(range(i)):
                        if is_noun(wdls[j]):
                            if F.nu.v(wdls[i]) == F.nu.v(wdls[j]) and F.gn.v(wdls[i]) == F.gn.v(wdls[j]):
                                self.add_rel(wdls[j], wdls[i], 'nmod')
                                break
                elif p == 'prde' or p == 'prps':
                    for j in reversed(range(i)):
                        if wdls[j] not in HEADED and is_noun(wdls[j]):
                            self.add_rel(wdls[j], wdls[i], 'nmod') # TODO: ask about this
                            break
            wunhd = [w for w in wdls if w not in HEADED]
            if len(wunhd) > 1 and all(is_NP(x) for x in wunhd):
                for w in wunhd[1:]:
                    self.add_rel(wunhd[0], w, 'appos') # TODO: check trees
            elif len(wunhd) > 1 and all(is_NP(x) or F.sp.v(x) == 'conj' for x in wunhd):
                for i, w in enumerate(wunhd):
                    if i > 0 and is_NP(w):
                        self.add_rel(wunhd[0], w, 'conj')
                    elif i+1 < len(wunhd) and F.sp.v(w) == 'conj' and is_NP(wunhd[i+1]):
                        self.add_rel(wunhd[i+1], w, 'cc')
            wunhd = [w for w in wdls if w not in HEADED]
            if len(wunhd) == 1:
                phrase_heads[phr] = wunhd[0]
        phr_lst = [(p, F.function.v(p)) for p in self.phrases()]
        if len(phrase_heads) == len(phr_lst):
            root = None
            for i, (phr, fun) in enumerate(phr_lst):
                if fun == 'Objc':
                    for j in reversed(range(i)):
                        if phr_lst[j][1] == 'Pred':
                            self.add_rel(phrase_heads[phr_lst[j][0]],
                                         phrase_heads[phr], 'obj')
                            break
                elif fun == 'Pred':
                    if root:
                        self.add_rel(root, phrase_heads[phr], 'conj')
                    else:
                        self.add_rel(0, phrase_heads[phr], 'root')
                        root = phrase_heads[phr]
                elif fun == 'Subj':
                    for pos in [i-1, i+1]:
                        if pos in range(len(phr_lst)):
                            if phr_lst[pos][1] == 'Pred':
                                self.add_rel(phrase_heads[phr_lst[pos][0]],
                                             phrase_heads[phr], 'nsubj')
                                break
            if root:
                root_loc = str(self.words.index(root)+1)
                for i, w in enumerate(self.words):
                    if w in PUNCT:
                        self.rels[i] = 'punct'
                        self.heads[i] = root_loc
        for i, w in enumerate(self.words):
            pos = F.sp.v(w)
            #wls = words(w)
            #print(w, pos, ptype(w), phrase(w), F.function.v(phrase(w)))
            if pos == 'verb' and F.lex_utf8.v(w) != 'היה':
                l = [x for x in self.words if F.sp.v(x) == 'verb']
                if len(l) == 1:
                    # TODO: what if it's a participle modifying subj or obj?
                    #self.add_rel(0, w, 'root')
                    pass
    def get_pos(self):
        for c in self.nodes.iter():
            if not c.ch:
                self.pos[c.w] = [c.pos, None]
    def conllu(self):
        self.gen_rels()
        ret = '# sent_id = ' + self.get_label() + '\n'
        ret += '# text = ' + ' '.join(T.text(s).strip() for s in self.sids) + '\n'
        words = self.words
        last_group = 0
        for i, w in enumerate(words, start=1):
            if i > last_group:
                if F.trailer.v(w) == '':
                    t = T.text(words[i-1])
                    for j in range(i+1, len(words)+1):
                        t += T.text(words[j-1])
                        if F.trailer.v(words[j-1]) != '':
                            t = t.strip(F.trailer_utf8.v(words[j-i]))
                            last_group = j
                            break
                    if last_group < len(words) and not isinstance(words[last_group], int):
                        last_group += 1
                    ret += f'{i}-{last_group}\t{t}\t' + '\t'.join(['_']*8) + '\n'
                elif i < len(words) and not isinstance(words[i], int) and words[i] not in PUNCT:
                    j = i+1
                    t = T.text(words[i-1])
                    ret += f'{i}-{j}\t{t}\t' + '\t'.join(['_']*8) + '\n'
            ls = [str(i)]
            ls += word_cols(w)
            ls.append(self.heads[i-1] or '_')
            ls.append(self.rels[i-1] or '_')
            while len(ls) < 10:
                ls.append('_')
            ret += '\t'.join(ls) + '\n'
        ret += '\n'
        return ret

def sent_seg():
    def start_verse(sent):
        return F.verse.v(L.u(L.d(sent, otype="word")[0], otype="verse")[0])
    def end_verse(sent):
        return F.verse.v(L.u(L.d(sent, otype="word")[0], otype="verse")[0])
    sents = list(F.otype.s('sentence'))
    ret = []
    i = 0
    while i < len(sents):
        ls = [sents[i]]
        v = end_verse(sents[i])
        while i+1 < len(sents) and start_verse(sents[i+1]) == v:
            i += 1
            ls.append(sents[i])
            v = end_verse(sents[i])
        i += 1
        ret.append(ls)
    return ret

with open('generated.conllu', 'w') as fout:
    for s in sent_seg():
        st = SentenceTree(s)
        st.gen_rels()
        fout.write(st.conllu())

#for p in F.otype.s('phrase'):
#    wf = L.d(p, otype="word")
#    wl = [x for x in wf if x not in HEADED]
#    if len(wl) > 1:
#        print(F.typ.v(p), [F.sp.v(x) for x in wl], [F.sp.v(x) for x in wf])
