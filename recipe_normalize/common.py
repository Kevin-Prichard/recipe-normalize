from collections import defaultdict as dd
import nltk
import re
from typing import AnyStr, Union, List, Tuple, Set
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


class DocGramme:
    # Index of wordlike strings pointing to
    _word_reg = dict()
    _word_reg_last_id = 1
    _gram_reg = dd(list)  # List[Tuple['DocGramme', int]])

    def __init__(self, text, keep_stopwords=True):
        self._text = text
        self._1grams = array('H')
        self._grams = dict()
        self.keep_stopwords = keep_stopwords
        self._ingest_doc()

    def __hash__(self):
        return hash(tuple(self._1grams))

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
            if word not in stopwords.words('english') or self.keep_stopwords]

        # Turn tokens into word IDs
        for token in useful_words:
            self._1grams.append(self._register_word(token))

        # Produce and register ngrams
        self._ngramify()

    def _ngramify(self):
        # Generate ngrams using word IDs
        # Also locally indexes ngrams, but unsure if that'll be useful (global index provides same, but across docs)
        min_n = 1
        max_n = 8
        uwlen = len(self._1grams)
        for i in range(0, uwlen - max(0, uwlen - max_n - 1)):
            for L in range(min_n, max_n + 1):
                if i + L - 1 < uwlen:
                    ngram_ptr = tuple(self._1grams[i:i + L])
                    self._register_gram(ngram_ptr, i)
                    x = self._grams.get(ngram_ptr, None)
                    if x is not None:
                        import pudb; pu.db
                        raise Exception(f"Well that was weird: {ngram_ptr} in {self._text} double-existed")
                    self._grams[ngram_ptr] = i

    def _register_gram(self, ngram, local_idx):
        self._gram_reg[ngram].append((self, local_idx))

    def _register_word(self, token) -> int:
        tid = self._word_reg.get(token, None)
        if tid is None:
            self._word_reg[token] = tid = self._word_reg_last_id
            self._word_reg_last_id += 1
        return tid

    """
    Class Interface:
        find(token): List[DocGramme]
        by_ngram(ngram): array[Tuple[int]]
        by_text(text)
    """

    @classmethod
    def by_ngram(cls, ngram):
        return cls._gram_reg.get(ngram, None)

    @classmethod
    def by_terms(cls, tokens: Tuple[AnyStr]) -> Set['DocGramme']:
        # This is an and query
        queue = dict()
        for token in tokens:
            queue[token] = cls._gram_reg.get((cls._word_reg.get(token, False),), [])

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