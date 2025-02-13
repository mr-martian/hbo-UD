#!/bin/bash

book=$1

mkdir -p to_check
rm -f to_check/*.html

function td() {
    ./tree-diff.py $1 $3
    prev=`echo "$2 - 1" | bc`
    next=`echo "$2 + 1" | bc`
    cat index.html | \
	sed "s|<p>|<p><a href=\"s$prev.html\">previous</a> |g" | \
	sed "s|</p>| <a href=\"s$next.html\">next</a></p>|g" \
	    > to_check/s$2.html
}
export -f td

grep index data/checkable/$book.conllu | \
    sed 's/.*= //g' | \
    nl -w1 -s" " | \
    xargs -n2 bash -c 'td "$@"' _ $book
