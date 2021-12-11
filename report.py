#!/usr/bin/env python3

from collections import defaultdict
import sys
book = sys.argv[1]

total_sents = 0
total_words = 0
rel = 0
head = 0
pos = 0
check_sent = 0
check_word = 0
by_pos = defaultdict(lambda: [0,0,0,0])
with open(f'{book}.parsed.conllu') as fin:
    for line in fin:
        if '# sent_id' in line:
            total_sents += 1
        elif '\t' in line:
            ls = line.split('\t')
            if '-' in ls[0]:
                continue
            total_words += 1
            by_pos[ls[4]][0] += 1
            if ls[3] != '_':
                pos += 1
            else:
                by_pos[ls[4]][1] += 1
            if ls[6] != '_':
                head += 1
            else:
                by_pos[ls[4]][2] += 1
            if ls[7] != '_':
                rel += 1
            else:
                by_pos[ls[4]][3] += 1

checkers = defaultdict(lambda: 0)
with open(f'{book}.checked.conllu') as fin:
    for line in fin:
        if '# sent_id' in line:
            check_sent += 1
        elif '# checker =' in line:
            for n in line.split('=')[1].split(','):
                checkers[n.strip()] += 1
        elif '\t' in line:
            if '-' in line.split()[0]:
                continue
            check_word += 1

def table(headers, rows):
    actual_headers = headers[:2]
    for h in headers[2:]:
        actual_headers.append(h)
        actual_headers.append('%')
    lines = [''] * (len(rows)+1)
    for i in range(len(actual_headers)):
        col = [actual_headers[i]]
        for r in rows:
            if i < 2:
                col.append(r[i])
            elif i % 2 == 1:
                idx = (i - 3) // 2 + 2
                col.append(round(100.0 * r[idx] / r[1], 2))
            else:
                col.append(r[(i-2)//2 + 2])
        wd = max(len(str(s)) for s in col)
        for j, ent in enumerate(col):
            add = str(ent)
            mv = ' '*(wd - len(add))
            if isinstance(ent, str):
                add += mv
            else:
                add = mv + add
            if i > 0:
                lines[j] += ' | '
            lines[j] += add
    return lines[0] + '\n' + '-'*len(lines[0]) + '\n' + '\n'.join(lines[1:])

print('')
print(table(['', 'Total', 'Count'],
            [
                ['Sentences Checked', total_sents, check_sent],
                ['Words Checked', total_words, check_word],
                ['UPOS', total_words, pos],
                ['Have Head', total_words, head],
                ['Have Relation', total_words, rel]
            ]))
print('')
print(table(['POS Statistics', 'Count', 'Missing UPOS', 'Missing Head', 'Missing Rel'],
            [ [k] + by_pos[k] for k in sorted(by_pos.keys()) ]))
print('\nAnnotators:')
for name, count in checkers.items():
    print(f'    {name}: {count} sentences')

