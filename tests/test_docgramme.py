from recipe_normalize.common import DocGramme
from unittest import TestCase



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
        self.assertEquals(len(DocGramme.by_terms(("McCormick®",))), 3)

    def test__by_gram_search__returns_expected_docs(self):
        import pudb; pu.db
        result = DocGramme.by_term("McCormick®")
        d=1

    def test_fiddle(self):
        r = DocGramme.by_term("McCormick®")
        import pudb; pu.db
        d=1

