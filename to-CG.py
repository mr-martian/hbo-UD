#!/usr/bin/env python3

import sys
import unicodedata
import utils
utils.load_volume(sys.argv[1], globals())

def norm(s):
    return unicodedata.normalize('NFC', s).replace('שׁ', 'שׁ').replace('שׂ', 'שׂ')

def surf(w):
    return norm(T.text(w).strip(F.trailer_utf8.v(w))) or 'blah'

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
    phr_ft = f'<ph{p}><c{c}><s{s}><{T.bookName(w)}>'
    for f in feats:
        phr_ft += get(p, f)
        phr_ft += get(c, f)
    phr_ft += get(c, 'rela', 'rela:')
    phr_ft += clause_parent(c)
    q_depth = (F.txt.v(c) or '').count('Q')
    phr_ft += f'<txt:{q_depth}>'
    srf = surf(w)
    if srf != 'blah':
        srf = srf[:len(F.g_lex_utf8.v(w))] or 'blah'
    lem = norm(F.lex_utf8.v(w))
    tags = ''
    for f in feats:
        tags += get(w, f)
    tags += get(w, 'uvf', 'uvf:')
    tags += phr_ft
    tags += f'<w{w}>'
    lu = ''
    if ' ' in lem:
        for i, l in enumerate(lem.split()):
            lu += f'^{srf}/{l}{tags}<wp{i+1}>$'
            if '־' in srf and i == 0:
                lu += '^־/־<punct>$'
    else:
        lu = f'^{srf}/{lem}{tags}$'
    prn = ''
    for f in ['prs_ps', 'prs_gn', 'prs_nu']:
        prn += get(w, f)
    if prn:
        srf = surf(w)[len(F.g_lex_utf8.v(w)):]
        lu += f'^{srf}/prn<prn>{prn}<w{w}p>{phr_ft}$'
    for c in F.trailer_utf8.v(w):
        if c == ' ':
            lu += c
        else:
            lu += f'^{c}/{c}<punct>$\n'
    print(lu, end='')
print('')
