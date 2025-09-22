#!/usr/bin/env python3

from collections import defaultdict
import unicodedata

def load_volume(vol, hoist):
    from tf.app import use
    import sys
    out = sys.stdout
    sys.stdout = open('blah.txt', 'w')
    if vol[0].isnumeric():
        v = vol[:2] + vol[2:].capitalize() + 'Book'
    else:
        v = vol.capitalize() + 'Book'
    use("ETCBC/bhsa:local", hoist=hoist, volume=v)
    sys.stdout.close()
    sys.stdout = out

def get_id(block):
    ls = block.splitlines()
    for ln in ls:
        if ln.startswith('# sent_id'):
            return ln.split()[-1]

def clean_ref(block):
    ls = block.splitlines()
    return '\n'.join(ln for ln in ls if not ln.startswith('# checker'))

def iter_conllu(fname):
    with open(fname) as fin:
        for block in fin.read().strip().split('\n\n'):
            if not block:
                continue
            yield get_id(block), block

def load_conllu(fname, clean=False):
    ret = {}
    for i, (n, b) in enumerate(iter_conllu(fname), 1):
        ret[n] = (i, clean_ref(b) if clean else b)
    return ret

def load_conllu_multi(fname):
    ret = defaultdict(list)
    for n, b in iter_conllu(fname):
        ret[n].append(b)
    return ret

def get_chapter(sid):
    def single(s):
        return int(s.split('-')[-1])
    p = sid.split(':')
    if len(p) == 2:
        return [single(p[0])]
    else:
        return [single(p[0]), single(p[1])]

def get_first_verse(sid):
    v1 = sid.split('-')[2]
    c, v = v1.split(':')
    return (int(c), int(v))

def split_lines(sent):
    head = []
    body = []
    for l in sent.strip().split('\n'):
        if l.startswith('#'):
            head.append(l)
        else:
            body.append(l)
    return head, body

def update_deps(old_sent, new_sent, old_headers=True):
    oh, ols = split_lines(old_sent)
    nh, nls = split_lines(new_sent)
    lines = oh if old_headers else nh
    if len(ols) != len(nls):
        return None
    for ol, nl in zip(ols, nls):
        ot = ol.split('\t')
        nt = nl.split('\t')
        if ot[0] != nt[0]:
            return None
        ot[6] = nt[6]
        ot[7] = nt[7]
        lines.append('\t'.join(ot))
    return '\n'.join(lines)

def get_cg(sent_id):
    book = sent_id.split('-')[1].lower()
    data = load_conllu(f'temp/merged/{book}.conllu')
    idx = data[sent_id][0]-1
    with open(f'temp/parsed-cg3/{book}.txt') as fin:
        return fin.read().split('\n\n')[idx]

def get_coref(book):
    with open(f'coref/spans/{book}.txt') as fin:
        for l in fin:
            ls = l.strip().split()
            if len(ls) != 2:
                continue
            yield (tuple(ls[0].split('-')), ls[1])

def iter_words(block):
    for ln in block.splitlines():
        ls = ln.strip().split('\t')
        if len(ls) == 10 and ls[0].isdigit():
            yield ls

def consonants_only(hbo):
    return ''.join(c for c in hbo if unicodedata.category(c) in ['Lo', 'Po', 'Zs', 'Pd'])

def grapheme_clusters(hbo):
    names = ['alef', 'bet', 'gimel', 'dalet', 'he', 'vav', 'zayin',
             'het', 'tet', 'yod', 'finkaf', 'kaf', 'lamed', 'finmem', 'mem',
             'finnun', 'nun', 'samekh', 'ayin', 'finpeh', 'peh',
             'fintsade', 'tsade', 'qof', 'resh', 'sin/shin', 'taf']
    vowels = ['sheva', 'hataf segol', 'hataf patah', 'hataf qamats',
              'hiriq', 'tsere', 'segol', 'patah', 'qamats', 'holam',
              'holam', 'qubuts']
    c = None
    d = False
    v = None
    for ch in hbo:
        cat = unicodedata.category(ch)
        if cat in ['Lo', 'Po', 'Pd', 'Zs']:
            if c:
                yield (c, d, v)
                c, d, v = None, False, None
            if cat == 'Lo':
                if ord(ch) == 0xfb2a:
                    c = 'shin'
                elif ord(ch) == 0xfb2b:
                    c = 'sin'
                else:
                    c = names[ord(ch) - 0x5d0]
            elif cat in ['Po', 'Pd']:
                yield ('punct', False, ch)
            elif cat == 'Zs':
                yield ('space', False, ch)
        elif cat == 'Mn':
            if ord(ch) < 0x5b0: # cantillation
                continue
            elif ord(ch) < 0x5bc:
                v = vowels[ord(ch) - 0x5b0]
            elif ord(ch) == 0x5bc:
                d = True
            elif ord(ch) == 0x5c1:
                if c == 'sin/shin':
                    c = 'shin'
            elif ord(ch) == 0x5c2:
                if c == 'sin/shin':
                    c = 'sin'
    if c:
        yield (c, d, v)

def transliterate_latex(hbo):
    name2latex = {
        'alef': "'", 'bet': 'b', 'gimel': 'g', 'dalet': 'd', 'he': 'h',
        'vav': 'w', 'zayin': 'z', 'het': '.h', 'tet': '.t', 'yod': 'y',
        'finkaf': 'K', 'kaf': 'k', 'lamed': 'l', 'finmem': 'M', 'mem': 'm',
        'finnun': 'N', 'nun': 'n', 'samekh': 's', 'ayin': '`',
        'finpeh': 'P', 'peh': 'p', 'fintsade': '.S', 'tsade': '.s',
        'qof': 'q', 'resh': 'r', 'sin/shin': '/s', 'sin': ',s',
        'shin': '+s', 'taf': 't',
        'sheva': ':', 'hataf segol': 'E:', 'hataf patah': 'a:',
        'hataf qamats': 'A:', 'hiriq': 'i', 'tsere': 'e', 'segol': 'E',
        'patah': 'a', 'qamats': 'A', 'holam': 'o', 'qubuts': 'u',
        None: '',
    }
    ret = r'\cjRL{'
    for c, d, v in grapheme_clusters(hbo):
        if c == 'space':
            ret += v
        elif c == 'punct':
            if ord(v) == 0x5c3:
                ret += ';'
            else:
                ret += ' '
        else:
            ret += name2latex[c]
            if d:
                ret += '*'
            if v:
                ret += name2latex[v]
    return ret + '}'

def transliterate_loc(hbo, latex):
    # TODO: qamats is sometimes "o" rather than "a"
    letters = {
        'gimel': 'g', 'dalet': 'd', 'he': 'h', 'zayin': 'z', 'yod': 'y',
        'lamed': 'l', 'finmem': 'm', 'mem': 'm', 'finnun': 'n', 'nun': 'n',
        'samekh': 's', 'fintsade': 'ts', 'tsade': 'ts', 'resh': 'r',
        'sin/shin': 'sh', 'shin': 'sh', 'taf': 't',
        'hataf segol': 'e', 'hataf patah': 'a',
        'hataf qamats': 'o', 'hiriq': 'i', 'tsere': 'e', 'segol': 'e',
        'patah': 'a', 'qamats': 'a', 'holam': 'o', 'qubuts': 'u',
    }
    if latex:
        letters.update({
            'alef': "'", 'vav': r'\d{v}', 'het': r'\d{h}', 'tet': r'\d{t}',
            'ayin': '`', 'qof': r'\d{k}', 'sin': r"\'{s}",
        })
    else:
        letters.update({
            'alef': 'ʼ', 'vav': 'ṿ', 'het': 'ḥ', 'tet': 'ṭ',
            'ayin': 'ʻ', 'qof': 'ḳ', 'sin': 'ś',
        })
    begedkefet = {
        'bet': ('v', 'b'), 'finkaf': ('kh', 'k'), 'kaf': ('kh', 'k'),
        'finpeh': ('f', 'p'), 'peh': ('f', 'p'),
    }
    ret = ''
    last_vowel_null = True
    last = (None, False, None)
    for c, d, v in grapheme_clusters(hbo):
        if c in ['space', 'punct']:
            ret += ' '
            last = (None, False, None)
            last_vowel_null = True
        elif c == 'yod' and not v:
            if last[2] == 'patah':
                ret += 'i'
        elif c == 'vav' and d:
            ret += 'u'
            last_vowel_null = False
        elif c == 'vav' and v == 'holam':
            ret += 'o'
            last_vowel_null = False
        elif c == 'vav' and not v and last[2] == 'holam':
            last_vowel_null = False
        else:
            if c in begedkefet:
                ret += begedkefet[c][int(last_vowel_null or d)]
            else:
                ret += letters[c]
            if v in letters:
                ret += letters[v]
                last_vowel_null = False
            elif v == 'sheva':
                if last_vowel_null:
                    ret += 'e'
                    last_vowel_null = False
                else:
                    last_vowel_null = True
        last = (c, d, v)
    return ret.strip()

def load_book_data(col):
    import csv
    with open('books.tsv', newline='') as fin:
        reader = csv.DictReader(fin, dialect='excel-tab')
        return {row['id']: row[col] for row in reader}

def feature_dict(s):
    if s == '_':
        return {}
    else:
        return dict(p.split('=', 1) for p in s.split('|'))

def conllu2display(book, block1, block2=None):
    word_offset = int(load_book_data('BHSA-start')[book])
    text = ''
    words = [['0', 'ROOT', 'ROOT', 'ROOT', 'ROOT', '', {}]]
    arcs = {}
    sent_id = ''
    for line in block1.splitlines():
        if line.startswith('# text'):
            text = line.split('=')[1].strip()
        elif line.startswith('# sent_id'):
            sent_id = line.split('=')[1].strip()
        elif not line.startswith('#'):
            break
    for word in iter_words(block1):
        d = feature_dict(word[5])
        d.update(feature_dict(word[9]))
        wid = d.get('Ref[BHSA]', '_')
        if wid.isdigit():
            wid = 'w' + str(int(wid)-word_offset)
        words.append([word[0], word[1], word[2], word[3],
                      d.get('Gloss', ''), wid, d])
        arcs[int(word[0])] = [(int(word[6].replace('_', '0')), word[7])]
    words.reverse()
    if block2:
        for word in iter_words(block2):
            arcs[int(word[0])].append((int(word[6].replace('_', '0')),
                                       word[7]))
    als = []
    for k, v in arcs.items():
        dep = len(words) - k - 1
        h0 = len(words) - v[0][0] - 1
        if v[0] == v[-1]:
            als.append({'head': h0, 'dep': dep, 'label': v[0][1],
                        'color': 'black', 'height': 0})
        else:
            h1 = len(words) - v[1][0] - 1
            als.append({'head': h0, 'dep': dep, 'label': v[0][1],
                        'color': 'green', 'height': 0})
            als.append({'head': h1, 'dep': dep, 'label': v[1][1],
                        'color': 'red', 'height': 0})
    def contains(big, little):
        bh, bd = big['head'], big['dep']
        lh, ld = little['head'], little['dep']
        if (bh, bd) == (ld, lh):
            return bh < lh
        elif (bh, bd) == (lh, ld):
            return big['color'] == 'green'
        elif (bh <= lh <= bd) and (bh <= ld <= bd):
            return True
        else:
            return (bd <= lh <= bh) and (bd <= ld <= bh)
    relevant = {}
    for i in range(len(als)):
        relevant[i] = [j for j in range(len(als))
                       if i != j and contains(als[i], als[j])]
    todo = list(relevant.keys())
    while todo:
        nt = []
        for t in todo:
            h = [als[i]['height'] for i in relevant[t]]
            if not h:
                als[t]['height'] = 1
            elif 0 not in h:
                als[t]['height'] = max(h) + 1
            else:
                nt.append(t)
        todo = nt
    return {'sent_id': sent_id, 'text': text, 'words': words, 'arcs': als,
            'height': max(h['height'] for h in als)}

def accept(book, annotator, ids):
    with open(f'temp/macula-merged/{book}.conllu') as fin:
        blocks = fin.read().strip().split('\n\n')
        with open(f'data/checked/{book}.conllu', 'a') as fout:
            for sent in ids:
                block = blocks[sent-1]
                written = False
                for ln in block.splitlines():
                    if ln[0] != '#' and not written:
                        fout.write(f'# checker = {annotator}\n')
                        written = True
                    fout.write(ln + '\n')
                fout.write('\n')

def show(book, idx, mode, wrange=None):
    if mode in ['cg', 'raw']:
        pr = '-parsed' if mode == 'cg' else ''
        with open(f'temp/macula{pr}-cg3/{book}.txt') as fin:
            cur = []
            i = -1 if mode == 'raw' else 0
            for line in fin:
                if not line.strip():
                    continue
                cur.append(line.rstrip())
                if '#1→' in cur[-1] or '#1->' in cur[-1]:
                    if i == idx:
                        return '\n'.join(cur[:-2])
                    else:
                        cur = cur[-2:]
                        i += 1
    gen = load_conllu(f'temp/macula-merged/{book}.conllu')
    sid = None
    for k in gen:
        if gen[k][0] == idx:
            sid = k
            break
    if not sid:
        return None
    if mode == 'conllu':
        return gen[sid][1]
    elif mode == 'ref':
        ref = load_conllu(f'data/checked/{book}.conllu', True)
        return ref.get(sid, (None, None))[1]
    elif mode == 'docs':
        block = gen[sid][1]
        ret = f'<!-- {book} {idx} -->\n'
        ret += '~~~ conllu\n'
        text = ''
        for line in block.splitlines():
            if line.startswith('# text ='):
                text = line[9:].strip()
            if line.count('\t') != 9:
                ret += line + '\n'
            else:
                ls = line.split('\t')
                if not ls[0].isdigit():
                    ls[9] = '_'
                else:
                    ls[9] = ls[9].replace(' ', '.')
                ret += '\t'.join(ls) + '\n'
        ret += '\n~~~\n'
        text = [l for l in block.splitlines() if l.startswith('# text')][0]
        text = text.split('=')[1].strip()
        ret += '\n_' + consonants_only(text) + '_\n\n'
        ret += '_' + transliterate_loc(text, False) + '_'
        return ret
    elif mode in ['latex', 'latexnp']:
        forms = []
        translit = []
        pos = []
        arcs = []
        block = gen[sid][1]
        words = list(reversed(list(iter_words(block))))
        if mode == 'latexnp':
            words = [w for w in words if w[3] != 'PUNCT']
        if wrange:
            words = [w for w in words if wrange[0] <= int(w[0]) <= wrange[1]]
        locs = {'0': 0}
        for h, w in enumerate(words, 1):
            locs[w[0]] = h
        for wid, ls in enumerate(words, 1):
            forms.append(transliterate_latex(ls[1]))
            translit.append(transliterate_loc(ls[1], True))
            pos.append(ls[3])
            head = locs.get(ls[6])
            if head is None:
                pass
            elif head == 0:
                arcs.append(f'\\deproot{{{wid}}}{{root}}')
            else:
                arcs.append(f'\\depedge{{{head}}}{{{wid}}}{{{ls[7]}}}')
        ret = f'% {book} {idx} {mode}'
        if wrange:
            ret += f' -w {wrange[0]}-{wrange[1]}'
        ret += '\n'
        ret += '\\begin{dependency}\n'
        ret += '  \\begin{deptext}\n'
        ret += '    ' + ' \\& '.join(forms) + ' \\\\\n'
        ret += '    ' + ' \\& '.join(translit) + ' \\\\\n'
        ret += '    ' + ' \\& '.join(pos) + ' \\\\\n'
        ret += '  \\end{deptext}\n'
        ret += '  ' + '\n  '.join(arcs) + '\n'
        ret += '\\end{dependency}\n'
        return ret

def get_cantillation(word):
    ret = []
    for c in word:
        n = unicodedata.name(c)
        if n.startswith('HEBREW ACCENT'):
            ret.append(n[14:].title().replace(' ', ''))
    return ret
