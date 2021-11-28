#!/usr/bin/env python3

from collections import defaultdict

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
