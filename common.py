import nltk
import re
from typing import AnyStr, Union, List
nltk.download("stopwords")
from nltk.corpus import stopwords, wordnet as wn
import nltk
nltk.download('wordnet')


WORD_SPLIT = re.compile(r'\s+')
whitespace_parens_rx = re.compile(r"[ \t\n\r\-(),.;:\"?!@#$\^&*_=+]+")
wordlike_rx = re.compile(r"\w+")
numerics_rx = re.compile(r"[0-9/¼½¾⅓⅔⅛⅜⅝⅞.\-x+]+")  # \s*[0-9/¼½¾⅓⅔⅛⅜⅝⅞.\-x]+
tags_rx = re.compile(r'<[^<]+?>')
mark_r = "\u00ae"
mark_tm = "\u2122"
brandname_rx = re.compile(f".*[{mark_r}{mark_tm}].*")
hyp = lambda s: s.hypernyms()


def ngrammer(
        txt: Union[AnyStr, List],
        n_gram_length: int = 3,
        tokenize: bool = False,
        keep_stopwords: bool = False):
    # Strip HTML
    if tokenize:
        while '<' in txt:
            txt = re.sub(r'<[^<]+?>', '', txt)
        raw_tokens = WORD_SPLIT.split(txt)
    else:
        raw_tokens = txt

    useful_words = [
        word.lower()
        for word in raw_tokens
        if word not in stopwords.words('english') or keep_stopwords]

    min_n = 1
    max_n = 8
    uwlen = len(useful_words)
    n_grams = []
    for i in range(0, uwlen - max(0, uwlen - max_n - 1)):
            for L in range(min_n, max_n+1):
                if i + L - 1 < uwlen:
                    n_grams.append(useful_words[i:i + L])

    return n_grams


def get_ingr_lines():
    lines = []
    with open("ingrs_uniq.txt", "r") as fh:
        for line in fh.readlines():
            lines.append(line)
    return lines


def tokenize_ingr_line(line, unknown, posify_words=True, skip_brandnames=True):
    tokens = whitespace_parens_rx.split(line.lower())
    # import pudb; pu.db
    for token in tokens:
        if numerics_rx.match(token):
            yield '#'
        if not token.strip() or len(token.strip()) <= 1:
            continue
        elif skip_brandnames and (mark_r in token or mark_tm in token):
            yield '<TN>'
        elif not wordlike_rx.match(token):
            yield f"unk:{token}"
        else:
            if posify_words:
                wndef = wn.synsets(token)
                if wndef:
                    yield f"<{wndef[0].pos()}>"
                else:
                    unknown[token] += 1
                    yield f"<n>"
            else:
                yield token