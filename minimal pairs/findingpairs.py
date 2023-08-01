import csv
from typing import Any

from tokenizer import word2phonemes, KannadaWord


def loadKannadaPairs(filename: str) -> list[tuple[str, str]]:
    list_pairs = []
    with open(filename, 'r', newline='') as csvfile:
        for row in csv.reader(csvfile, delimiter='\t'):
            # adding word in kannada script and transcription
            list_pairs.append((row[0], row[4]))
    return list_pairs


discarded_minipairs: set[tuple[str, str]] = set()
difficult_minipairs = [
    ('b', 'bʱ'),
    ('b', 'p'),
    ('b', 'ʋ'),
    ('bʱ', 'p'),
    ('bʱ', 'ʋ'),
    ('bː', 'pː'),
    ('bː', 'ɖ'),
    ('bː', 'ʈː'),
    ('bː', 'ʋ'),
    ('d̪', 'd̪ʱ'),
    ('d̪', 'd͡ʒ'),
    ('d̪', 'p'),
    ('d̪', 't̪'),
    ('d̪', 't̪ʰ'),
    ('d̪', 't̪ː'),
    ('d̪', 't͡ʃː'),
    ('d̪', 'ɖ'),
    ('d̪', 'ʈ'),
    ('d̪', 'ʈʰ'),
    ('d̪', 'ʋ'),
    ('d̪ʱ', 'd͡ʒ'),
    ('d̪ʱ', 'gʰ'),
    ('d̪ʱ', 'h'),
    ('d̪ʱ', 't̪ʰ'),
    ('d̪ʱ', 't͡ʃ'),
    ('d̪ː', 'p'),
    ('d̪ː', 't̪ː'),
    ('d͡ʒ', 'g'),
    ('d͡ʒ', 'gʰ'),
    ('d͡ʒ', 'j'),
    ('d͡ʒ', 't̪'),
    ('d͡ʒ', 't͡ʃ'),
    ('d͡ʒ', 'ɖ'),
    ('d͡ʒː', 'ɖ'),
    ('d͡ʒː', 'ɖː'),
    ('e', 'eː'),
    ('g', 'j'),
    ('g', 'k'),
    ('g', 'kː'),
    ('i', 'iː'),
    ('k', 'p'),
    ('k', 't̪'),
    ('kʰ', 'ʈː'),
    ('l', 'lː'),
    ('l', 'ɭ'),
    ('m', 'n̪'),
    ('m', 'ɳː'),
    ('mː', 'n̪ː'),
    ('n̪', 'ɳ'),
    ('n̪ː', 'ɳ'),
    ('n̪ː', 'ɳː'),
    ('o', 'oː'),
    ('p', 't̪'),
    ('p', 't͡ʃ'),
    ('pː', 't̪ː'),
    ('pː', 'ʈː'),
    ('r', 'ɖ'),
    ('r', 'ɖː'),
    ('r', 'ɭ'),
    ('r', 'ʈ'),
    ('r', 'ʈː'),
    ('t̪', 't̪ʰ'),
    ('t̪', 't͡ʃ'),
    ('t̪', 'ɕ'),
    ('t̪', 'ʈ'),
    ('t̪', 'ʈʰ'),
    ('t̪', 'ʈː'),
    ('t̪ː', 'ʈː'),
    ('u', 'uː'),
    ('ɐ', 'ɐː'),
    # ('ɐ', 'ɐi̯'),
    # ('ɐi̯', 'ɐː'),
    # ('ɐu̯', 'ɐː'),
    ('ʈ', 'ʈʰ'),
    ('ʈ', 'ʈː'),
    ('ʈʰ', 'ʈː'),
]


def minimalPairs(lst: list[Any], lst2: list[Any]) -> tuple[str, str] | None:
    if len(lst) != len(lst2) or len(lst) == 1:
        return None

    this_discarded: set[tuple[str, str]] = set()
    found_diff = False
    found_it: tuple[str, str] | None = None
    for left, right in zip(lst, lst2):
        if left != right:
            if found_diff:
                return None  # only up to one difference, this is the second
            found_diff = True  # found one difference

            # admitting interesting patterns (actual difficult minimal pairs)
            if any(left.replace(ch1, ch2) == right or left.replace(ch2, ch1) == right
                   for ch1, ch2 in difficult_minipairs):
                found_it = tuple(sorted([left, right]))  # type: ignore
            # anything else is discarded
            else:
                this_discarded.add(tuple(sorted([left, right])))  # type: ignore
                break

    if found_diff:
        if found_it:
            return found_it
        else:
            # so we found two words differing in one character, but they are not in the
            # list of difficult minimal pairs
            discarded_minipairs.update(this_discarded)
    return None


if __name__ == '__main__':
    list_pairs = loadKannadaPairs('kannada-2.5k.csv')
    tokenized = [word2phonemes(w) for w, _ in list_pairs]

    perfect: list[KannadaWord] = []
    total_perfect = 0
    total_good = 0
    total_bad = 0
    for (_, iso), kWord in zip(list_pairs, tokenized):
        orig_iso = iso.replace(' ', '').replace('ř', 'r̥').lower()
        this_iso = kWord['iso']

        if iso == this_iso:
            total_perfect += 1
            perfect.append(kWord)
        # All of these are variations on what "anuswara" can be converted into (yeah, it's
        # best to ignore any minimal pairs that contain it)
        elif orig_iso == this_iso \
                or any(orig_iso == this_iso.replace('ṃ', c) for c in 'nṇŋmñ') \
                or orig_iso == this_iso.replace('ḥ', 'h'):
            total_good += 1
        else:
            total_bad += 1
            print(f"Word = {kWord['word']} \tOriginal ISO {iso} != my ISO {kWord['iso']}")

    print("Number of words which ISO matches =", total_perfect)
    print("Number of words which ISO almost matches =", total_good)
    print("Number of words which ISO doesn't match =", total_bad)

    kannada_words = perfect
    # kannada_words = tokenized
    kannada_words.sort(key=lambda kW: kW['iso'])
    # simple double loop to find all minimal pairs (ignoring bad ISO's and "anuswara")
    total_pairs = 0
    for i in range(len(kannada_words)):
        for j in range(i+1, len(kannada_words)):
            pair = minimalPairs(kannada_words[i]['ipa'], kannada_words[j]['ipa'])
            if pair:
                print(f"{pair[0]}\t{pair[1]}\t{kannada_words[i]['word']}\t"
                      f"{kannada_words[j]['word']}\t{kannada_words[i]['iso']}\t"
                      f"{kannada_words[j]['iso']}")
                # print(f"Pair {pair}: {kannada_words[i]['word']} {kannada_words[i]['iso']}"
                #       f" {kannada_words[j]['word']} {kannada_words[j]['iso']}")
                total_pairs += 1

    print(f"Found a total of {total_pairs} pairs")
