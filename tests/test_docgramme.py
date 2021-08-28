import sys

from recipe_normalize.common import DocGramme, Ngram
from unittest import TestCase
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)


doc_cocoa = '.563 cup unsweetened cocoa powder'
doc_lentils = '.66 cup <a href="https://www.allrecipes.com/gallery/red-lentil-recipes/" aria-label="red lentils">red lentils</a>'
doc_flour = '.66 cup all-purpose flour'
doc_yeast = "1 (.25 ounce) package dry active yeast (such as Fleischmann's® RapidRise Yeast)"
doc_marinade = '1 (0.71 ounce) package McCormick® Grill Mates® Montreal <a href="https://www.allrecipes.com/recipe/143809/best-steak-marinade-in-existence/" aria-label="Steak Marinade">Steak Marinade</a>, divided'
doc_gravy = "1 (.87 ounce) package McCormick® Onion Gravy Mix"
doc_dip = "1 (0.53 ounce) package McCormick® French Onion Dip Seasoning Mix"

all_docs = [doc_cocoa, doc_lentils, doc_flour, doc_yeast, doc_marinade, doc_gravy, doc_dip]


class TestDocGramme(TestCase):
    docset = [DocGramme(d) for d in all_docs]

    def beforeEach(self):
        self.docset = [DocGramme(d) for d in all_docs]

    def test_docgramme_creation_and_find_work(self):
        d = DocGramme(doc_marinade)
        self.assertEqual(DocGramme.by_terms(('package',)), set([d]))

    def test_that_multiple_docs_same_terms_work(self):
        import pudb; pu.db
        logger.info("KcKs %d", len(DocGramme.by_terms(("McCormick®",))))
        self.assertEqual(len(DocGramme.by_terms(("McCormick®",))), 3)

    def test__by_gram_search__returns_expected_docs(self):
        import pudb; pu.db
        result = DocGramme.by_term("McCormick®")
        d=1

    def test_fiddle(self):
        r = DocGramme.by_term("McCormick®")
        import pudb; pu.db
        d=1


class TestTTuple(TestCase):
    def test_that_ttuple_contains_works_for_sequences(self):
        test_tup = make_gram([1, 2, 3, 4, 5, 6, 7])
        test_sub = (4, 5, 6)
        self.assertEqual(3, whereis(test_tup, test_sub), "Failed on first")
        self.assertEqual(3, whereis(test_tup, test_sub), "Failed on second (state should be same")
        self.assertEqual(4, whereis(test_tup, (5, 6, 7)), "Failed on end")
        test_tup_len = len(test_tup)
        for i in range(test_tup_len):
            for o in range(i, test_tup_len):
                for p in range(o+1, test_tup_len-o):
                    self.assertEqual(o, whereis(test_tup, test_tup[o:p]), f"Failed at: i={i}, o={o}, p={p}\n")
