#!/usr/bin/env python3

from collections import defaultdict
import unicodedata

def load_volume(vol, hoist):
    from tf.app import use
    import sys
    out = sys.stdout
    sys.stdout = open('blah.txt', 'w')
    if vol[0].isnumeric():
        v = vol[:2] + vol[2:].capitalize() + 'Book'
    else:
        v = vol.capitalize() + 'Book'
    use("ETCBC/bhsa:local", hoist=hoist, volume=v)
    sys.stdout.close()
    sys.stdout = out

def get_id(block):
    ls = block.splitlines()
    for ln in ls:
        if ln.startswith('# sent_id'):
            return ln.split()[-1]

def clean_ref(block):
    ls = block.splitlines()
    return '\n'.join(ln for ln in ls if not ln.startswith('# checker'))

def iter_conllu(fname):
    with open(fname) as fin:
        for block in fin.read().strip().split('\n\n'):
            if not block:
                continue
            yield get_id(block), block

def load_conllu(fname, clean=False):
    ret = {}
    for i, (n, b) in enumerate(iter_conllu(fname), 1):
        ret[n] = (i, clean_ref(b) if clean else b)
    return ret

def load_conllu_multi(fname):
    ret = defaultdict(list)
    for n, b in iter_conllu(fname):
        ret[n].append(b)
    return ret

def get_chapter(sid):
    def single(s):
        return int(s.split('-')[-1])
    p = sid.split(':')
    if len(p) == 2:
        return [single(p[0])]
    else:
        return [single(p[0]), single(p[1])]

def get_first_verse(sid):
    v1 = sid.split('-')[2]
    c, v = v1.split(':')
    return (int(c), int(v))

def split_lines(sent):
    head = []
    body = []
    for l in sent.strip().split('\n'):
        if l.startswith('#'):
            head.append(l)
        else:
            body.append(l)
    return head, body

def update_deps(old_sent, new_sent, old_headers=True):
    oh, ols = split_lines(old_sent)
    nh, nls = split_lines(new_sent)
    lines = oh if old_headers else nh
    if len(ols) != len(nls):
        return None
    for ol, nl in zip(ols, nls):
        ot = ol.split('\t')
        nt = nl.split('\t')
        if ot[0] != nt[0]:
            return None
        ot[6] = nt[6]
        ot[7] = nt[7]
        lines.append('\t'.join(ot))
    return '\n'.join(lines)

def get_cg(sent_id):
    book = sent_id.split('-')[1].lower()
    data = load_conllu(f'temp/merged/{book}.conllu')
    idx = data[sent_id][0]-1
    with open(f'temp/parsed-cg3/{book}.txt') as fin:
        return fin.read().split('\n\n')[idx]

def get_coref(book):
    with open(f'coref/spans/{book}.txt') as fin:
        for l in fin:
            ls = l.strip().split()
            if len(ls) != 2:
                continue
            yield (tuple(ls[0].split('-')), ls[1])

def iter_words(block):
    for ln in block.splitlines():
        ls = ln.strip().split('\t')
        if len(ls) == 10 and ls[0].isdigit():
            yield ls

def consonants_only(hbo):
    return ''.join(c for c in hbo if unicodedata.category(c) in ['Lo', 'Po', 'Zs', 'Pd'])

def grapheme_clusters(hbo):
    names = ['alef', 'bet', 'gimel', 'dalet', 'he', 'vav', 'zayin',
             'het', 'tet', 'yod', 'finkaf', 'kaf', 'lamed', 'finmem', 'mem',
             'finnun', 'nun', 'samekh', 'ayin', 'finpeh', 'peh',
             'fintsade', 'tsade', 'qof', 'resh', 'sin/shin', 'taf']
    vowels = ['sheva', 'hataf segol', 'hataf patah', 'hataf qamats',
              'hiriq', 'tsere', 'segol', 'patah', 'qamats', 'holam',
              'holam', 'qubuts']
    c = None
    d = False
    v = None
    for ch in hbo:
        cat = unicodedata.category(ch)
        if cat in ['Lo', 'Po', 'Pd', 'Zs']:
            if c:
                yield (c, d, v)
                c, d, v = None, False, None
            if cat == 'Lo':
                if ord(ch) == 0xfb2a:
                    c = 'shin'
                elif ord(ch) == 0xfb2b:
                    c = 'sin'
                else:
                    c = names[ord(ch) - 0x5d0]
            elif cat in ['Po', 'Pd']:
                yield ('punct', False, ch)
            elif cat == 'Zs':
                yield ('space', False, ch)
        elif cat == 'Mn':
            if ord(ch) < 0x5b0: # cantillation
                continue
            elif ord(ch) < 0x5bc:
                v = vowels[ord(ch) - 0x5b0]
            elif ord(ch) == 0x5bc:
                d = True
            elif ord(ch) == 0x5c1:
                if c == 'sin/shin':
                    c = 'shin'
            elif ord(ch) == 0x5c2:
                if c == 'sin/shin':
                    c = 'sin'
    if c:
        yield (c, d, v)

def transliterate_latex(hbo):
    name2latex = {
        'alef': "'", 'bet': 'b', 'gimel': 'g', 'dalet': 'd', 'he': 'h',
        'vav': 'w', 'zayin': 'z', 'het': '.h', 'tet': '.t', 'yod': 'y',
        'finkaf': 'K', 'kaf': 'k', 'lamed': 'l', 'finmem': 'M', 'mem': 'm',
        'finnun': 'N', 'nun': 'n', 'samekh': 's', 'ayin': '`',
        'finpeh': 'P', 'peh': 'p', 'fintsade': '.S', 'tsade': '.s',
        'qof': 'q', 'resh': 'r', 'sin/shin': '/s', 'sin': ',s',
        'shin': '+s', 'taf': 't',
        'sheva': ':', 'hataf segol': 'E:', 'hataf patah': 'a:',
        'hataf qamats': 'A:', 'hiriq': 'i', 'tsere': 'e', 'segol': 'E',
        'patah': 'a', 'qamats': 'A', 'holam': 'o', 'qubuts': 'u',
        None: '',
    }
    ret = r'\cjRL{'
    for c, d, v in grapheme_clusters(hbo):
        if c == 'space':
            ret += v
        elif c == 'punct':
            if ord(v) == 0x5c3:
                ret += ';'
            else:
                ret += ' '
        else:
            ret += name2latex[c]
            if d:
                ret += '*'
            if v:
                ret += name2latex[v]
    return ret + '}'

def transliterate_loc(hbo, latex):
    # TODO: qamats is sometimes "o" rather than "a"
    letters = {
        'gimel': 'g', 'dalet': 'd', 'he': 'h', 'zayin': 'z', 'yod': 'y',
        'lamed': 'l', 'finmem': 'm', 'mem': 'm', 'finnun': 'n', 'nun': 'n',
        'samekh': 's', 'fintsade': 'ts', 'tsade': 'ts', 'resh': 'r',
        'sin/shin': 'sh', 'shin': 'sh', 'taf': 't',
        'hataf segol': 'e', 'hataf patah': 'a',
        'hataf qamats': 'o', 'hiriq': 'i', 'tsere': 'e', 'segol': 'e',
        'patah': 'a', 'qamats': 'a', 'holam': 'o', 'qubuts': 'u',
    }
    if latex:
        letters.update({
            'alef': "'", 'vav': r'\d{v}', 'het': r'\d{h}', 'tet': r'\d{t}',
            'ayin': '`', 'qof': r'\d{k}', 'sin': r"\'{s}",
        })
    else:
        letters.update({
            'alef': 'ʼ', 'vav': 'ṿ', 'het': 'ḥ', 'tet': 'ṭ',
            'ayin': 'ʻ', 'qof': 'ḳ', 'sin': 'ś',
        })
    begedkefet = {
        'bet': ('v', 'b'), 'finkaf': ('kh', 'k'), 'kaf': ('kh', 'k'),
        'finpeh': ('f', 'p'), 'peh': ('f', 'p'),
    }
    ret = ''
    last_vowel_null = True
    last = (None, False, None)
    for c, d, v in grapheme_clusters(hbo):
        if c in ['space', 'punct']:
            ret += ' '
            last = (None, False, None)
            last_vowel_null = True
        elif c == 'yod' and not v:
            if last[2] == 'patah':
                ret += 'i'
        elif c == 'vav' and d:
            ret += 'u'
            last_vowel_null = False
        elif c == 'vav' and v == 'holam':
            ret += 'o'
            last_vowel_null = False
        elif c == 'vav' and not v and last[2] == 'holam':
            last_vowel_null = False
        else:
            if c in begedkefet:
                ret += begedkefet[c][int(last_vowel_null or d)]
            else:
                ret += letters[c]
            if v in letters:
                ret += letters[v]
                last_vowel_null = False
            elif v == 'sheva':
                if last_vowel_null:
                    ret += 'e'
                    last_vowel_null = False
                else:
                    last_vowel_null = True
        last = (c, d, v)
    return ret.strip()
