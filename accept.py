#!/usr/bin/env python3

import argparse
import utils

parser = argparse.ArgumentParser()
parser.add_argument('annotator', action='store')
parser.add_argument('book', action='store')
parser.add_argument('sent', type=int, nargs='+')
args = parser.parse_args()

utils.accept(args.book, args.annotator, args.sent)
