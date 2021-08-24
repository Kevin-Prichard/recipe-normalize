from collections import defaultdict as dd
from pymongo import MongoClient
from simple_classproperty import classproperty
import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords
import os
from threading import Thread, Lock
import logging
from logging import Logger
import re

from common import ngrams

mutex = Lock()
logging.basicConfig()
logger = logging.getLogger(__name__)


class RecipeConverter:
    _instance = None


    DATABASE_NAME = 'RecipeDB'
    COLL_NAME_QUEUE = 'queue'
    COLL_NAME_RECIPE = 'recipe'
    COLL_NAME_HISTORY = 'action'

    def __init__(self):
        # print("\n".join(str(kv) for kv in os.environ.items()))
        self.user = os.environ.get("MONGO_APP_USERNAME")
        self.passwd = os.environ.get("MONGO_APP_PASSWORD")
        self.host = os.environ.get("localhost")
        # self.conn_uri = f"mongo+srv://{self.user}:{self.passwd}@"
        # import pudb; pu.db
        self._mdb = MongoClient()
        self._ensure_existence()
        self._logger = None

    @classproperty
    def instance(cls) -> 'RecipeConverter':
        if cls._instance is None:
            mutex.acquire()
            try:
                # Why check twice? Multiple threads could can slip past the
                # first if, and we don't want the lock penalty on every
                if cls._instance is None:
                    cls._instance = cls()
            finally:
                mutex.release()
        return cls._instance

    def setLogger(self, logger: Logger):
        self._logger = logger

    def _ensure_existence(self):
        # Database
        self._db = self._mdb[self.DATABASE_NAME]

        # Collections
        self._queue = self._db[self.COLL_NAME_QUEUE]
        self._recipe = self._db[self.COLL_NAME_RECIPE]
        self._action = self._db[self.COLL_NAME_HISTORY]

    # INGR_REGEX = re.compile(r"^([0-9.⅓½⅔¼⅞/]+)\s+(\S+)\s+(.+)$")
    INGR_REGEX = re.compile(r"^(\S+)\s+(\S+)\s*(.*)$")

    def recipe_doc_gen(self):
        numbers = dd(int)
        measures = dd(int)
        foodstuffs = dd(int)
        ingredients = dd(int)
        ngrams = dd(int)
        ingr_log = open('ingrs.txt', 'w')
        for doc in self._recipe.find():
            if ('title' not in doc or
                'ingredients' not in doc or
                'instructions' not in doc or
                not doc['title'] or
                not doc['ingredients'] or
                not doc['instructions']):
                # print(f"Huh? {doc['canonical_url']}")
                continue
            else:
                if 'johnsonville' in doc['title'].lower():
                    continue
                for ingr in doc['ingredients']:
                    ingr_log.write(ingr)
                    ingr_log.write('\n')
                """
                for ingr in doc['ingredients']:
                    try:
                        for ngram in self.ngrams(ingr):
                            ngrams[" ".join(ngram)] += 1
                        ingredients[ingr] += 1
                        ingr_parts = self.INGR_REGEX.match(ingr).groups()
                        numbers[ingr_parts[0]] += 1
                        measures[ingr_parts[1]] += 1
                        foodstuffs[ingr_parts[2]] += 1
                    except BaseException as ee:
                        continue
                """

        ingr_log.close()
        """
        print(f"\nUnique ingr lines {len(ingredients.keys())}")
        print(f"Unique numbers {len(numbers.keys())}")
        print(f"Unique measures {len(measures.keys())}")
        print(f"Unique foodstuffs {len(foodstuffs.keys())}")

        print("\nNumerics\n", "\n".join(f"{cnt}\t{numerics}"
                                      for numerics, cnt in numbers.items()))
        print("\nMeasures\n", "\n".join(f"{cnt}\t{measure}"
                                    for measure, cnt in measures.items()))
        print("\nFoodstuffs\n", "\n".join(f"{cnt}\t{foodstuff}"
                                        for foodstuff, cnt in foodstuffs.items()))
        print("\nN-grams\n", "\n".join(f"{cnt}\t{ngram}"
                                       for ngram, cnt in ngrams.items()))
        """

    WORD_SPLIT = re.compile(r'\s+')

    def ngrams(self, txt):
        if '<' in txt:
            txt = re.sub(r'<[^<]+?>', '', txt)
        useful_words = [
            word.lower()
            for word in self.WORD_SPLIT.split(txt)
            if word not in (stopwords.words('english'))]

        n_grams = [useful_words[i:i + L + 1]
                   for L in range(max(len(useful_words), self.n_gram_length))
                   for i in range(len(useful_words) - self.n_gram_length)]
        return n_grams


if __name__ == '__main__':
    conv = RecipeConverter.instance
    x = conv.recipe_doc_gen()


"""
./video_noise_analysis/utils/ingest_noise_log.py
./video_noise_analysis/video_analysis/models.py
"""
