#!/bin/bash

cg-comp hbo.cg3 hbo.bin
./to-CG.py | grep -v IPython | grep -v 'This is' | grep -v 'Api reference' | grep -v 'features found' | grep -v '^$' | cg-conv -al | vislcg3 -g hbo.bin
