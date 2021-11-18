#!/usr/bin/env python3

# TODO LIST
# - maybe retag (e.g.) שם, פה

from tf.app import use
A = use("bhsa", mod="etcbc/trees/tf,etcbc/bridging/tf", hoist=globals(), volume="Torah")

def surf(w):
    return T.text(w).strip(F.trailer_utf8.v(w))

def get(w, f):
    v = F.__getattribute__(f).v(w)
    if not v or v in ['NA', 'unknown', 'none']:
        return ''
    else:
        return f'<{v}>'

feats = ['sp', 'ls', 'vt', 'vs', 'typ', 'function', 'gn', 'nametype', 'nu', 'ps', 'st']

for w in F.otype.s('word'):
    p = L.u(w, otype="phrase")[0]
    lu = '^' + surf(w) + '/' + F.lex_utf8.v(w)
    for f in feats:
        lu += get(w, f)
        lu += get(p, f)
    lu += f'<w{w}>$'
    prn = ''
    for f in ['prs_ps', 'prs_gn', 'prs_nu']:
        prn += get(w, f)
    if prn:
        lu += f'^prn/prn{prn}$'
    for c in F.trailer_utf8.v(w):
        if c == ' ':
            lu += c
        else:
            lu += f'^{c}/{c}<punct>$'
    print(lu, end='')
    if w > 40: break
print('')
