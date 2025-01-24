#!/usr/bin/env python3

import argparse
import sys

import utils

parser = argparse.ArgumentParser()
parser.add_argument('b', action='store', help='Book')
parser.add_argument('n', action='store', type=int, help='Sentence index')
parser.add_argument('modes', nargs='*',
                    choices=['cg', 'conllu', 'raw', 'ref', 'docs', 'latex'])
args = parser.parse_args()

gen = utils.load_conllu(f'temp/macula-merged/{args.b}.conllu')
sid = None
for k in gen:
    if gen[k][0] == args.n:
        sid = k
        break
else:
    print(f'No sentence found at index {args.n}')
    sys.exit(1)

for m in args.modes or ['cg', 'conllu']:
    if m == 'cg':
        with open(f'temp/macula-parsed-cg3/{args.b}.txt') as fin:
            print(fin.read().strip().split('\n\n')[args.n-1])
    elif m == 'conllu':
        print(gen[sid][1])
    elif m == 'raw':
        with open(f'temp/macula-cg3/{args.b}.txt') as fin:
            cur = []
            i = -1
            for line in fin:
                if not line.strip():
                    continue
                cur.append(line.rstrip())
                if '#1→' in cur[-1]:
                    if i == args.n:
                        print('\n'.join(cur[:-2]))
                        break
                    else:
                        cur = cur[-2:]
                        i += 1
    elif m == 'ref':
        ref = utils.load_conllu(f'data/checked/{args.b}.conllu', True)
        if sid in ref:
            print(ref[sid][1])
        else:
            print(f'Sentence at index {args.n} ({sid}) has not been confirmed.')
            sys.exit(1)
    elif m == 'docs':
        block = gen[sid][1]
        print(f'<!-- {args.b} {args.n} -->')
        print('~~~ conllu')
        text = ''
        for line in block.splitlines():
            if line.startswith('# text ='):
                text = line[9:].strip()
            if line.count('\t') != 9:
                print(line)
            else:
                ls = line.split('\t')
                if not ls[0].isdigit():
                    ls[9] = '_'
                else:
                    ls[9] = ls[9].replace(' ', '.')
                print('\t'.join(ls))
        print('')
        print('~~~')
        text = [l for l in block.splitlines() if l.startswith('# text')][0]
        text = text.split('=')[1].strip()
        print('\n_' + utils.consonants_only(text) + '_\n')
        print('_' + utils.transliterate_loc(text, False) + '_')
    elif m == 'latex':
        forms = []
        translit = []
        pos = []
        arcs = []
        block = gen[sid][1]
        words = list(utils.iter_words(block))
        for ls in reversed(words):
            wid = len(words) - int(ls[0]) + 1
            head = 0 if ls[6] == '0' else len(words) - int(ls[6]) + 1
            forms.append(utils.transliterate_latex(ls[1]))
            translit.append(utils.transliterate_loc(ls[1], True))
            pos.append(ls[3])
            if head == 0:
                arcs.append(f'\\deproot{{{wid}}}{{root}}')
            else:
                arcs.append(f'\\depedge{{{head}}}{{{wid}}}{{{ls[7]}}}')
        print('\\begin{dependency}')
        print('  \\begin{deptext}')
        print('    ' + ' \\& '.join(forms) + r' \\')
        print('    ' + ' \\& '.join(translit) + r' \\')
        print('    ' + ' \\& '.join(pos) + r' \\')
        print('  \\end{deptext}')
        print('  ' + '\n  '.join(arcs))
        print('\\end{dependency}')
