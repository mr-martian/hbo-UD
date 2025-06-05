#!/usr/bin/env python3

import collections
from flask import Flask, request, render_template
import json
import os
import subprocess
import sys
import utils

base_dir = os.path.dirname(__file__)
app = Flask('hbo-UD',
            static_folder=os.path.join(base_dir, 'static'),
            static_url_path='/static',
            template_folder=os.path.join(base_dir, 'templates'))

@app.route('/')
def main_page():
    return render_template('index.html',
                           books=utils.load_book_data('id').values())

def all_ids(fname):
    with open(fname) as fin:
        for line in fin:
            if line.startswith('# sent_id'):
                yield line

@app.route('/book/<book_id>/')
def book_report(book_id):
    total = collections.Counter()
    acc = collections.Counter()
    for line in all_ids(f'data/checked/{book_id}.conllu'):
        acc[0] += 1
        for c in utils.get_chapter(line):
            acc[c] += 1
    for line in all_ids(f'temp/macula-merged/{book_id}.conllu'):
        total[0] += 1
        for c in utils.get_chapter(line):
            total[c] += 1
    chapters = []
    for k in sorted(total.keys()):
        a = acc[k]
        t = total[k]
        chapters.append((k, a, t, round(100*a/t,2)))
    return render_template('book_report.html', book_id=book_id,
                           chapters=chapters)

@app.route('/book/<book_id>/chapter/<int:ch>/', methods=['GET', 'POST'])
def review_chapter(book_id, ch):
    acc = []
    for key in request.form:
        if key.isdigit():
            acc.append(int(key))
    if acc:
        utils.accept(book_id, 'Daniel', acc)
        return app.redirect(f'/book/{book_id}/chapter/{ch}/')
    gen = utils.load_conllu(f'temp/macula-merged/{book_id}.conllu')
    ref = utils.load_conllu(f'data/checked/{book_id}.conllu')
    data = []
    for key in gen:
        if (ch == 0 or utils.get_chapter(key)[0] == ch) and key not in ref:
            blob = utils.conllu2display(book_id, gen[key][1])
            blob['index'] = gen[key][0]
            data.append((gen[key][0], json.dumps(blob)))
    return render_template('edit_chapter.html', book_id=book_id,
                           chapter=ch, sentences=data)

@app.route('/check/<book_id>/<int:sent>/', methods=['GET', 'POST'])
def diffsent(book_id, sent):
    rules = request.form.get('rules', '')
    clean_rules = f'#{sent}\n'
    dct = {}
    heads = set()
    for line in rules.splitlines():
        ls = line.split()
        if len(ls) > 1:
            dct[ls[0]] = ls[1:]
            if ls[1] != '_':
                heads.add(ls[1])
    if dct:
        inp = utils.show(book_id, sent, 'raw')
        head_locs = {'0': '0'}
        for line in inp.splitlines():
            ls = line.split()
            for h in heads:
                if h in ls:
                    head_locs[h] = line.split('→')[0].split('#')[1]
                    break
        lines = []
        for line in inp.splitlines():
            for k in dct:
                if ' '+k+' ' in line:
                    print(k, line, file=sys.stderr)
                    if dct[k][0] != '_':
                        pieces = line.split('→')
                        subpieces = pieces[1].split(' ', 1)
                        line = pieces[0] + '->' + head_locs[dct[k][0]]
                        if len(subpieces) == 2:
                            line += ' ' + subpieces[1]
                    line += ' ' + ' '.join(dct[k][1:])
            lines.append(line)
        proc = subprocess.run(['bash', 'test-sent.sh', book_id, str(sent)],
                              input='\n'.join(lines).encode('utf-8'),
                              capture_output=True)
        diff = proc.stdout.decode('utf-8')
        for key in sorted(dct):
            line = key + '\t' + dct[key][0]
            if len(dct[key]) > 1:
                line += '\t' + '><'.join(dct[key][1:])
            clean_rules += line + '\n'
    else:
        diff = ''
    return render_template('diffsent.html', book_id=book_id, sentence=sent,
                           tree=json.dumps(utils.conllu2display(
                               book_id,
                               utils.show(book_id, sent, 'conllu'),
                               utils.show(book_id, sent, 'ref'))),
                           cg=utils.show(book_id, sent, 'cg'),
                           raw=utils.show(book_id, sent, 'raw'),
                           diff=diff, rules=rules, clean_rules=clean_rules)

@app.route('/check/<book_id>/<int:sent>/accept/', methods=['POST'])
def accept_single(book_id, sent):
    utils.accept(book_id, 'Daniel', [sent])
    return app.redirect(f'/check/{book_id}/{sent}/')

@app.route('/check/<book_id>/')
def check(book_id):
    gen = utils.load_conllu(f'temp/macula-merged/{book_id}.conllu')
    ref = utils.load_conllu(f'data/checked/{book_id}.conllu', True)
    fail = []
    for k in ref:
        if k in gen and gen[k][1] != ref[k][1]:
            fail.append(gen[k][0])
    return render_template('check.html', book_id=book_id, fail=fail)
