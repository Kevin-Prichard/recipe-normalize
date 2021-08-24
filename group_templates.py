#!/usr/bin/env python3

from collections import defaultdict as dd
import re

# https://colab.research.google.com/drive/1uD2tRUrXBtHm0YYWM7vuDivjacLq7K0G?usp=sharing#scrollTo=VTPQ4rUBy1Ky
# https://github.com/twinters/gitta


lines = dd(list)
split_rx = re.compile(r"\s+")
parens_rx = re.compile(r".*[\(\)].*")
with open("ingrs_uniq.txt", "r") as fh:
    for line in fh.readlines():
        parens = 1 if parens_rx.match(line) else -1
        parts = split_rx.split(line)
        lines[parens * len(parts)].append(line[:-1])

"""
    for line in fh.readlines():
        parens = 1 if "(" in line or ")" in line else -1
        parts = split_rx.split(line)
        lines[parens * len(parts)].append(line[:-1])
"""

for count in sorted(lines.keys()):
    print(f"\n{count}\n" + "=" * 80)
    print("\n".join(lines[count]))
