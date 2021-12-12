#!/usr/bin/env python3

import sys
from tf.app import use
A = use("bhsa", hoist=globals())
book = sys.argv[1]
if book[0].isnumeric():
    book = book[0] + ' ' + book[1]
book = book.capitalize()
A.extract({book+'Book':(book,)}, overwrite=True)
