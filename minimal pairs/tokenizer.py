#!/usr/bin/env python

# Time spent in this script:
# First time, about 4 hours
# (2023.06.25): 3 hours
# next: 3 hours
# (2023.07.01): 5 hours
# In total, since 07.02 to today 07.04, I've dedicated about 8 more hours (including
# creating the anki deck)

# According to the wikipedia there are two ways to write Bengaluru, but they are not
# really. "For example, the /ŋg/ in the word Beṅgaḷūru (ಬೆಂಗಳೂರು) is usuall
# written ಂಗ rather than ಙ್ಗ (ಬೆಙ್ಗಳೂರು) "
# The problem resides on the postifx (anuswara) which does not translate to only -n or -m,
# but both depending on context
# Stay away from using it for minimal pairs

import re
import sys
from pprint import pprint
from typing import TypedDict, NamedTuple


# Tokenizer adapted from: https://github.com/vinayakakv/akshara_tokenizer
swara = '[\u0c85-\u0c94\u0ce0\u0ce1]'  # pure vowels
vyanjana = '[\u0c95-\u0cb9\u0cde]'  # consonant
halant = '\u0ccd'  # (or virama) makes a consonant to drop its vowel sound (pure consonant)
vowel_signs = '[\u0cbe-\u0ccc]'  # vowel sounds
anuswara = '\u0c82'  # -n sound
visarga = '\u0c83'   # -h sound

# Old tokenizer. Will capture "one" character at the time as a tuple
kannada_tokenizer = re.compile(
    # pure vowel
    f"(?:({swara})|"
    # syllable (group 1: isolated consonant, group 2: consonant, group 3: vowel or
    #           consonant isolator)
    f"((?:{vyanjana}{halant})*)({vyanjana})(?:({vowel_signs})|({halant}))?)"
    # -n or -h posfix sound
    f"({anuswara}|{visarga})?")

# Captures isolated consonants (group 1 of syllable)
halanted_consonant_tokenizer = re.compile(f"({vyanjana}){halant}")

# table for each character and their latin variation
# eg, \u0c85 -> (ɐ, a), \u0c95 -> (k, k)
# Tuple: first IPA, second ISO
phonemes: dict[str, tuple[str, str]] = {
    '\u0c85': ('ɐ', 'a'),
    '\u0c86': ('ɐː', 'ā'),
    '\u0c87': ('i', 'i'),
    '\u0c88': ('iː', 'ī'),
    '\u0c89': ('u', 'u'),
    '\u0c8a': ('uː', 'ū'),
    '\u0c8b': ('ru', 'r̥'),
    '\u0c8e': ('e', 'e'),
    '\u0c8f': ('eː', 'ē'),
    '\u0c90': ('ɐi̯', 'ai'),
    '\u0c92': ('o', 'o'),
    '\u0c93': ('oː', 'ō'),
    '\u0c94': ('ɐu̯', 'au'),

    '\u0c95': ('k', 'k'),
    '\u0c96': ('kʰ', 'kh'),
    '\u0c97': ('g', 'g'),
    '\u0c98': ('gʰ', 'gh'),
    '\u0c99': ('ŋ', 'ṅ'),
    '\u0c9a': ('t͡ʃ', 'c'),
    '\u0c9b': ('t͡ʃʰ', 'ch'),
    '\u0c9c': ('d͡ʒ', 'j'),
    '\u0c9d': ('d͡ʒʱ', 'jh'),
    '\u0c9e': ('ɲ', 'ñ'),
    '\u0c9f': ('ʈ', 'ṭ'),
    '\u0ca0': ('ʈʰ', 'ṭh'),
    '\u0ca1': ('ɖ', 'ḍ'),
    '\u0ca2': ('ɖʱ', 'ḍh'),
    '\u0ca3': ('ɳ', 'ṇ'),
    '\u0ca4': ('t̪', 't'),
    '\u0ca5': ('t̪ʰ', 'th'),
    '\u0ca6': ('d̪', 'd'),
    '\u0ca7': ('d̪ʱ', 'dh'),
    '\u0ca8': ('n̪', 'n'),
    '\u0caa': ('p', 'p'),
    '\u0cab': ('pʰ', 'ph'),
    '\u0cac': ('b', 'b'),
    '\u0cad': ('bʱ', 'bh'),
    '\u0cae': ('m', 'm'),
    '\u0caf': ('j', 'y'),
    '\u0cb0': ('r', 'r'),
    '\u0cb2': ('l', 'l'),
    '\u0cb3': ('ɭ', 'ḷ'),
    '\u0cb5': ('ʋ', 'v'),
    '\u0cb6': ('ɕ', 'ś'),
    '\u0cb7': ('ʂ', 'ṣ'),
    '\u0cb8': ('s', 's'),
    '\u0cb9': ('h', 'h'),

    '\u0cbe': ('ɐː', 'ā'),
    '\u0cbf': ('i', 'i'),
    '\u0cc0': ('iː', 'ī'),
    '\u0cc1': ('u', 'u'),
    '\u0cc2': ('uː', 'ū'),
    '\u0cc3': ('ru', 'r̥'),
    '\u0cc6': ('e', 'e'),
    '\u0cc7': ('eː', 'ē'),
    '\u0cc8': ('ɐi̯', 'ai'),
    '\u0cca': ('o', 'o'),
    '\u0ccb': ('oː', 'ō'),
    '\u0ccc': ('ɐu̯', 'au'),

    '\u0c82': ('m', 'ṃ'),
    '\u0c83': ('h', 'ḥ'),
}

obsolete = {
    '\u0c8c', '\u0ce0', '\u0ce1',
    '\u0cb1', '\u0cde',
    '\u0cc4',
}


class KannadaToken(NamedTuple):
    pure_vowel: str
    additional_consonant: str
    consonant: str
    vowel_sign: str
    halant: str
    postfix: str


class KannadaWord(TypedDict):
    word: str
    tokens: list[KannadaToken]
    ipa: list[str]
    iso: str


def __addConsonant(token: KannadaToken, phs: list[tuple[str, str]]) -> None:
    if token.additional_consonant:
        cons = halanted_consonant_tokenizer.findall(token.additional_consonant)
        if cons[0] == token.consonant:
            phs.extend(phonemes[c] for c in cons[:-1])
            ipa, iso = phonemes[cons[-1]]
            # These consonants are long
            if ipa in 'ŋɳn̪mɭl':
                phs.append((f"{ipa}ː", f"{iso}{iso}"))
            # These consonants are "stopped"
            else:
                phs.append((f"{ipa}.{ipa}", f"{iso}{iso}"))
        else:
            phs.extend(phonemes[c] for c in cons)
            phs.append(phonemes[token.consonant])
    else:
        phs.append(phonemes[token.consonant])

    if not token.vowel_sign and not token.halant:
        phs.append(('ɐ', 'a'))

    if token.vowel_sign:
        phs.append(phonemes[token.vowel_sign])


# a kannada input word and outputs a list of phonemes
def word2phonemes(word: str) -> KannadaWord:
    if not all(0x0c80 <= ord(c) <= 0x0cf3 for c in word):
        return {'word': word, 'tokens': [], 'ipa': [], 'iso': ''}
    tokens = [KannadaToken(*ts) for ts in kannada_tokenizer.findall(word)]
    phs = []
    for token in tokens:
        assert token.pure_vowel not in obsolete
        if token.pure_vowel:
            assert token.consonant == ''
            assert token.vowel_sign == ''
            phs.append(phonemes[token.pure_vowel])
        else:
            assert token.consonant
            __addConsonant(token, phs)
        if token.postfix:
            phs.append(phonemes[token.postfix])

    return {
        'word': word,
        'tokens': tokens,
        'ipa': [p[0] for p in phs],
        'iso': ''.join([p[1] for p in phs])
    }


if __name__ == '__main__':
    # word = "ಬಡ್ತಿ"
    word = sys.argv[1]
    processed_word = word2phonemes(word)
    pprint(processed_word)
