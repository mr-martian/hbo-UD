#!/usr/bin/env python3

import collections
import logging
import re
import unicodedata

from udapi.block.ud.markbugs import MarkBugs

REQUIRED_FEATURE_FOR_UPOS = {
    'NOUN': ['Gender', 'Number'],
    'PROPN': ['Gender', 'Number'],
    'PRON': ['PronType'],
    'DET': ['PronType'],
    'ADJ': ['Number', 'Gender'],
    'NUM': ['NumType'],
    'VERB': ['VerbForm', 'HebBinyan'],
    'VERB_exist': ['VerbForm', 'Mood'],
}

class HebrewCheck(MarkBugs):
    """Block for checking suspicious/wrong constructions in Ancient Hebrew (hbo) UD v2.

    See ud.MarkBugs for documentation of the options of this block.
    """

    def is_distributive(self, node):
        if node.udeprel != 'parataxis':
            return False
        if node.lemma != 'אישׁ':
            return False
        if not all(c.udeprel in ['orphan', 'punct', 'conj'] for c in node.children):
            return False
        return True

    def process_node(self, node):
        form, udeprel, upos, feats = node.form, node.udeprel, node.upos, node.feats
        parent = node.parent

        if udeprel in ['parataxis'] and node.precedes(parent):
            if self.is_distributive(node):
                pass
            else:
                self.log(
                    node, udeprel+'-rightheaded',
                    udeprel+' relations should be left-headed, not right.')

        if udeprel in ['case'] and parent.precedes(node):
            self.log(node, udeprel+'-leftheaded',
                     udeprel+' relations should be right-headed, not left.')

        if upos == 'VERB' and node.lemma in ['ישׁ', 'אין']:
            upos = 'VERB_exist'
        for i_upos, i_feat_list in REQUIRED_FEATURE_FOR_UPOS.items():
            if upos == i_upos:
                for i_feat in i_feat_list:
                    if not feats[i_feat]:
                        self.log(node, upos+'-no-' + i_feat, 'upos=%s but %s feature is missing' % (upos, i_feat))

        if feats['VerbForm'] == 'Fin' and upos != 'VERB_exist':
            for i_feat in ['Mood', 'Number', 'Person']:
                if not feats[i_feat]:
                    self.log(node, 'finverb-no-' + i_feat, 'VerbForm=Fin but %s feature is missing' % i_feat)
            if feats['Person'] == '2' and not feats['Gender']:
                self.log(node, 'finverb-no-gender', 'VerbForm=Fin and Person=2 but Gender feature is missing')
            if feats['Person'] == '3' and feats['Number'] == 'Sing' and not feats['Gender']:
                self.log(node, 'finverb-no-gender', 'VerbForm=Fin and Person=3 and Number=Sing but Gender feature is missing')
            if feats['Mood'] == 'Ind' and not feats['Tense'] and not feats['Aspect']:
                self.log(node, 'finverb-no-tense-aspect', 'VerbForm=Fin but Tense/Aspect is missing')

        if feats['VerbForm'] == 'Part':
            for i_feat in ['Gender', 'Number']:
                if not feats[i_feat]:
                    self.log(node, 'partverb-no-' + i_feat, 'VerbForm=Part but %s feature is missing' % i_feat)

        if udeprel == 'case' and node.lemma == 'את':
            # it could in principle also be comitative,
            # but that's still not nsubj
            if parent.udeprel == 'nsubj':
                self.log(parent, 'acc-subj', 'Subjects should not have accusative marking.')
        if udeprel == 'case' and parent.feats['VerbForm'] == 'Fin':
            self.log(node, 'case-finverb', 'Prepositions should not attach to finite verbs. Maybe this should be acl:relcl or obj+xcomp?')

        if udeprel in ['obj', 'ccomp'] and parent.upos == 'AUX':
            self.log(node, 'aux-'+udeprel, f'AUX should not have dependent {udeprel}.')

    def after_process_document(self, document):
        total = 0
        message = 'HebrewCheck Error Overview:'
        for bug, count in sorted(self.stats.items(), key=lambda pair: (pair[1], pair[0])):
            total += count
            message += '\n%20s %10d' % (bug, count)
        message += '\n%20s %10d\n' % ('TOTAL', total)
        logging.warning(message)
        if self.save_stats:
            document.meta["bugs"] = message
        self.stats.clear()
