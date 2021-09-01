#!/usr/bin/env python3

from collections import defaultdict as dd
from nltk.corpus import wordnet as wn
import json



"""
    {
        "key1": {
            "key11": {
                "key111": 123
            },
            "key12": {
                "key121": {
                    "key1211": 321
                },
                "key122": {
                    ...
                }
            },
        "key2": {
            ...
        }
    }

    {
        "name": "root",
        "children": [
            {
                "name": "key1",
                "children": [
                    {
                        "name": "key11":
                        "children": [
                            {
                                "name": "key111",
                                "value": 123
                            }
                        ],
                    },
                    {
                        "name": "key12",
                        "children": [
                        ]
                    }
                ]

"""

# next_nutree = nutree.get("children")
# if next_nutree is None:
#     nutree["children"] = next_nutree = {"name": key, "children": {}}


"""
def convert_ancestry_to_d3_hierarchy(tree, nutree):
    for key, subtree_or_value in tree.items():
        if key != 'value' and isinstance(subtree_or_value, dict):
            next_nutree = {"name": key, "children": []}
            nutree["children"].append(next_nutree)
            convert_ancestry_to_d3_hierarchy(subtree_or_value, next_nutree)
        elif key == 'value':
            nutree["value"] = subtree_or_value
            # nutree["children"].append({"name": key, "value": subtree_or_value})
        else:
            print(f"Error: {key}->{subtree_or_value}")




def convert_ancestry_to_d3_hierarchy(tree, nutree):
    for key, subtree_or_value in tree.items():
        # if "children" not in nutree:
        #     nutree["children"] = {}
        if key != '__value__' and isinstance(subtree_or_value, dict):
            next_nutree = {"name": key, "children": []}
            if "children" not in nutree:
                import pudb; pu.db
            nutree["children"].append(next_nutree)
            convert_ancestry_to_d3_hierarchy(subtree_or_value, next_nutree)
        elif key == '__value__':
            nutree["value"] = subtree_or_value
            del nutree["children"]
            # nutree["children"].append({"name": key, "value": subtree_or_value})
        else:
            print(f"Error: {key}->{subtree_or_value}")

"""

counts = dd(int)


def hn_visit(syn, ancestry=None, coll=None, depth=0):
    global counts
    hyns = syn.hypernyms()
    if hyns:
        for hyn in hyns:
            counts[hyn.name()] += 1
            ancestry.append(hyn.name())
            hn_visit(hyn, ancestry=ancestry, depth=depth + 1, coll=coll)
    else:
        if len(ancestry) > 2:
            mahnuthreads = [el for el in ancestry]
            mahnuthreads.reverse()
            coll.append(mahnuthreads)


def word_tree(word):
    set = wn.synsets(word)
    ancestries = []
    for term in set:
        hn_visit(term, ancestry=[word, str(term.name())], coll=ancestries)
    return ancestries


def word_ancestry_finder(word_gen):
    root = dict()
    c = 0
    for word in word_gen:
        c += 1
        ancestry = word_tree(word)
        for anc_line in ancestry:
            node = root
            for term in anc_line:
                term = term.split(".")[0]
                next_node = node.get(term)
                if next_node is None:
                    node[term] = next_node = dd(int)
                node = next_node
            node["__value__"] += 1
    return root


def convert_ancestry_to_d3_hierarchy(tree, nutree):
    if "children" not in nutree:
        nutree["children"] = []
    for key, subtree_or_value in tree.items():
        if key == '__value__':
            nutree["value"] = subtree_or_value
            del nutree["children"]
            break
        next_nutree = {"name": key, "children": []}
        nutree["children"].append(next_nutree)
        convert_ancestry_to_d3_hierarchy(subtree_or_value, next_nutree)


def main():
    def word_gen():
        words=["23", "twenty-four", "three", "hamburger",
               "carrot", "fresh", "chopped", "golden", "toasted"]
        for word in words:
            yield word

    root = word_ancestry_finder(word_gen())
    nuroot = {"name": "__root__", "children": []}
    convert_ancestry_to_d3_hierarchy(root, nuroot)
    return nuroot


if __name__ == "__main__":
    r = main()
    print(json.dumps(r, indent=2, sort_keys=True))
