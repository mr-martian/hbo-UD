#!/usr/bin/env python3

import sys
book = sys.argv[1]

with open(f'temp/conv/{book}.conllu') as af:
    with open(f'temp/punct/{book}.conllu') as bf:
        with open(f'temp/merged/{book}.conllu', 'w') as out:
            for al, bl in zip(af, bf):
                ls = []
                for a, b, in zip(al.strip().split('\t'), bl.strip().split('\t')):
                    if a == b:
                        ls.append(a)
                    elif a == 'SpaceAfter=No':
                        ls.append(a)
                    else:
                        ls.append(b)
                out.write('\t'.join(ls) + '\n')
