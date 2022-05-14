#!/usr/bin/env python3

import argparse
import sys

import utils

parser = argparse.ArgumentParser()
parser.add_argument('gen', action='store')
parser.add_argument('ref', action='store')
parser.add_argument('man', action='store')
args = parser.parse_args()

gen = utils.load_conllu(args.gen)
ref = utils.load_conllu(args.ref, True)
man = utils.load_conllu(args.man, True)

fail = []
for k in ref:
    if k in gen and gen[k][1] != ref[k][1]:
        print(f'Sentence {gen[k][0]} ({k}) differs!')
        fail.append(str(gen[k][0]))

if fail:
    print(f'{len(fail)} sentences in {args.gen} differ from accepted!')
    print(' '.join(fail))
    sys.exit(1)

