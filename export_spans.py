#!/usr/bin/env python3

import utils
import sys

for book in sys.argv[1:]:
    ids = [x[0] for x in utils.iter_conllu(f'coref/base/{book}.conllu')]
    print(ids)
    for (start, end), eid in utils.get_coref(book):
        sent = int(start.split(':')[0])-1
        w1 = start.split(':')[1]
        w2 = end.split(':')[1]
        print('\t'.join([ids[sent], w1, w2, eid]))
