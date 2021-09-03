# recipe-normalize

### Synopsis

Circa September 1, this repo contains python experiments that are moving toward converting the relatively unstructured `ingredients` text records, found in recipe objects produced by [recipe-scrapers](https://github.com/hhursev/recipe-scrapers), into structured objects.

### Code notes

These files contain commented-out usage examples in their `if __name__ == "__main__` blocks-
- wordnet-exam.py 
- walk_hn.py

Not many guardrails, here, just a pile of experimental code aimed at understanding some of the ingredients texts. More work remains to be done in parsing number-like strings, adjectives, stemming, etc. The main result here was to identify the principal word nouns of an ingredient specification.

Upcoming work would be-
- 1.1 extract and convert numeric quantities into real numbers
- 1.2 identify units and measures
- 1.3 pair those quantities and measures
- 2.1 ignore or remove recipes containing trademarked product ingredients (because they're often unlinkable to word nouns/phrases from similar recipes that do not contain that product)
- 3.1 combine quantities+measures+food nouns to see whether they remain coherent as ingredient specifications

What's done in recipe-normalize
- common.py
  - IsAFood: True if word has one of several hypernyms
  - IsAWord - True if exists in wordnet 
  - gen_ingr_words(lines) -yield gen of word-like strings
  - gen_ingr_lines(filename) -yield gen of lines from file, html-stripped
  - ngrammer(str/list) -generate ngrams from str or list of str
  - DocGramme -attempt at tree of ngram length vs frequency
  - NGramTree/NGramTreeNode -like DocGramme, and unfinished

- syntree.py: a cli util displays the hypernyms of a word

- wordnet-exam.py:
  - brandname_lexicon -makes lexicon of words containing or ending with R or TM, but not included if also a generic food noun
  - flatten(toflatten) -yields nested lists into one flat generator
  - hypernym_collector -counts common ancestors across all ingr words
  - pos_collector -convert ingr lines to pos templates, to see the collapse
  - count_ngrams -count occurrences of ingr ngrams
  - inverted_hypernym_tree -collect ingr word hypernym trees, invert to shared root
  - word_food_histogram -categ ingr words to [food, word, unkown], writes to files, gens histogram and counts

- walk_hn.py:
  - convert_ancestry_to_d3_hierarchy -transform output of word_ancestry_finder to d3.hierarchy compatible data structure (with 'value' and 'children' entries)
  - word_ancestry_finder -produce dict tree of word-to-hypernym ancestry paths, with '__value__' int counts,
    uses word_tree+hn_visit to recurse the hypernym tree

- hier.html: d3js to display hyn hier from convert_ancestry_to_d3_hierarchy

- gitta_clean.py: replaces numeric-ish strings with "quant" in attempt to run gitta with fewer permutations

