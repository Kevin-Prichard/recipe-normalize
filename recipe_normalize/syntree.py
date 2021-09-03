#!/usr/bin/env python3

import sys

from walk_hn import word_tree


if __name__ == "__main__":
    # Fetch, decompose a word's hypernym tree into one or more linear outputs
    print(sys.argv[1])
    for track in word_tree(sys.argv[1]):
        track.reverse()
        print("->".join(track))
