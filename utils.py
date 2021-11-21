#!/usr/bin/env python3

def get_id(block):
    ls = block.splitlines()
    for ln in ls:
        if ln.startswith('# sent_id'):
            return ln.split()[-1]

def clean_ref(block):
    ls = block.splitlines()
    return '\n'.join(ln for ln in ls if not ln.startswith('# checker'))

def load_conllu(fname, clean=False):
    with open(fname) as fin:
        ret = {}
        for i, block in enumerate(fin.read().strip().split('\n\n'), 1):
            b = block
            if clean:
                b = clean_ref(b)
            ret[get_id(block)] = (i, b)
        return ret
