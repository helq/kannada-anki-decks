import csv
from typing import NamedTuple, Any
import pathlib
import glob

import genanki
from bs4 import BeautifulSoup

from tokenizer import KannadaWord, word2phonemes


class KannadaSound(NamedTuple):
    sound: str
    recording: int
    word: KannadaWord


class Pair(NamedTuple):
    left: KannadaSound
    right: KannadaSound
    tip: str


def loadKannadaPairs() -> list[Pair]:
    # Loading recording number
    record_num = {
        w: int(i)
        for i, w in [row.split() for row in open('./words-on-their-own.txt', 'r').readlines()]}

    # Loading pairs
    pairs = []
    with open('pairs.csv', 'r', newline='') as csvfile:
        for row in csv.reader(csvfile, delimiter='\t'):
            # adding word in kannada script and transcription
            pairs.append(Pair(
                left=KannadaSound(row[0], record_num[row[2]], word2phonemes(row[2])),
                right=KannadaSound(row[1], record_num[row[3]], word2phonemes(row[3])),
                tip=row[6] if len(row) > 6 else ''
            ))

    return pairs


def load_html_template(path: str) -> str:
    here = pathlib.Path(path).parent
    with open(path, 'r') as html:
        soup = BeautifulSoup(html, features='html.parser')

    for script in soup.find_all('script', src=True):
        src_path = here / script.attrs.pop('src')
        data = open(src_path.resolve(), 'r').read()
        script.insert(0, data)

    # TODO: Minify js here. Anki seems to have problems with minified js, but there is
    # probably a way.

    return str(soup.prettify(formatter='html'))


class PairNote(genanki.Note):  # type: ignore
    @property
    def guid(self) -> Any:
        return genanki.guid_for(self.fields[0])


minimal_note = {
  'qfmt': load_html_template('anki-assets/notes/minimal-pair-front.html'),
  'afmt': load_html_template('anki-assets/notes/minimal-pair-back.html'),
}


minimal_model = genanki.Model(
  5238922911,
  'Kannada - Minimal pairs',
  fields=[
    {'name': 'PairSounds'},  # To be used as key for card
    {'name': 'Sound1'},  # phoneme 1
    {'name': 'Word1'},
    {'name': 'IPA1'},  # IPA of entire word
    {'name': 'ISO1'},  # another sound strategy
    {'name': 'Recordings1'},
    {'name': 'Sound2'},  # phoneme 2
    {'name': 'Word2'},
    {'name': 'IPA2'},
    {'name': 'ISO2'},
    {'name': 'Recordings2'},
    {'name': 'Tip'},
  ],
  templates=[
    {'name': "Note 1"} | minimal_note,
    {'name': "Note 2"} | minimal_note,
  ],
  css=open('anki-assets/style.css').read()
)


if __name__ == '__main__':
    pairs = loadKannadaPairs()

    pairs_deck = genanki.Deck(
        70628919387,
        'Kannada::1. Minimal Pairs'
    )

    for left, right, tip in pairs:
        if left.sound not in left.word['ipa']:
            print(f"{left.sound} isn't in {left.word['ipa']}")
        if right.sound not in right.word['ipa']:
            print(f"{right.sound} isn't in {right.word['ipa']}")

        soundnames_left = [
            pathlib.Path(file).name
            for file in
            glob.glob(f'audio/audio-1/kannada_minimal_1_{left.recording}.*')
            + glob.glob(f'audio/audio-2/kannada_minimal_2_{left.recording}.*')
        ]

        soundnames_right = [
            pathlib.Path(file).name
            for file in
            glob.glob(f'audio/audio-1/kannada_minimal_1_{right.recording}.*')
            + glob.glob(f'audio/audio-2/kannada_minimal_2_{right.recording}.*')
        ]

        fields: list[str] = [
            f'{left.word["iso"]} vs {right.word["iso"]}',
            left.sound,
            left.word['word'],
            ''.join(left.word['ipa']),
            left.word['iso'],
            ' EOL '.join(f'[sound:{name}]' for name in soundnames_left),
            right.sound,
            right.word['word'],
            ''.join(right.word['ipa']),
            right.word['iso'],
            ' EOL '.join(f'[sound:{name}]' for name in soundnames_right),
            tip
        ]
        pairs_deck.add_note(PairNote(model=minimal_model, fields=fields))

    package = genanki.Package(pairs_deck)
    package.write_to_file('kannada_minimal_pairs.apkg')
