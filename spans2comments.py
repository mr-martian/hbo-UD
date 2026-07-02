import argparse
from collections import defaultdict
import utils

parser = argparse.ArgumentParser()
parser.add_argument('book')
args = parser.parse_args()

spans = defaultdict(list)

for (start, end), eid in utils.get_coref(args.book):
    s, w1 = start.split(':')
    w2 = end.split(':')[1]
    spans[int(s)].append(f'{w1}-{w2}-{eid}')

with open(f'coref/comment-spans/{args.book}.conllu', 'w') as fout:
    for i, (sid, block) in enumerate(utils.iter_conllu(f'data/checked/{args.book}.conllu'), 1):
        head, body = utils.split_lines(block)
        print('\n'.join(head), file=fout)
        print('# coref_spans = ', ' '.join(spans[i]), file=fout)
        print('\n'.join(body), file=fout)
        print('', file=fout)
