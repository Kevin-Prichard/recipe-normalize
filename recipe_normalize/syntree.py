#!/usr/bin/env python3

from collections import defaultdict as dd
import json
import logging
import re
import sys

from walk_hn import counts
from walk_hn import word_ancestry_finder, convert_ancestry_to_d3_hierarchy
from walk_hn import word_tree
from common import get_ingr_lines, ngrammer, tokenize_ingr_line
from common import (whitespace_parens_rx, wordlike_rx, numerics_rx, tags_rx,
                    brandname_rx, mark_r, mark_tm,
                    gen_ingr_words, gen_ingr_lines, IsAFood)

from nltk.corpus import wordnet as wn

logging.basicConfig()
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    print(sys.argv[1])
    for track in word_tree(sys.argv[1]):
        track.reverse()
        print("->".join(track))
