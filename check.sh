#!/bin/bash

mkdir -p temp/check
touch temp/check/$1.old.txt
touch temp/check/$1.txt
mv temp/check/$1.txt temp/check/$1.old.txt
./check.py -m $1 > temp/check/$1.txt
ret=$?
cat temp/check/$1.txt
diff -U0 temp/check/$1.old.txt temp/check/$1.txt | dwdiff -uc
exit $ret
