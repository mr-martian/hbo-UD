from udapi.core.block import Block
from udapi.core.coref import CorefMention, CorefEntity, store_coref_to_misc
import logging

class ImportSpans(Block):
    """Load and convert entity spans."""

    def process_start(self):
        self.type_conv = {
            'p': 'person',
            't': 'time',
            'i': 'object',
            'l': 'place',
            'n': 'organization',
            'a': 'abstract',
            'c': 'animal',
            'v': 'plant',
            'e': 'event',
            's': 'substance',
        }

    def add_entity(self, doc, eid):
        if eid not in doc.eid_to_entity:
            doc.create_coref_entity(eid,
                                    self.type_conv.get(eid[0], 'other'))
        return doc.eid_to_entity[eid]

    def get_range(self, tree, w1, w2):
        ret = []
        for w in tree.descendants:
            if isinstance(w.ord, int) and int(w1) <= w.ord <= int(w2):
                ret.append(w)
        return ret

    def process_tree(self, tree):
        clines = (tree.comment or '').splitlines()
        spans = []
        for l in clines:
            if l.startswith(' coref_spans'):
                spans += l.split('=')[1].split()
        for span in spans:
            w1, w2, eid = span.split('-')
            w1, w2 = int(w1), int(w2)
            words = self.get_range(tree, w1, w2)
            ent = self.add_entity(tree.document, eid)
            mention = CorefMention(words, entity=ent,
                                   add_word_backlinks=True)
        tree.comment = '\n'.join(l for l in clines
                                 if not l.startswith(' coref_spans'))

    def after_process_document(self, doc):
        store_coref_to_misc(doc)
