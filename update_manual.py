#!/usr/bin/env python3

import argparse
import utils

parser = argparse.ArgumentParser('Fix morphology etc for manual sentences')
parser.add_argument('book', action='store')
args = parser.parse_args()

gen = utils.load_conllu(f'temp/merged/{args.book}.conllu')
man = utils.load_conllu(f'data/manual/{args.book}.conllu')

ret = []
for sid, sent in man.items():
    if sid not in gen:
        print(f'{args.book} manual includes {sid}, which is not in generated')
        ret.append((0, sent))
        continue
    res = utils.update_deps(gen[sid][1], sent[1], False)
    idx = gen[sid][0]
    if not res:
        print(f'{args.book} manual/generated token mismatch in {sid} (index {idx})')
        ret.append((-1, sent))
        continue
    ret.append((idx, res))

ret.sort()
with open(f'data/manual/{args.book}.conllu', 'w') as fout:
    fout.write('\n\n'.join(r[1] for r in ret) + '\n\n')

