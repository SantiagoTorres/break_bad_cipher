#!/usr/bin/env python3
"""
    <name>
        crack

    <description>
        Tries to crack a ciphertext using different approaches to cracking

    <usage>
        crack <file>

    <output>
        Will output status messages and the result, if found
"""
import json
import re
import copy
import sys
from encrypt import cipher_to_words, decrypt
from letter_frequency import LETTER_FREQUENCIES, LETTER_TOTAL

#DEFAUT_DICTIONARY = 'dict_full.txt.dict.json'
DEFAUT_DICTIONARY = 'english_words.txt.dict.json'
#DEFAUT_DICTIONARY = 'target_pt.dict.json'
DEBUG = False

interactive_key = None

class InteractiveKey:
    """
    <name>
        InteractiveKey

    <descritption>
        Defines a key that can be dynamically upated with new values
        will automatically check if the possible key values have been overflown
    """

    key = None
    tempkey = None
    tempcount = None
    count = None

    def __init__(self, oldkey, oldcount = None):

        if oldcount:
            self.count = oldcount

        if oldkey:
            self.key = copy.deepcopy(oldkey)
            self.tempkey = {x:set() for x in self.key}
            return 

        self.key = {}
        self.tempkey = {}
        self.count = 0
        self.tempcount = 0
        for char in LETTER_FREQUENCIES:
            self.key[char] = set()
            self.tempkey[char] = set()

    def add_value(self, char, value):

        # verify that this value is not in another key
        for keychar in self.key:
            if char == keychar:
                continue
            if value in self.key[keychar] or value in self.tempkey[keychar]:
                return 0
            
        # now, check that we are not adding a value to a key that's already full
        if value not in self.key[char]:
            self.tempkey[char].add(value)
            self.tempcount += 1
        if len(self.key[char]) + len(self.tempkey[char]) > LETTER_FREQUENCIES[char]:
            return 0


        if self.count + self.tempcount == LETTER_TOTAL:
            return 2
        return 1

    def commit(self):
        return {char:self.tempkey[char].union(self.key[char]) for char in self.key}

    def drop(self):
        self.tempcount = 0
        for char in self.key:
            self.tempkey[char] = set()



def crackito_ergo_sum(ciphertext):

    global interactive_keys

    words = cipher_to_words(ciphertext)
    with open(DEFAUT_DICTIONARY) as fp:
        dictionary = json.load(fp)

    interactive_keys = [InteractiveKey({}) for x in words]


    return _recurse_word(words, dictionary, 0)


def _recurse_word(cipherwords, dictionary, index):


    cipherword = cipherwords[0]
    length = str(len(cipherword))
    interactive_key = interactive_keys[index]

    prefix = 'a'*50
    for word in dictionary[length]:

        if DEBUG and index < 2:
            print("{} {}".format('-'*index, word))
        
        if word.startswith(prefix):
            continue
        else:
            prefix = ''
        for char, value in zip(word, cipherword):
            
            res = interactive_key.add_value(char, value)
            prefix += char
            if res == 0 :
                interactive_key.drop()
                break
            if res == 2:
                print("weee! {} {}".format(interactive_key.count, interactive_key.tempcount))
                print("{}".format(interactive_key.commit()))
                return decrypt(interactive_key.commit(), cipherwords)


        else:

            if index== len(interactive_keys) - 2:
                return word
       
            interactive_keys[index+1].count = interactive_key.count + interactive_key.tempcount
            interactive_keys[index+1].tempcount = 0 
            interactive_keys[index+1].key = interactive_key.commit()

            result = _recurse_word(cipherwords[1:], 
                                   dictionary, index+1)
            if result:
                return "{} {}".format(word, result)
            else:
                interactive_key.drop()
    return None


def dumb_space_cracking(ciphertext):
    """
    <name>
        dumb_space_cracking

    <description>
        Does that, find spaces and crack if there's a piece of ciphertext with
        this specific behavior
    """
    with open('barcode.json') as fp:
        space_dict = json.load(fp)

    words = cipher_to_words(ciphertext)
    i = 0

    # build a barcode for this ciphertext
    cipher_barcodes = []
    for word in words:
        i += len(word)
        cipher_barcodes.append(i)
        i += 1

    # compare barcodes with the available barcodes
    for barcode_info in space_dict:
        barcode = barcode_info[0]
        for length, cipher_length in zip(barcode, cipher_barcodes):
            if length != cipher_length:
                break
        else:
            if DEBUG:
                print("found barcode!")
                print(barcode_info[1])
            return barcode_info[1]
    else: 
        print("[xx] couldn't find!")

    return 0

if __name__ == "__main__":

    with open(sys.argv[1]) as fp:
        ciphertext = fp.read()

    #dumb_space_cracking(ciphertext)
    print("{}".format(crackito_ergo_sum(ciphertext)))



