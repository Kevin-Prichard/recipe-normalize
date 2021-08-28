from collections import defaultdict as dd
import nltk
import re
from typing import AnyStr, Union, List, Tuple, Set, Sequence
nltk.download("stopwords")
from nltk.corpus import stopwords, wordnet as wn
import nltk
nltk.download('wordnet')

from array import array
from simple_classproperty import classproperty

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

WORD_SPLIT = re.compile(r'\s+')
HTML_TAG_RX = re.compile(r'<[^<]+?>')
whitespace_parens_rx = re.compile(r"[ \t\n\r(),.;:\"?!@#$\^&*_=+]+")
wordlike_rx = re.compile(r"\w+")
numerics_rx = re.compile(r"[0-9/¼½¾⅓⅔⅛⅜⅝⅞.\-x+]+")  # \s*[0-9/¼½¾⅓⅔⅛⅜⅝⅞.\-x]+
tags_rx = re.compile(r'<[^<]+?>')
mark_r = "\u00ae"
mark_tm = "\u2122"
brandname_rx = re.compile(f".*[{mark_r}{mark_tm}].*")
hyp = lambda s: s.hypernyms()
EMPTY_SET = set()
EMPTY_TUPLE = tuple()
EMPTY_LIST = list()


# https://www.youtube.com/watch?v=ahkBExnJjdA
# https://www.youtube.com/watch?v=In2f9-JQNqs

class Ngram:
    def __init__(self, seq: Sequence):
        self._tup = tuple(seq)
        self._kids = []

    def __iter__(self):
        return self._tup.__iter__()

    def __hash__(self):
        return hash(self._tup)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        return " ".join(DocGramme.get_word(wid) for wid in self._tup)

    __repr__ = __str__

    def add_child(self, child):
        self._kids.append(child)

    def whereis(self, other):
        if not isinstance(other, Sequence):
            return other in self._tup
        self_len = len(self._tup)
        other_len = len(other)
        self_ptr = 0
        other_ptr = 0
        while self_ptr < self_len and other_ptr < other_len and (self_ptr + other_len <= self_len):
            if other[other_ptr] == self._tup[self_ptr + other_ptr]:
                other_ptr += 1
            else:
                other_ptr = 0
                self_ptr += 1
        return self_ptr if other_ptr == other_len else None


class DocGramme:
    # Index of wordlike strings pointing to
    _gram_ngram_map = dd(set)
    _ngram_doc_map = dd(set)  # List[Tuple['DocGramme', int]])
    _word_id_map = dict()
    _word_last_id = 1

    def __init__(self, text, keep_stopwords=True):
        self._text = text
        self._local_gram_id = array('H')
        self._local_ngram_pos = dd(set)
        self._keep_stopwords = keep_stopwords
        self._ingest_doc()

    @classmethod
    def get_word(cls, word_id):
        logger.warning(word_id)
        return cls._word_id_map.get(word_id, "??")

    def __hash__(self):
        return hash(tuple(self._local_gram_id))

    def _ingest_doc(self):

        # Remove HTML tags prior to tokenizing
        while '<' in self._text:
            self._text = re.sub(HTML_TAG_RX, '', self._text)

        # Everything wordlike is a token
        raw_tokens = WORD_SPLIT.split(self._text)

        # Remove noise words, if required
        useful_words = [
            word.lower()
            for word in raw_tokens
            if word not in stopwords.words('english') or self._keep_stopwords]

        # Turn tokens into word IDs
        for token in useful_words:
            self._local_gram_id.append(self._register_word(token))

        # Produce and register ngrams
        self._ngramify()

    def _ngramify(self):
        # Generate ngrams using word IDs
        # Also locally indexes ngrams, but unsure if that'll be useful (global index provides same, but across docs)
        min_n = 1
        max_n = 8
        uwlen = len(self._local_gram_id)
        for i in range(0, uwlen - max(0, uwlen - max_n - 1)):
            last_gram = None
            for L in range(min_n, max_n + 1):
                if i + L - 1 < uwlen:
                    ngram = Ngram(self._local_gram_id[i:i + L])
                    self._register_ngram(ngram)
                    self._local_ngram_pos[ngram].add(i)
                    if last_gram:
                        last_gram.add_child(ngram)
                    last_gram = ngram

    def _register_ngram(self, ngram: Ngram):
        self._ngram_doc_map[ngram].add(self)
        for gram in ngram:
            self._gram_ngram_map[gram].add(ngram)

    def _register_word(self, token: AnyStr) -> int:
        tid = self._word_id_map.get(token, None)
        if tid is None:
            self._word_id_map[token] = tid = self._word_last_id
            self._word_last_id += 1
        return tid

    @classmethod
    def by_ngram(cls, ngram: Tuple[int]):
        return cls._ngram_doc_map.get(ngram, None)

    @classmethod
    def reconstitute(cls, ngram: Tuple[int], delim: AnyStr = ' ') -> AnyStr:
        return delim.join(cls._word_id_map.get(gram, "??") for gram in ngram)

    @classmethod
    def longest_contiguous_common_ngrams(cls, gram: AnyStr) -> Set[tuple]:
        word_id = cls._word_id_map.get(gram, None)
        if word_id:
            for ngram in cls._gram_ngram_map.get(word_id, EMPTY_TUPLE):
                L = len(ngram)
                P = len(cls._ngram_doc_map.get(ngram))
                # unfinished

    @classmethod
    def by_term(cls, gram: AnyStr) -> Set['DocGramme']:
        docset = set()
        word_id = cls._word_id_map.get(gram.lower(), None)
        if word_id:
            ngrams = cls._gram_ngram_map.get(word_id, EMPTY_SET)
            for ngram in ngrams:
                docset.update(cls._ngram_doc_map.get(ngram, set()))
        return docset

    @classmethod
    def by_terms(cls, tokens: Tuple[AnyStr]) -> Set['DocGramme']:
        # This is an and query
        queue = dict()
        for token in tokens:
            token = token.lower()
            queue[token] = cls._ngram_doc_map.get((cls._word_id_map.get(token, False),), [])

        # Intersect the matching docs - doc must exist under all terms
        result = set()
        first_docset = True
        for docset in queue.values():
            if first_docset:
                result = docset
            else:
                result.intersection_update(docset)
        return result


"""
text: original text
grams: List[AnyStr] - the 1-grams, in order. Serves as an index to this Line's ngrams
maxgram = max number of ngrams

"""


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
    with open("../ingrs_uniq.txt", "r") as fh:
        for line in fh.readlines():
            while '<' in line:
                line = re.sub(r'<[^<]+?>', '', line)
            lines.append(line)
    return lines


def tokenize_ingr_line(line, unknown:List[AnyStr]=None, substitute_pos=True, skip_brandnames=True):
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
            if substitute_pos:
                wndef = wn.synsets(token)
                if wndef:
                    yield f"<{wndef[0].pos()}>"
                elif unknown is not None:
                    unknown[token] += 1
                    yield f"<n>"
            else:
                yield token