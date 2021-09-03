#!/usr/bin/env python3

import re
import sys

from common import get_ingr_lines


numbers_rx = re.compile(r"[0-9.]+[0-9]*[- ]?[0-9./¼½¾⅓⅔⅛⅜⅝⅞]+" r"|[0-9.]+")

"""
These account for 149 entries of ingrs_uniq.txt
    r"|(one|two|three|four|five|six|seven|eight|nine|ten"
    r"|eleven|twelve|thirteen|fourteen|fifteen|sixteen"
    r"|seventeen|eighteen|nineteen|twenty|thirty|forty"
    r"|fifty|sixty|seventy|eighty|ninty|ninety|hundred"
    r"|thousand"
    r")
"""


def gitta_prep(ingrs):
    for line in ingrs:
        if numbers_rx.match(line):
            line = line[:-1]
            new = numbers_rx.sub("quant", line)
            print(new.lower())


if __name__ == "__main__":
    data = get_ingr_lines(sys.argv[1])
    gitta_prep(data)
