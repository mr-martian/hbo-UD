#!/usr/bin/env python3

import utils
import cmd
from collections import defaultdict
import re

class CorefCLI(cmd.Cmd):
    prompt = '> '
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
        self.todo_spans = []
        self.cur_span = None
        self.cur_col = -1
        self.unk_only = True
        super().__init__()
        self.next_span()
    def ispans(self, unk_only=False):
        ls = self.spans.keys()
        if unk_only:
            ls = [s for s,i in self.spans.items() if i[0] == 'u']
        yield from sorted(ls, key=self.parse_span)
    def save(self):
        with open(f'coref/spans/{self.book}.txt', 'w') as fout:
            for sp in self.ispans():
                fout.write(f'{sp[0]}-{sp[1]} {self.spans[sp]}\n')
    def update_span(self, span, new_id, save=True):
        self.spans[span] = new_id
        self.span_ids[new_id[0]].add(new_id)
        if save:
            self.save()
    def next_span(self):
        self.cur_span = None
        if not self.todo_spans:
            self.todo_spans = [s for s in self.ispans() if self.spans[s][0] == 'u']
            if not self.todo_spans:
                print('No unknown spans remain. Search if you want to merge anything.')
                return
        self.cur_span = self.todo_spans[0]
        self.print_span(self.cur_span)
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
        print(f'{span[0]}-{span[1]} {self.spans[span]}')
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
                if comp(key, line.split('\t')[column]):
                    return True
        return False
    def search(self, key, column=-1):
        self.todo_spans = [s for s in self.ispans(self.unk_only) if self.matches(s, key, column)]
    def do_search(self, arg):
        key = arg
        if arg.startswith('/') and arg.endswith('/'):
            key = re.compile(arg.strip('/'))
        self.search(key, self.cur_col)
        print(len(list(self.ispans(self.unk_only))))
        print(f'{len(self.todo_spans)} results for "{arg}" in column {self.cur_col}')
        self.next_span()
    def do_setcol(self, arg):
        col_names = {
            'surf': 1,
            'lem': 2,
            'lemma': 2,
            'upos': 3,
            'xpos': 4,
        }
        if not arg:
            self.cur_col = -1
        elif arg.isdigit():
            self.cur_col = int(arg)-1
        elif arg.lower() in col_names:
            self.cur_col = col_names[arg.lower()]
        else:
            print(f'Unknown column {arg}')
    def do_new(self, arg):
        c = arg.strip()
        if len(c) != 1:
            print(f'ID type must be single character, not {c}')
        else:
            n = len(self.span_ids[c])+1
            while c+str(n) in self.span_ids[c]:
                n += 1
            self.cur_id = c + str(n)
            print(f'New ID: {self.cur_id}')
    def do_set(self, arg):
        if self.cur_span and arg:
            self.update_span(self.cur_span, arg)
            if self.todo_spans and self.todo_spans[0] == self.cur_span:
                self.todo_spans.pop(0)
        self.next_span()
    def do_setid(self, arg):
        self.cur_id = arg
    def do_yes(self, arg):
        self.do_set(self.cur_id)
    def do_yesall(self, arg):
        if self.cur_id:
            for sp in self.todo_spans:
                self.update_span(sp, self.cur_id, save=False)
                self.print_span(sp, window_only=True)
            self.save()
            self.todo_spans = []
            self.next_span()
    def do_no(self, arg):
        if self.todo_spans:
            self.todo_spans.pop(0)
        self.next_span()
    def do_y(self, arg):
        self.do_yes('')
    def do_n(self, arg):
        self.do_no('')
    def do_singletons(self, arg):
        self.todo_spans = [s for s in self.todo_spans if s[0] == s[1]]
        self.next_span()
    def do_fix(self, arg):
        ls = arg.split()
        sp = ls[0].split('-')
        if sp not in self.spans:
            print(f'Unknown span {sp}')
        elif len(ls) == 2:
            self.update_span(sp, ls[1])
    def replace_span(self, old, new):
        if new not in self.spans:
            self.spans[new] = self.spans[old]
        del self.spans[old]
    def replace_cur_span(self, sent, w1, w2):
        new_span = (f'{sent+1}:{w1}', f'{sent+1}:{w2}')
        self.replace_span(self.cur_span, new_span)
        if self.todo_spans[0] == self.cur_span:
            self.todo_spans[0] = new_span
        self.cur_span = new_span
        self.print_span(self.cur_span, window_only=True)
    def update_cur_span(self, w1shift, w2shift):
        if self.cur_span:
            sent, w1, w2 = self.parse_span(self.cur_span)
            w1 += w1shift
            w2 += w2shift
            if 1 <= w1 <= w2 <= self.tree_maps[sent]['len']:
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
    def do_shiftlast(self, arg):
        try:
            self.update_cur_span(0, int(arg))
        except:
            print(f'Invalid argument {arg}')
    def do_del(self, arg):
        if self.cur_span:
            del self.spans[self.cur_span]
            self.save()
            self.todo_spans.pop(0)
            self.next_span()
    def do_recent(self, arg):
        if self.cur_span:
            all_spans = list(self.ispans())
            idx = all_spans.index(self.cur_span)
            n = int(arg or '5')
            for i in range(max(idx-n, 0), idx):
                self.print_span(all_spans[i], window_only=True)
    def do_show(self, arg):
        ls = arg.split()
        if len(ls) == 2:
            self.print_span(tuple(ls))
    def do_quit(self, arg):
        return True
    def do_EOF(self, arg):
        print('')
        return self.do_quit('')

if __name__ == '__main__':
    import sys
    CorefCLI(sys.argv[1]).cmdloop()
