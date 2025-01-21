#!/bin/bash

grep sent_id temp/macula-merged/$1.conllu | nl | grep $2
