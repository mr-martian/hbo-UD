#!/usr/bin/env python3

import argparse
import sys

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
        for block in fin.read().strip().split('\n\n'):
            if clean:
                ret[get_id(block)] = clean_ref(block)
            else:
                ret[get_id(block)] = block
        return ret

parser = argparse.ArgumentParser()
parser.add_argument('gen', action='store')
parser.add_argument('ref', action='store')
args = parser.parse_args()

gen = load_conllu(args.gen)
ref = load_conllu(args.ref, True)

fail = False
for k in ref:
    if k in gen and gen[k] != ref[k]:
        print(f'Sentence {k} differs!')
        fail = True

if fail:
    sys.exit(1)

