#!/usr/bin/env python3

import sys
import unicodedata
import utils
utils.load_volume(sys.argv[1], globals())

def norm(s):
    return unicodedata.normalize('NFC', s).replace('שׁ', 'שׁ').replace('שׂ', 'שׂ')

def surf(w):
    ws = norm(T.text(w).strip(F.trailer_utf8.v(w))) or 'blah'
    prs = F.prs.v(w)
    if prs and prs not in ['absent', 'n/a']:
        cons = {
            'W': ['ו', 'ה'],
            'J': ['י'],
            'K': ['כ', 'ך'],
            'H': ['ה', 'נ', 'ת'],
            'M': ['מ', 'ם'],
            'N': ['נ', 'ן'],
            # ignore '='
        }
        #print(ws, prs, file=sys.stderr)
        i = len(ws)-1
        p = len(prs)-1
        while p >= 0:
            if prs[p] not in cons:
                p -= 1
            elif ws[i] in cons[prs[p]]:
                p -= 1
                i -= 1
            else:
                i -= 1
                continue
        return ws[:i+1], ws[i+1:]
    else:
        return ws, ''

def get(w, f, p=''):
    v = F.__getattribute__(f).v(w)
    if not v or v in ['NA', 'unknown', 'none', '>']:
        return ''
    else:
        return f'<{p}{v}>'

def clause_parent(c):
    l = list(E.mother.f(c))
    if len(l) != 1:
        return ''
    p = l[0]
    if F.otype.v(p) == 'phrase':
        return f'<par:ph{p}>'
    elif F.otype.v(p) == 'clause':
        return f'<par:c{p}>'
    elif F.otype.v(p) == 'word':
        return f'<par:w{p}>'
    else:
        return ''

feats = ['sp', 'ls', 'vt', 'vs', 'typ', 'function', 'domain', 'gn', 'nametype', 'nu', 'ps', 'st', 'det']

prev_p = 0
prev_c = 0
prev_s = 0
prev_v = 0

for w in F.otype.s('word'):
    p = L.u(w, otype="phrase")[0]
    c = L.u(w, otype="clause")[0]
    s = L.u(w, otype="sentence")[0]
    v = L.u(w, otype="verse")[0]
    if s != prev_s and v != prev_v:
        print('^svb/svb<svb>$', end=' ')
    elif s != prev_s:
        print('^sb/sb<sb>$', end=' ')
    prev_s = s
    prev_v = v
    if c != prev_c:
        print('^cb/cb<cb>$', end=' ')
        prev_c = c
    if p != prev_p:
        print('^pb/pb<pb>$', end=' ')
        prev_p = p
    phr_ft = f'<ph{p}><c{c}><s{s}><{T.bookName(w)}><v{v}>'
    phr_ft += f'<pn{p%10}><cn{c%10}><sn{s%10}><vn{v%10}>'
    for f in feats:
        phr_ft += get(p, f)
        phr_ft += get(c, f)
    phr_ft += get(c, 'rela', 'rela:')
    phr_ft += clause_parent(c)
    q_depth = (F.txt.v(c) or '').count('Q')
    phr_ft += f'<txt:{q_depth}>'
    srf, psrf = surf(w)
    lem = norm(F.lex_utf8.v(w))
    tags = ''
    for f in feats:
        tags += get(w, f)
    tags += get(w, 'uvf', 'uvf:')
    tags += phr_ft
    tags += f'<w{w}>'
    lu = ''
    if ' ' in lem:
        lem_segs = lem.split()
        for i, l in enumerate(lem_segs):
            lu += f'^{srf}/{l}{tags}<wp{i+1}>$'
            if '־' in srf and i == 0 and len(lem_segs) == 2:
                lu += '^־/־<punct>$'
            elif '־' in srf and i == 1 and len(lem_segs) == 3 and T.bookName(w) == 'Deuteronomy':
                lu += '^־/־<punct>$'
    elif ' ' in srf:
        for i, s in enumerate(srf.split()):
            lu += f'^{s}/{lem}{tags}<wp{i+1}>$'
    else:
        lu = f'^{srf}/{lem}{tags}$'
    prn = ''
    for f in ['prs_ps', 'prs_gn', 'prs_nu']:
        prn += get(w, f)
    if prn:
        lu += f'^{psrf}/prn<prn>{prn}<w{w}p>{phr_ft}$'
    for c in F.trailer_utf8.v(w):
        if c == ' ':
            lu += c
        else:
            lu += f'^{c}/{c}<punct>$\n'
    print(lu, end='')
print('')
