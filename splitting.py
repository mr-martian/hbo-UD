#!/usr/bin/env python3

from tf.app import use
A = use("bhsa", hoist=globals())
#A.extract({'Torah':('Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy')}, overwrite=True)
for book in ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Ruth']:
    A.extract({book+'Book':(book,)}, overwrite=True)
