from collections import defaultdict as dd
import nltk
import re
from typing import AnyStr, Union, List, Tuple, Set
import typing as t
nltk.download("stopwords")
from nltk.corpus import stopwords, wordnet as wn
import nltk
nltk.download('wordnet')

from array import array
from simple_classproperty import classproperty


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


class T:
    def __init__(self, text):
        self._text = text
    def __hash__(self):
        return hash(self._text)
    def __eq__(self, other):
        if isinstance(other, T):
            return self._text == other._text
        return self._text == other
    def __str__(self):
        return f"T[{self._text}/{hash(self)}]"
    __repr__ = __str__


class Document:
    # Static properties
    _root = set()

    class GramNode:
        def __init__(self, gram_text, doc):
            self._gram_text = gram_text
            self._kids = set()
            self._docs = set()
            self._docs_count = 0
            self._kids_count = 0

        def __eq__(self, other):
            if isinstance(other, Document.GramNode):
                return self._gram_text == other._gram_text
            return self._gram_text == other

        def add(self, gram: 'GramNode', doc: 'Document'):
            self._kids.add(gram)
            self._docs.add(doc)
            self._kids_count += 1
            self._docs_count += 1
            return gram

        @property
        def child_count(self):
            return self._kids_count

        @property
        def doc_count(self):
            return self._kids_count

    def __init__(self, text, keep_stopwords=True):
        self._text = text
        self._keep_stopwords = keep_stopwords
        self._grams = dict()
        self._text_to_ngrams()

    def __hash__(self):
        return hash(self._text)

    def _text_to_ngrams(self):
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

        self._add_ngrams(useful_words)

    def _add_ngrams(self, terms: t.Sized[AnyStr], max_depth: int = 8):
        min_n = 1
        max_n = 8
        uwlen = len(terms)
        for word_num in range(0, uwlen):
            term = terms[word_num]
            gram = self._root[term]
            if not gram:
                gram = self.GramNode(term, self)
                self._root.add(gram)
            for length in range(min_n, max_n):
                if word_num + length < uwlen:
                    gram = gram.add(self.GramNode(terms[word_num + length], self))


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
            for L in range(min_n, max_n + 1):
                if i + L - 1 < uwlen:
                    ngram_ptr = tuple(self._local_gram_id[i:i + L])
                    self._register_ngram(ngram_ptr)
                    self._local_ngram_pos[ngram_ptr].add(i)

    def _register_ngram(self, ngram: Tuple[int]):
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
        maxdocs = dd(set)
        if word_id:
            for ngram in cls._gram_ngram_map.get(word_id, EMPTY_TUPLE):
                ngram_size = len(ngram)
                ngram_docs = cls._ngram_doc_map.get(ngram, EMPTY_SET)
                docs_having = len(ngram_docs)
                maxdocs[ngram_size]

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
            queue[token] = cls._ngram_doc_map.get((cls._word_id_map.get(token, False),), [])

        # Intersect the matching docs - doc must exist under all terms
        result = set()
        first_docset = True
        for docs in queue.values():
            docset = set(doc for doc, local_idx in docs)
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