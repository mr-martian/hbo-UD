#!/bin/bash

# ensure the output directory exists
mkdir -p coref/base
# ensure the conllu files exist
./export.py genesis 1-50 > coref/base/genesis.conllu
./export.py ruth 1-4 > coref/base/ruth.conllu
# dump all spans to stdout
./export_spans.py genesis ruth
