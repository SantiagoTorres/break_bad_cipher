#!/usr/bin/env python3
"""
    <name>
        encrpyt.py

    <description>
        Generates a random key of numbers for a wordlist frequency table and
        encrypts a random plaintext

    <usage>
        ./encrypt

    <outputs>
        crypt.txt: a file containing the encrypted text 
        crypt.key: a file containing a human readable from letters to numbers
                    can be loaded by the decrypt script (for verification)
"""
import json
# We know this is not crypto suitable, but it could be easily replaced in 
# production  if so desired.
from random import choice, shuffle 
from string import ascii_lowercase
from letter_frequency import LETTER_FREQUENCIES, LETTER_TOTAL

PLAINTEXT_DICT = 'plaintext_dictionary.txt'
DEFAULT_KEY_FILENAME = "crypt.key"
DEFAULT_CIPHER_FILENAME = "crypt.txt"


def encrypt(key, text):
    """
        <name>
            encrypt

        <description>
            Given a key and a plaintext, output a string of the
            encrypted plaintext
    """

    result  = ''

    for char in text:
        char = char.lower()

        if char not in ascii_lowercase:
            result += char
        else:
            result += "{},".format(choice(key[char]))

    return result

def keygen():
    """
        <name>
            keygen

        <description>
            randomly generates a target key for testing, usinjg the letter
            frequencies. The key is represented as a dictionary (that can
            be parallelized to json)
    """
    values = [x for x in range(1, LETTER_TOTAL+1)]
    shuffle(values)

    key = {}
    for letter in LETTER_FREQUENCIES:
        key[letter] = []
        for i in range(0, LETTER_FREQUENCIES[letter]):
            key[letter].append(values.pop())

    return key

def cipher_to_words(cipher):
    """
        <name>
            cipher_to_words

        <description>
            splits a cipher into a list of lists, where each list is a word
            with a number

    """
    words = cipher.split(" ")
    result = []
    for word in words:
        word = word.strip(",\n")
        word = [int(x) for x in word.split(",")]
        result.append(word)

    return result

def decrypt(key, ciphertext):
    """
        <name>
            decrypt

        <description>
            provided a ciphertext, decrypt the text and display the plaintext
            to the screen

    """
    if type(ciphertext) == list:
        words = ciphertext
    else:
        words = cipher_to_words(ciphertext)
    revkey = _reverse_key(key)
    
    s = ''
    for word in words:
        for value in word:
            if value not in revkey:
                s += '?'
            else:
                s += "{}".format(revkey[value])

        s += " "

    return s


def _reverse_key(key):
    """
        <name>
            _reverse_key
        
        <description>
            reverses the key mapping to decrypt text
    """
    reverse_key = {}
    for char in key:
        for value in key[char]:
            reverse_key[value] = char

    return reverse_key
 
if __name__ == "__main__":

    print("[x] Generating key...")
    key = keygen()

    print("[x] loading plaintexts")
    plaintexts = []
    with open(PLAINTEXT_DICT) as fp:
        for line in fp:
            if len(line) < 5:
                continue
            plaintexts.append(line)

    print("[x] randomly choosing target plaintext")
    target_plaintext = choice(plaintexts)

    print("[x] encrypting...")
    encrypted = encrypt(key, target_plaintext)

    print("[x] saving key...")
    with open(DEFAULT_KEY_FILENAME, 'wt') as fp:
        json.dump(key, fp)

    print("[x] saving ciphertext...")
    with open(DEFAULT_CIPHER_FILENAME, 'wt') as fp:
        fp.write(encrypted)

    print("[x] testing decryption")
    decrypt(key, encrypted)

    print("[x] done...")
