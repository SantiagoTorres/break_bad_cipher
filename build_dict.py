#!/usr/bin/env python
"""
    <name> 
        build_dict

    <description>
        builds a dictionary from a wordlist, and saves it to json
"""
import json
import sys

lengthdict = {}

if __name__ == "__main__":

    with open(sys.argv[1]) as fp:
        for line in fp:
            word = line.strip("\n")
            if len(word) not in lengthdict:
                lengthdict[len(word)] = []

            lengthdict[len(word)].append(word)

    with open("{}.dict.json".format(sys.argv[1]), 'wt') as fp:
        json.dump(lengthdict, fp)
