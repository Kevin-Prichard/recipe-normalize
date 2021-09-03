#!/usr/bin/env python3

from collections import defaultdict as dd
import json
import logging
import re

from walk_hn import word_ancestry_finder, convert_ancestry_to_d3_hierarchy
from common import get_ingr_lines, ngrammer, tokenize_ingr_line
from common import (
    whitespace_parens_rx,
    wordlike_rx,
    numerics_rx,
    tags_rx,
    brandname_rx,
    brandname_strip_rx,
    gen_ingr_words,
    gen_ingr_lines,
    IsAFood,
    IsAWord,
)

from nltk.corpus import wordnet as wn

logging.basicConfig()
logger = logging.getLogger(__name__)

POS = {
    "n": "NOUN",
    "v": "VERB",
    "a": "ADJECTIVE",
    "s": "ADJECTIVE",
    "r": "ADVERB",
}


def wnname(synname):
    return synname.name().split(".")[0]


def flatten(toflatten):
    for element in toflatten:
        if isinstance(element, list):
            yield from flatten(element)
        else:
            yield element


def get_synsets_flattened(term, synsets=None):
    synsets = set() if synsets is None else synsets
    thisset = set(wn.synsets(term))
    for syn in thisset:
        syn_word = syn.name().split(".")[0]
        if syn_word not in synsets:
            synsets.add(syn_word)
            get_synsets_flattened(syn_word, synsets)
    return synsets


def hypernym_collector(lines):
    comanc = dd(lambda: dd(int))
    words_covered = set()

    lineptr = 0
    print(f"Lines {len(lines)}")
    for line in lines:
        lineptr += 1
        tokens = whitespace_parens_rx.split(line)
        for token in tokens:
            if not token or numerics_rx.match(token):
                continue
            if not wordlike_rx.match(token):
                logger.info("Unknown token: %s", token)
            if token in words_covered:
                continue
            x = wn.synsets(token)
            synsets = set(flatten(x))

            for syn in synsets:
                hn = syn.hypernyms()
                for idx, hyper in enumerate(hn):
                    comanc[POS[syn.pos()]][wnname(hyper)] += 1
            words_covered.add(token)

    print(len(comanc.keys()))
    print(
        "\n".join(
            f"{c}\t{k1}\t{k2}"
            for k1, sub in comanc.items()
            for k2, c in sub.items()
        )
    )


def pos_collector(countdown=True):
    templates = dd(list)
    unknown = dd(int)

    lines = get_ingr_lines()

    lineptr = 0
    print(f"Lines {len(lines)}")
    for line in lines:
        line = line[:-1]
        lineptr += 1
        template = []
        while "<" in line:
            line = re.sub(tags_rx, line, "")
        if countdown and lineptr / 100 == int(lineptr / 100):
            print(f"{lineptr} / {len(lines)}")
        for token in tokenize_ingr_line(line, unknown):
            if token:
                template.append(token)
        if template and len(line) > 1:
            templates[" ".join(template)].append(line)

    print(json.dumps(templates, indent=4, sort_keys=True))
    unk_keys = sorted(unknown.keys())
    print(
        "Unknown lexicon: ", ", ".join(f"{k}:{unknown[k]}" for k in unk_keys)
    )
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
    for line in lines:
        overall_count += 1
        if brandname_rx.match(line):
            bn_count += 1
            tokenized = [
                token
                for token in tokenize_ingr_line(
                    line, unknown, substitute_pos=False, skip_brandnames=False
                )
            ]
            ngrams = ngrammer(tokenized)
            for ngram in ngrams:
                freq_map[tuple(ngram)] += 1
    print(
        f"Overall {overall_count}, brandname {bn_count}, "
        f"{bn_count/overall_count}"
    )
    return freq_map


def count_ngrams(fn):
    freq_map = dd(int)
    lines = get_ingr_lines(fn)
    unknown = dd(int)
    bn_count = 0
    overall_count = 0

    for line in lines:
        if not brandname_rx.match(line):
            continue
        overall_count += 1
        tokenized = [
            token
            for token in tokenize_ingr_line(
                line, unknown, substitute_pos=False, skip_brandnames=False
            )
        ]
        ngrams = ngrammer(tokenized, keep_stopwords=True)
        for ngram in ngrams:
            freq_map[tuple(ngram)] += 1
        if brandname_rx.match(line):
            bn_count += 1
    print(
        f"Overall {overall_count}, brandname {bn_count}, "
        f"{bn_count/overall_count}"
    )
    return freq_map


def fiddle():
    n = ngrammer(["abc", "def", "ghi", "jkl", "mno"])
    print(json.dumps(n))


def inverted_hypernym_tree(fn):
    r = word_ancestry_finder(gen_ingr_words(gen_ingr_lines(fn)))
    tree = {"name": "__root__", "children": []}
    convert_ancestry_to_d3_hierarchy(r, tree)
    print(json.dumps(tree, indent=2, sort_keys=True))


def word_food_histogram(
    input_fn="ingrs_uniq_dequantified.txt",
    uniq_food_out_fn="uniq_food.txt",
    uniq_nonfood_out_fn="uniq_nonfood.txt",
    uniq_unknown_out_fn="uniq_unknown.txt",
    more_food_hypernyms=None,
):
    isafood = IsAFood(more_food_hypernyms)
    isaword = IsAWord()
    line_words_histo = dd(int)
    line_foods_histo = dd(int)
    line_unknown_histo = dd(int)
    line_count = 0
    word_count = 0
    nonfood_count = 0
    food_count = 0
    unknown_count = 0
    uniq_nonfood = set()
    uniq_food = set()
    uniq_unknown = set()
    for line in gen_ingr_lines(input_fn):
        line_count += 1
        line_word_count = 0
        line_food_count = 0
        line_unknown_count = 0
        for word in gen_ingr_words([line]):
            word_count += 1
            line_word_count += 1
            if word in isafood:
                uniq_food.add(word)
                food_count += 1
                line_food_count += 1
            elif word in isaword:
                nonfood_count += 1
                uniq_nonfood.add(word)
            else:
                uniq_unknown.add(word)
                unknown_count += 1
                line_unknown_count += 1
        line_words_histo[line_word_count] += 1
        line_foods_histo[line_food_count] += 1
        line_unknown_histo[line_unknown_count] += 1

    uniq_all = len(uniq_nonfood) + len(uniq_food) + len(uniq_unknown)
    print(f"Ingr lines unique: {line_count}")
    print(
        f"All words: {word_count}, "
        f"Food words: {food_count}, "
        f"Food% {int(food_count/word_count*10000)/100}%, "
        f"Nonfood words: {nonfood_count}, "
        f"Nonwords: {unknown_count}, "
        f"Nonwords% {int(unknown_count/word_count*10000)/100}%"
    )
    print(
        f"Unique words- "
        f"All: {uniq_all}, "
        f"Nonfood: {len(uniq_nonfood)}, "
        f"Food: {len(uniq_food)}, "
        f"Food% "
        f"{int(len(uniq_food)/max(1, uniq_all)*10000)/100}%, "
        f"Nonword: {len(uniq_unknown)}, "
        f"Nonword% "
        f"{int(len(uniq_unknown)/max(1, uniq_all)*10000)/100}%"
    )
    print("== Dictionary words Per Line Histo ==")
    for wpl in sorted(line_words_histo.keys()):
        print(f"{wpl}\t{line_words_histo[wpl]}")
    print("== Food words Per Line Histo ==")
    for fpl in sorted(line_foods_histo.keys()):
        print(f"{fpl}\t{line_foods_histo[fpl]}")
    print("== Unknown words Per Line Histo ==")
    for fpl in sorted(line_unknown_histo.keys()):
        print(f"{fpl}\t{line_unknown_histo[fpl]}")
    foods = "\n".join(sorted(uniq_food))
    words = "\n".join(sorted(uniq_nonfood))
    unknown = "\n".join(sorted(uniq_unknown))
    with open(uniq_food_out_fn, "w") as fh:
        fh.write(foods)
    with open(uniq_nonfood_out_fn, "w") as fh:
        fh.write(words)
    with open(uniq_unknown_out_fn, "w") as fh:
        fh.write(unknown)


def brandname_lexicon(input_fn="ingrs_uniq_dequantified.txt"):
    line_count = 0
    isafood = IsAFood(
        match_hypernyms=[
            "food.n.01",
            "food.n.02",
            "organism.n.01",
            "plant_part.n.01",
            "living_thing.n.01",
        ]
    )
    lex = set()
    for line in gen_ingr_lines(input_fn):
        line_count += 1
        for word in gen_ingr_words([line.lower()]):
            brandname_match = brandname_strip_rx.match(word)
            if brandname_match:
                brand_word = brandname_match.group(1)
                if brand_word not in isafood:
                    lex.add(brand_word)
    with open("brandname_lexicon.txt", "w") as fh:
        fh.write("\n".join(sorted(lex)))
    return lex


if __name__ == "__main__":

    """
    # The list of experiments and their invocation-

    # 1. Templatize ingredients lines by replacing each word with its EN pos
    pos_collector(nounify_unknowns=True, countdown=False)

    # 2. For ingr having brandnames, generate n-gram frequencies
    freqs = find_brandname_phrases()

    # 3. Just dump hypernyms of words to see what it looks like
    lines = get_ingr_lines(sys.argv[1])
    hypernym_collector(lines)

    # 4. Search one particular brand name to see what its ngrams look like
    freqs = count_ngrams("mccormick.txt")
    brands = set()
    for ngram, cnt in freqs.items():
        print(f"{cnt}\t{ngram}")

    # 5. Generate inverted hypernym tree in the d3.hierarchy() display format
    inverted_hypernym_tree("ingrs_uniq_dequantified.txt")

    # 6. A rough sketch towards #5
    r = word_ancestry_finder(gen_ingr_words(
        gen_ingr_lines("ingrs_uniq_dequantified.txt")))
    print(json.dumps(counts, indent=2, sort_keys=True))
    """

    # Search for all word-like strings with R or TM appended, strip, lexify
    brandname_lexicon()

    """
    # 7. Lookup ingredient words in wordnet, determine if food or nonfood
    # or unknown word (typos, brandnames), then write to those 3 files,
    # and gen histograms of each.
    food_hyn = [
        'food.n.01', 'food.n.02', 'organism.n.01', 'plant_part.n.01',
        'living_thing.n.01',
    ]
    fn_suffix = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    word_food_histogram(#"uniq_word2.txt",
                        uniq_food_out_fn=f"uniq_food_{fn_suffix}.txt",
                        uniq_nonfood_out_fn=f"uniq_nonfood_{fn_suffix}.txt",
                        uniq_unknown_out_fn=f"uniq_unknown_{fn_suffix}.txt",
                        more_food_hypernyms=food_hyn)

    """
