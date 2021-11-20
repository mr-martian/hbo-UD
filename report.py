#!/usr/bin/env python3

from collections import defaultdict

total_sents = 0
total_words = 0
rel = 0
head = 0
pos = 0
check_sent = 0
check_word = 0
with open('generated.conllu') as fin:
    for line in fin:
        if '# sent_id' in line:
            total_sents += 1
        elif '\t' in line:
            ls = line.split('\t')
            if '-' in ls[0]:
                continue
            total_words += 1
            if ls[3] != '_':
                pos += 1
            if ls[6] != '_':
                head += 1
            if ls[7] != '_':
                rel += 1

checkers = defaultdict(lambda: 0)
with open('checked.conllu') as fin:
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
    lines = [''] * (len(rows)+1)
    for i in range(len(headers)):
        col = [headers[i]]
        for r in rows:
            if i == len(r):
                col.append(round(100.0 * r[i-2] / r[i-1], 2))
            else:
                col.append(r[i])
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

print(table(['', 'Count', 'Total', 'Percent'],
            [
                ['Sentences Checked', check_sent, total_sents],
                ['Words Checked', check_word, total_words],
                ['UPOS', pos, total_words],
                ['Have Head', head, total_words],
                ['Have Relation', rel, total_words]
            ]))
print('\nAnnotators:')
for name, count in checkers.items():
    print(f'    {name}: {count} sentences')

