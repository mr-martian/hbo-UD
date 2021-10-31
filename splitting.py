#!/usr/bin/env python3

from tf.app import use
A = use("bhsa", mod="etcbc/trees/tf,etcbc/bridging/tf", hoist=globals())
A.extract({'Torah':('Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy')}, overwrite=True)