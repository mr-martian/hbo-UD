#!/usr/bin/env python3

# TODO LIST
# - maybe retag (e.g.) שם, פה

import sys
import unicodedata
import utils
utils.load_volume(sys.argv[1], globals())

def surf(w):
    return unicodedata.normalize('NFC', T.text(w).strip(F.trailer_utf8.v(w))) or 'blah'

def get(w, f):
    v = F.__getattribute__(f).v(w)
    if not v or v in ['NA', 'unknown', 'none']:
        return ''
    else:
        return f'<{v}>'

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
        print('^sb/sb<sb>$', end=' ')
    prev_s = s
    prev_v = v
    if c != prev_c:
        print('^cb/cb<cb>$', end=' ')
        prev_c = c
    if p != prev_p:
        print('^pb/pb<pb>$', end=' ')
        prev_p = p
    phr_ft = ''
    for f in feats:
        phr_ft += get(p, f)
        phr_ft += get(c, f)
    lu = '^' + surf(w) + '/' + unicodedata.normalize('NFC', F.lex_utf8.v(w))
    for f in feats:
        lu += get(w, f)
    lu += phr_ft
    lu += f'<w{w}><{T.bookName(w)}>$'
    prn = ''
    for f in ['prs_ps', 'prs_gn', 'prs_nu']:
        prn += get(w, f)
    if prn:
        lu += f'^prn/prn<prn>{prn}{phr_ft}$'
    for c in F.trailer_utf8.v(w):
        if c == ' ':
            lu += c
        #elif c in 'נפס':
        #    pass # skip inter-sentential punctuation
        else:
            lu += f'^{c}/{c}<punct>$\n'
    print(lu, end='')
print('')
