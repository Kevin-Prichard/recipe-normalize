#!/usr/bin/env python3

from gitta import grammar_induction
import json
import random
import re
import sys
import time
random.seed(time.time())

# https://colab.research.google.com/drive/1uD2tRUrXBtHm0YYWM7vuDivjacLq7K0G?usp=sharing#scrollTo=VTPQ4rUBy1Ky
# https://github.com/twinters/gitta


from common import get_ingr_lines
# lines = get_ingr_lines("mccormick.txt")
lines = get_ingr_lines(sys.argv[1])
print(f"Lines {len(lines)}")

import pudb; pu.db
rg = grammar_induction.induce_grammar_using_template_trees(lines)
print(json.dumps(json.loads(rg.to_json()), indent=4))
