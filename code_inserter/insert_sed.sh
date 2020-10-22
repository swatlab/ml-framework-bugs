#!/bin/bash
git diff -U10000000000 --patience ${1:?First argument should be the pre version} ${2:-HEAD} ${3:+ -- $3}|sed -e '/^-\s/d' -e '/^+\s/i __X__PLACEHOLDER_FOR_BUG_TRACE__' -e 's/^\+ / /'
