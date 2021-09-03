#!/usr/bin/env python3

from common import get_ingr_lines
from gitta import grammar_induction
import json
import random
import sys
import time

random.seed(time.time())


lines = get_ingr_lines(sys.argv[1])
print(f"Lines {len(lines)}")

rg = grammar_induction.induce_grammar_using_template_trees(lines)
print(json.dumps(json.loads(rg.to_json()), indent=4))
