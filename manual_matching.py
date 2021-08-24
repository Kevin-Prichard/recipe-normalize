#!/usr/bin/env python3

from collections import defaultdict as dd
import json
import re

numerics = r"[0-9/¼½¾⅓⅔⅛⅜⅝⅞.\-]+\s*[0-9/¼½¾⅓⅔⅛⅜⅝⅞.\-]+"
whitespace = r"[ \t\n\r-]+"
whitespace_parens_rx = re.compile(r"[ \t\n\r-()]+")

token_rx = re.compile(f"({numerics})" + r"|(\w+)|\s+")
# numeric_rx = re.compile()

lines = []
commented_rx = re.compile(r"^\s*#")
with open("ingrs_uniq.txt", "r") as fh:
    for line in fh.readlines():
        if not commented_rx.match(line):
            lines.append(line)

print(f"Lines {len(lines)}")

wordhist = dd(int)
parts = set()
for L in lines:
    # tokens = token_rx.split(L)
    tokens = whitespace_parens_rx.split(L)
    for token in tokens:
        parts.add(token.lower())
    # print("*".join(tokens))

    # if not numeric_rx.match(tokens[1]):
    #     print(tokens[1].lower())
    #     # print("\t".join(tokens[1]))

print("\n".join(sorted(parts)))
