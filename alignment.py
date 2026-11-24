import unicodedata

xml_id = '{http://www.w3.org/XML/1998/namespace}id'

bhsa_skip_nodes = {
    'genesis': [28427, 28426, 28460, 28461, 16564, 17279],
    'numbers': [8083, 21962],
    'joshua': [8625],
}

macula_skip_nodes = {
    'leviticus': ['o030270330051ה'],
    'numbers': ['o040340040061'],
}

def skip(c):
    if ord(c) > 0x5ea:
        return True # trop
    if ord(c) == 0x5c3:
        return True # sof pasuq
    if ord(c) < 0x5d0:
        return True # vowel
    return False

def clean(s):
    s2 = (s or '').replace(chr(0xfb2a), chr(0x5e9)).replace(chr(0xfb2b), chr(0x5e9))
    s3 = ''.join(c for c in s2.strip() if not skip(c))
    return unicodedata.normalize('NFC', s3)

def remsuf(a, b):
    if not b:
        return a
    if not a.endswith(b):
        return a
    return a[:-len(b)]

name_groups = {
    '883+': ['B>R/', 'LXJ_R>J/'],
    '884+': ['B>R/', 'CB<==/'],
    '6636': ['YB>JM/'],
    '1976': ['H', 'LZH'],
    '763+': ['>RM/', 'NHR/'],
    '3026 a': ['JGR/', 'FHDW/'],
    '4772': ['MRGLT/'],
}

merge_groups = {
    'LMH': ['l', '4100'],
    'LKN': ['l', '3651c'],
    'HXJRWT/': ['d', '6367'],
    'M<LH_<QRBJM/': [None, '4610'],
}

class Aligner:
    def __init__(self, book, sentence, bhsa0, F, T):
        self.bhsa_skip = set(bhsa_skip_nodes.get(book, []))
        self.macula_skip = set(macula_skip_nodes.get(book, []))
        self.sentence = sentence
        self.start = bhsa0
        self.idx = bhsa0
        self.F = F
        self.T = T
        self.align()

    def matches(self, node, idx):
        bt = remsuf(self.T.text(idx) or '', self.F.trailer_utf8.v(idx))
        mt = node.text
        btc = clean(bt)
        mtc = clean(mt)
        if btc == mtc:
            return True
        if self.F.prs.v(idx) and btc.startswith(mtc):
            return True
        return False

    def lex(self, idx):
        return self.F.lex.v(idx)

    def strong(self, node):
        return node.attrib.get('oshb-strongs')

    def is_split_prefix(self, node, idx):
        if self.strong(node) == '1976' and self.lex(idx) == 'H' \
           and self.lex(idx+1) == 'LZH':
            return True
        if self.strong(node) == '935' and self.lex(idx) == 'L' \
           and self.lex(idx+1) == 'BW>[':
            return True
        return False

    def is_merge_group(self, m1, m2, idx):
        b = self.lex(idx)
        return b in merge_groups and merge_groups[b] == [
            self.strong(m1), self.strong(m2)]

    def is_np_second(self, node, idx):
        if self.lex(idx) == '>RM/' and self.lex(idx-1) == 'PDN/':
            return True
        return False

    def is_name_group(self, node, idx):
        lm = self.strong(node)
        if lm in name_groups:
            for i in range(len(name_groups[lm])):
                if self.lex(idx+i) != name_groups[lm][i]:
                    return (False, 0)
            return (True, len(name_groups[lm]))
        return (False, 0)

    def extract_morphemes(self, node):
        if node.tag == 'm':
            if node.attrib[xml_id] not in self.macula_skip:
                yield node
        elif node.tag == 'c':
            yield node[0]
            for n in node[1:]:
                if n.attrib.get('pos') == 'noun':
                    yield n
        else:
            for ch in node:
                yield from self.extract_morphemes(ch)

    def align(self):
        self.morphs = list(self.extract_morphemes(self.sentence))
        self.morphs.sort(key=lambda m: m.attrib[xml_id])
        self.mapping = {}
        skip_next = False
        for mi, m in enumerate(self.morphs):
            if skip_next:
                skip_next = False
                continue
            mid = m.attrib[xml_id]
            while self.idx in self.bhsa_skip:
                self.idx += 1
            if self.is_np_second(m, self.idx):
                self.idx += 1
            if m.attrib['pos'] == 'suffix':
                if m.attrib['type'] == 'pronominal':
                    self.mapping[mid] = str(self.idx-1) + 'p'
                continue
            if mi+1 < len(self.morphs):
                mnext = self.morphs[mi+1]
                if self.is_merge_group(m, mnext, self.idx):
                    skip_next = True
                    self.mapping[mnext.attrib[xml_id]] = self.idx
                    self.idx += 1
                    continue
            if self.is_split_prefix(m, self.idx):
                self.mapping[mid] = self.idx + 1
                self.idx += 2
                continue
            ok, n = self.is_name_group(m, self.idx)
            if ok:
                self.mapping[mid] = self.idx
                self.idx += n
                continue
            if self.matches(m, self.idx):
                self.mapping[mid] = self.idx
                self.idx += 1
                continue
