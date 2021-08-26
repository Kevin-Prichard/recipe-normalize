#!/usr/bin/env python3

from collections import defaultdict as dd
import json
import logging
import re

from common import get_ingr_lines, ngrammer, tokenize_ingr_line
from common import (whitespace_parens_rx, wordlike_rx, numerics_rx, tags_rx,
                    brandname_rx, mark_r, mark_tm)

from nltk.corpus import wordnet as wn

logging.basicConfig()
logger = logging.getLogger(__name__)


def get_synsets_flattened(term, synsets=set()):
    # print(f"Checking {term}")
    thisset = set(wn.synsets(term))
    for syn in thisset:
        syn_word = syn.name().split(".")[0]
        if not syn_word in synsets:
            synsets.add(syn_word)
            get_synsets_flattened(syn_word, synsets)
    return synsets


def hypernym_collector():
    common_ancestors = dd(int)
    words_covered = set()

    lines = []
    with open("../ingrs_uniq.txt", "r") as fh:
         for line in fh.readlines():
             lines.append(line)

    lineptr = 0
    print(f"Lines {len(lines)}")
    for line in lines:
        lineptr += 1
        # if lineptr / 100 == int(lineptr / 100):
        #     print(f"{lineptr} / {len(lines)}")
        tokens = whitespace_parens_rx.split(line)
        for token in tokens:
            if not token or numerics_rx.match(token):
                continue
            if not wordlike_rx.match(token):
                logger.info("Unknown token: %s", token)
            if token in words_covered:
                continue
            # synsets = get_synsets_flattened(token)
            x = wn.synsets(token)
            pu.db
            synsets = set(sum(x, []))
            for syn in synsets:
                common_ancestors[syn] += 1
            words_covered.add(token)

    print(len(common_ancestors.keys()))
    print(json.dumps(common_ancestors, indent=4, sort_keys=True))


def pos_collector(nounify_unknowns=False, countdown=True):
    templates = dd(list)
    unknown = dd(int)

    lines = get_ingr_lines()

    lineptr = 0
    print(f"Lines {len(lines)}")
    for line in lines:
        line = line[:-1]
        lineptr += 1
        template = []
        while '<' in line:
            line = re.sub(tags_rx, line, '')
        if countdown and lineptr / 100 == int(lineptr / 100):
            print(f"{lineptr} / {len(lines)}")
        for token in tokenize_ingr_line(line, unknown):
            if token:
                template.append(token)
        if template and len(line) > 1:
            templates[" ".join(template)].append(line)

    print(json.dumps(templates, indent=4, sort_keys=True))
    unk_keys = sorted(unknown.keys())
    print(f"Unknown lexicon: ",
          ', '.join(f"{k}:{unknown[k]}" for k in unk_keys))
    tmpl_keys = templates.keys()
    print(len(templates.keys()))
    print("Templates with unknowns:", sum(1 for k in tmpl_keys if "-" in k))
    print("Templates w/o unknowns:", sum(1 for k in tmpl_keys if "-" not in k))


def find_brandname_phrases():
    freq_map = dd(int)
    lines = get_ingr_lines()
    unknown = dd(int)
    bn_count = 0
    overall_count = 0
    # import pudb; pu.db
    for line in lines:
        overall_count += 1
        if brandname_rx.match(line):
            bn_count += 1
            # import pudb; pu.db
            # if "betty crocker" in line.lower():  # "fruit roll ups" in line.lower() and
            #     import pudb; pu.db
            tokenized = [token for token in tokenize_ingr_line(
                line, unknown, substitute_pos=False, skip_brandnames=False)]
            ngrams = ngrammer(tokenized)
            for ngram in ngrams:
                freq_map[tuple(ngram)] += 1
            # freq_map[" ".join(ngram)] += 1
    print(f"Overall {overall_count}, brandname {bn_count}, {bn_count/overall_count}")
    return freq_map


def count_ngrams():
    freq_map = dd(int)
    lines = get_ingr_lines()
    unknown = dd(int)
    bn_count = 0
    overall_count = 0
    ach_rx = re.compile(f".*\Wh{mark_r}.*")
    from functools import reduce
    # import pudb; pu.db
    for line in lines:
        if not brandname_rx.match(line):
            continue
        # if "h®" in line:
        #    print(line[:-1])
        # if overall_count > 100:
        #     break
        overall_count += 1
        tokenized = [token for token in tokenize_ingr_line(
            line, unknown, substitute_pos=False, skip_brandnames=False)]
        ngrams = ngrammer(tokenized, keep_stopwords=True)
        for ngram in ngrams:
            freq_map[tuple(ngram)] += 1
        if brandname_rx.match(line):
            bn_count += 1
            # shortest_ng = reduce(ngram
    print(f"Overall {overall_count}, brandname {bn_count}, {bn_count/overall_count}")
    return freq_map


def fiddle():
    n = ngrammer(["abc", "def", "ghi", "jkl", "mno"])
    print(json.dumps(n))


if __name__ == '__main__':
    # pos_collector(nounify_unknowns=True, countdown=False)
    # freqs = find_brandname_phrases()
    # fiddle()

    freqs = count_ngrams()
    brands = set()
    for ngram, cnt in freqs.items():
        if len(ngram) == 1 and brandname_rx.match(ngram[0]):
            brands.add(ngram[0])

             # print(f"{freqs[ngram]}\t{ngram}")
    # for ngram, cnt in freqs.items():
    #     if brandname_rx.match(ngram):
    #         print(f"{cnt}\t{ngram}")
