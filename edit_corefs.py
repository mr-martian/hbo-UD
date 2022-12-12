#!/usr/bin/env python3

import utils
import cmd
from collections import defaultdict, Counter
import re

CONLL_COLUMNS = {
    'id': 1,
    'surf': 2,
    'lem': 3,
    'lemma': 4,
    'upos': 4,
    'xpos': 5,
    'morph': 6,
    'head': 7,
    'deprel': 8,
    'edeps': 9,
    'misc': 10,
}

class CorefCorpus:
    def __init__(self, book):
        self.book = book
        self.spans = dict(utils.get_coref(book))
        self.trees = list(utils.iter_conllu(f'coref/base/{book}.conllu'))
        self.tree_maps = []
        for tree in self.trees:
            dct = {}
            mx = 0
            for ln in tree[1].splitlines():
                if ln.startswith('# text ='):
                    dct['text'] = ln.split('=')[-1].strip()
                    continue
                wid = ln.split('\t')[0]
                if wid.isdigit():
                    dct[int(wid)] = ln
                    mx = int(wid)
            dct['len'] = mx
            self.tree_maps.append(dct)
        self.span_ids = defaultdict(set)
        for sid in self.spans.values():
            self.span_ids[sid[0]].add(sid)
        self.names = {}
        self.rev_names = {}
        with open(f'coref/spans/names.txt') as fin:
            for line in fin.readlines():
                i, n = line.split()
                self.span_ids[i[0]].add(i)
                if n != '_':
                    self.names[n] = i
                self.rev_names[i] = n
    def ispans(self, unk_only=False):
        ls = self.spans.keys()
        if unk_only:
            ls = [s for s,i in self.spans.items() if i[0] == 'u']
        yield from sorted(ls, key=self.parse_span)
    def save(self):
        with open(f'coref/spans/{self.book}.txt', 'w') as fout:
            for sp in self.ispans():
                fout.write(f'{sp[0]}-{sp[1]} {self.spans[sp]}\n')
        with open(f'coref/spans/names.txt', 'w') as fout:
            ls = sorted(self.rev_names.keys(), key=lambda x: (x[0], int(x[1:])))
            for n in ls:
                fout.write(f'{n} {self.rev_names[n]}\n')
    def update_span(self, span, new_id, save=True):
        nid = self.names.get(new_id, new_id)
        self.spans[span] = nid
        self.span_ids[new_id[0]].add(nid)
        if save:
            self.save()
    def parse_span(self, span):
        sent = int(span[0].split(':')[0])-1
        w1 = int(span[0].split(':')[1])
        w2 = int(span[1].split(':')[1])
        return sent, w1, w2
    def get_span(self, sent, w1, w2, window=2):
        dct = self.tree_maps[sent]
        cl = max(w1-window, 1)
        cr = min(w2+window, dct['len'])
        for i in range(cl, cr+1):
            yield (i, dct[i])
    def matches(self, span, key, column=-1):
        def comp(k, v):
            if isinstance(k, str):
                return k in v
            else:
                return k.match(v)
        sent, w1, w2 = self.parse_span(span)
        for i, line in self.get_span(sent, w1, w2, window=0):
            if column == -1:
                if comp(key, line):
                    return True
            else:
                if comp(key, line.split('\t')[column-1]):
                    return True
        return False
    def search(self, key, spans, column=-1):
        k = key
        if k.startswith('/') and k.endswith('/'):
            k = re.compile(key.strip('/'))
        return [s for s in spans if self.matches(s, k, column)]
    def print_span(self, span, window=2, window_only=False):
        sent, w1, w2 = self.parse_span(span)
        if not window_only:
            print(self.trees[sent][0])
            print(self.tree_maps[sent]['text'])
        for i, ln in self.get_span(sent, w1, w2, window):
            if i == w1:
                print('|', end=' ')
            print(ln.split('\t')[2], end=' ')
            if i == w2:
                print('|', end=' ')
        print('')
        print(f'{span[0]}-{span[1]} {self.spans[span]} ({self.rev_names.get(self.spans[span], "")})')
    def replace_span(self, old, new):
        if new not in self.spans:
            self.spans[new] = self.spans[old]
        del self.spans[old]
    def next_id(self, prefix, name=None, save=True):
        n = len(self.span_ids[prefix])+1
        while prefix+str(n) in self.span_ids[prefix]:
            n += 1
        sid = prefix+str(n)
        if name:
            self.names[name] = sid
            self.rev_names[sid] = name
            self.span_ids[prefix].add(sid)
            if save:
                self.save()
        return sid
    def name_id(self, name, sid):
        self.names[name] = sid
        self.rev_names[sid] = name
        self.save()
    def stats(self):
        freq = Counter()
        for span, sid in self.spans.items():
            freq[sid[0]] += 1
        for typ, cnt in freq.most_common():
            print(f'    {typ}: {cnt}\t({round(100.0*cnt/len(self.spans), 2)}%)')
        print(f'TOTAL: {len(self.spans)}')

class CorefCLI(cmd.Cmd):
    prompt = '> '
    def __init__(self, corpus, all_spans=None):
        self.corpus = corpus
        self.all_spans = all_spans or self.corpus.ispans(unk_only=True)
        self.todo_spans = []
        self.cur_span = None
        self.cur_col = -1
        self.macros = {}
        super().__init__()
        self.next_span()
    def next_span(self):
        self.cur_span = None
        if not self.todo_spans:
            self.todo_spans = all_spans
            if not self.todo_spans:
                print('No unknown spans remain. Search if you want to merge anything.')
                return
        self.cur_span = self.todo_spans[0]
        if self.cur_span not in self.corpus.spans:
            self.todo_spans.pop(0)
            self.next_span()
            return
        self.corpus.print_span(self.cur_span)
    def search(self, arg, spans):
        self.todo_spans = self.corpus.search(arg, spans, self.cur_col)
        print(f'{len(self.todo_spans)} results for "{arg}"')
        self.next_span()
    def do_search(self, arg):
        self.search(arg, self.all_spans)
    def do_searchwithin(self, arg):
        self.search(arg, self.todo_spans)
    def do_setcol(self, arg):
        try:
            self.cur_col = int(CONLL_COLUMNS.get(arg.lower, arg or '-1'))
        except:
            print(f'Unknown column {arg}')
    def do_new(self, arg):
        ls = arg.split()
        c = ls[0]
        name = ls[1] if len(ls) > 1 else None
        self.cur_id = None
        if len(c) != 1:
            print(f'ID type must be single character, not {c}')
        elif name in self.corpus.names:
            print(f'Name {name} already exists')
        else:
            self.cur_id = self.corpus.next_id(c, name)
            print(f'New ID: {self.cur_id}')
    def do_setnew(self, arg):
        self.do_new(arg)
        self.do_yes('')
    def do_rename(self, arg):
        ls = arg.split()
        if ls[1] in self.corpus.names:
            print(f'Name {ls[1]} already exists')
        elif len(ls) == 2:
            self.corpus.name_id(ls[1], ls[0])
    def current_token(self, line):
        ls = line.split()
        if line[-1].isspace():
            return ('', len(ls))
        else:
            return (ls[-1], len(ls)-1)
    def completion_list(self, prefix, keys, tok):
        if not prefix:
            return list(keys)
        ln = 0
        if len(prefix) > len(tok):
            ln = len(prefix) - len(tok)
        return [l[ln:] for l in keys if l.startswith(prefix)]
    def do_set(self, arg):
        if self.cur_span and arg:
            self.corpus.update_span(self.cur_span, arg)
            if self.todo_spans and self.todo_spans[0] == self.cur_span:
                self.todo_spans.pop(0)
        self.next_span()
    def complete_set(self, text, line, beginidx, endidx):
        key, tok = self.current_token(line)
        return self.completion_list(key, self.corpus.names.keys(), text)
    def complete_fix(self, text, line, beginidx, endidx):
        key, tok = self.current_token(line)
        if tok == 1:
            return self.completion_list(key, ['%s-%s' % s for s in self.corpus.ispans()], text)
        elif tok == 2:
            return self.completion_list(key, self.corpus.names.keys(), text)
    def do_setid(self, arg):
        self.cur_id = arg
    def do_yes(self, arg):
        self.do_set(self.cur_id)
    def do_yesall(self, arg):
        if self.cur_id:
            for sp in self.todo_spans:
                self.corpus.update_span(sp, self.cur_id, save=False)
                self.corpus.print_span(sp, window_only=True)
            self.corpus.save()
            self.todo_spans = []
            self.next_span()
    def do_no(self, arg):
        if self.todo_spans:
            self.todo_spans.pop(0)
        self.next_span()
    def do_skip(self, arg):
        n = int(arg or '10')
        if self.todo_spans:
            self.todo_spans = self.todo_spans[n:]
        self.next_span()
    def do_y(self, arg):
        self.do_yes('')
    def do_n(self, arg):
        self.do_no('')
    def do_singletons(self, arg):
        self.todo_spans = [s for s in self.todo_spans if s[0] == s[1]]
        print(f'{len(self.todo_spans)} results')
        self.next_span()
    def do_fix(self, arg):
        ls = arg.split()
        sp = tuple(ls[0].split('-'))
        if sp not in self.corpus.spans:
            print(f'Unknown span {sp}')
        elif len(ls) == 2:
            self.corpus.update_span(sp, ls[1])
    def replace_cur_span(self, sent, w1, w2):
        new_span = (f'{sent+1}:{w1}', f'{sent+1}:{w2}')
        self.corpus.replace_span(self.cur_span, new_span)
        if self.todo_spans[0] == self.cur_span:
            self.todo_spans[0] = new_span
        self.cur_span = new_span
        self.corpus.save()
        self.corpus.print_span(self.cur_span, window_only=True)
    def update_cur_span(self, w1shift, w2shift):
        if self.cur_span:
            sent, w1, w2 = self.corpus.parse_span(self.cur_span)
            w1 += w1shift
            w2 += w2shift
            if 1 <= w1 <= w2 <= self.corpus.tree_maps[sent]['len']:
                self.replace_cur_span(sent, w1, w2)
    def do_addnext(self, arg):
        self.update_cur_span(0, 1)
    def do_addprev(self, arg):
        self.update_cur_span(-1, 0)
    def do_remfirst(self, arg):
        self.update_cur_span(1, 0)
    def do_remlast(self, arg):
        self.update_cur_span(0, -1)
    def do_shiftfirst(self, arg):
        try:
            self.update_cur_span(int(arg), 0)
        except:
            print(f'Invalid argument {arg}')
    def do_sf(self, arg):
        self.do_shiftfirst(arg)
    def do_shiftlast(self, arg):
        try:
            self.update_cur_span(0, int(arg))
        except:
            print(f'Invalid argument {arg}')
    def do_sl(self, arg):
        self.do_shiftlast(arg)
    def do_del(self, arg):
        if self.cur_span:
            del self.corpus.spans[self.cur_span]
            self.corpus.save()
            self.todo_spans.pop(0)
            self.next_span()
    def do_recent(self, arg):
        if self.cur_span:
            all_spans = list(self.corpus.ispans())
            idx = all_spans.index(self.cur_span)
            n = int(arg or '5')
            for i in range(max(idx-n, 0), idx):
                self.corpus.print_span(all_spans[i], window_only=True)
    def do_near(self, arg):
        if self.cur_span:
            all_spans = list(self.corpus.ispans())
            idx = all_spans.index(self.cur_span)
            n = int(arg or '5')
            for i in range(max(idx-n, 0), min(idx+n, len(all_spans))):
                self.corpus.print_span(all_spans[i], window_only=True)
    def do_show(self, arg):
        ls = arg.strip().split('-')
        if len(ls) == 2:
            self.corpus.print_span(tuple(ls))
    def do_defmacro(self, arg):
        name, ls = arg.strip().split(' ', 1)
        self.macros[name] = ls.split('|')
    def do_macro(self, arg):
        for c in self.macros[arg]:
            print('>', c)
            self.onecmd(c)
    def do_stats(self, arg):
        self.corpus.stats()
    def do_quit(self, arg):
        return True
    def do_EOF(self, arg):
        print('')
        return self.do_quit('')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('book', action='store')
    parser.add_argument('-s', '--search', action='append')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('-p', '--print', action='store_true')
    parser.add_argument('-w', '--window', type=int, default=2)
    parser.add_argument('--width', type=int, default=0)
    parser.add_argument('--assign', action='store', default='')
    parser.add_argument('-c', '--count', action='store_true')
    parser.add_argument('--chapter', type=int, default=0)
    parser.add_argument('-r', '--review', type=str, default='')
    args = parser.parse_args()

    corpus = CorefCorpus(args.book)
    all_spans = list(corpus.ispans(unk_only=not (args.all or args.review)))
    if args.review:
        ls = []
        for sp in all_spans:
            if corpus.spans[sp] == args.review:
                ls.append(sp)
        all_spans = ls
    if args.width != 0:
        ls = []
        for sp in all_spans:
            sent, w1, w2 = corpus.parse_span(sp)
            if w2 - w1 + 1 == args.width:
                ls.append(sp)
        all_spans = ls
    if args.chapter != 0:
        ls = []
        for sp in all_spans:
            sent, w1, w2 = corpus.parse_span(sp)
            if f'-{args.chapter}:' in corpus.trees[sent][0]:
                ls.append(sp)
        all_spans = ls
    for s in args.search or []:
        col = -1
        key = s
        if ':' in s:
            col, key = s.split(':', 1)
            col = int(CONLL_COLUMNS.get(col, col))
        all_spans = corpus.search(key, all_spans, col)
    if args.count:
        print(len(all_spans))
    elif args.print:
        for sp in all_spans:
            corpus.print_span(sp, window=args.window)
        print(f'\n{len(all_spans)} results')
    elif args.assign:
        new_id = args.assign
        if new_id.endswith('?'):
            new_id = corpus.next_id(new_id.strip('?'))
        for sp in all_spans:
            corpus.update_span(sp, new_id, save=False)
        corpus.save()
        print(f'Assigned {len(all_spans)} spans to {new_id}')
    else:
        CorefCLI(corpus, all_spans=all_spans).cmdloop()
