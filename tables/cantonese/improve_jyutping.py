#!/usr/bin/python3
#
# Copyright (c) 2022 Mike FABIAN <mfabian@redhat.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
'''
Improves the jyutping.txt table to resolve:

https://github.com/mike-fabian/ibus-table-chinese/issues/6

Used “unicode_to_jyutping_table.pl” by
Anthony Wong <yp@anthonywong.net> as a starting point.
'''

from typing import Any
from typing import List
from typing import Dict
from typing import Tuple
import re
import unicodedata
import urllib.request
import logging

MAPPING_TABLE: Dict[str, str] = {
    # Special cases
    'm': 'm',
    'ng': 'ng',
    'zou': 'jo', # for 做，早
    'la': 'la', # for 喇
}
INITIALS: Dict[str, str] = {
    # jyutping => cantonese
    'b': 'b',
    'p': 'p',
    'm': 'm',
    'f': 'f',
    'd': 'd',
    't': 't',
    'n': 'n',
    'l': 'l',
    'g': 'g',
    'k': 'k',
    'ng': 'ng',
    'h': 'h',
    'gw': 'gw',
    'kw': 'kw',
    'w': 'w',
    'z': 'j',
    'c': 'ch',
    's': 's',
    'j': 'y',
}

FINALS: Dict[str, str] = {
    # jyutping => cantonese
    'aa': 'a',
    'aai': 'aai',
    'aau': 'aau',
    'aam': 'aam',
    'aan': 'aan',
    'aang': 'aang',
    'aap': 'aap',
    'aat': 'aat',
    'aak': 'aak',
    'ai': 'ai',
    'au': 'au',
    'am': 'am',
    'an': 'an', # special case: 燜 uses 'men'
    'ang': 'ang',
    'ap': 'ap',
    'at': 'at',
    'ak': 'ak',
    'e': 'e',
    'ei': 'ei',
    'eu': 'eu', # no such pronuncation in original cantonese romanization
    'em': 'em',
    'en': 'en',
    'eng': 'eng',
    'ep': 'ep',
    'et': 'et',
    'ek': 'ek',
    'i': 'i',
    'iu': 'iu',
    'im': 'im',
    'in': 'in',
    'ing': 'ing',
    'ip': 'ip',
    'it': 'it',
    'ik': 'ik',
    'o': 'oh',
    'oi': 'oi',
    'ou': 'ou',  # cantonese romanization also use 'o'
    'om': 'yam', # 媕, om
    'on': 'on',
    'ong': 'ong',
    'ot': 'ot',
    'ok': 'ok',
    'u': 'oo',
    'ui': 'ooi',
    'un': 'oon',
    'ung': 'ung',
    'ut': 'oot',
    'uk': 'uk',
    'oe': 'oe', # seems no corresponding romanization in cantonese
    'eoi': 'ui',
    'eon': 'un',
    'oeng': 'eung',
    'eot': 'ut',
    'oet': 'ut', # 㖀, loet
    'oek': 'euk',
    'yu': 'ue',
    'yun': 'uen',
    'yut': 'uet',
    'm': 'am',   # 噷, hm
    'ng': 'ang', # 哼, hng
}

def parse_args() -> Any:
    '''Parse the command line arguments'''
    import argparse
    parser = argparse.ArgumentParser(
        description=(
            'Python script to improve the jyutping.txt table.'))
    parser.add_argument('-i', '--inputfilename',
                        nargs='?',
                        type=str,
                        default='jyutping.txt',
                        help='input file, default is %(default)s')
    parser.add_argument('-o', '--outputfilename',
                        nargs='?',
                        type=str,
                        default='jyutping.txt.new',
                        help='output file, default is %(default)s')
    parser.add_argument('-u', '--unihanreadingsfilename',
                        nargs='?',
                        type=str,
                        default='Unihan_Readings.txt',
                        help=('file to use for the readings, '
                              'default is %(default)s'))
    parser.add_argument('-f', '--frequencyfilename',
                        nargs='?',
                        type=str,
                        default='cantonese.txt',
                        help=('file to use for the frequencies, '
                              'default is %(default)s'))
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='print debugging output')
    return parser.parse_args()

def convert_jp_to_cantonese(jp: str) -> str:
    if not jp:
        return ''
    if jp in MAPPING_TABLE:
        return MAPPING_TABLE[jp]
    initial = ''
    for key in INITIALS:
        if not jp.startswith(key):
            continue
        if len(jp) == len(key):
            MAPPING_TABLE[jp] = INITIALS[key]
            return MAPPING_TABLE[jp]
        if len(key) > len(initial):
            initial = key
    for final in FINALS:
        if not jp == initial + final:
            continue
        if not initial:
            MAPPING_TABLE[jp] = FINALS[final]
        else:
            MAPPING_TABLE[jp] = INITIALS[initial] + FINALS[final]
        return MAPPING_TABLE[jp]
    logging.error('Impossible!')
    exit(1)

def create_freq_table(inputfilename: str) -> Dict[Tuple[str, str], str]:
    '''
    Read the frequencies from the frequency file (default: cantonese.txt)
    '''
    head: List[str] = []
    tail: List[str] = []
    table: Dict[Tuple[str, str], str] = {}
    reading_head = True
    reading_table = True
    reading_tail = True
    with open(inputfilename, 'r') as inputfile:
        logging.info("input file=%s", inputfile)
        for line in inputfile:
            if reading_head and not line.startswith('BEGIN_TABLE'):
                head.append(line)
                continue
            if reading_head:
                logging.info('Header read.')
                head.append('BEGIN_TABLE\n')
                reading_head = False
                continue
            if reading_table and not line.startswith('END_TABLE'):
                (input,
                 chinese_character,
                 weight) = line.strip().split('\t')[:3]
                table[(input, chinese_character)] = weight
                continue
            if reading_table:
                logging.info('Table read.')
                reading_table = False
            tail.append(line)
    return table

def create_all_pinyin_table(
        inputfilename: str,
        freq_table: Dict[Tuple[str, str], str]
) -> Dict[Tuple[str, str], Dict[str, str]]:
    table: Dict[Tuple[str, str], Dict[str, str]] = {}
    pattern = re.compile(
        r'^U\+(?P<codepoint>[0-9A-Z]+)\s+kCantonese\s+(?P<pinyin>[a-zA-Z1-6]+)$')
    with open(inputfilename, 'r') as inputfile:
        logging.info("input file=%s", inputfile)
        for line in inputfile:
            match = pattern.match(line)
            if not match:
                continue
            codepoint = match.group('codepoint')
            pinyin = match.group('pinyin')
            # Tonal markers using letters instead of digits according to:
            # https://github.com/rime/rime-cantonese/blob/main/README-en.md#tonal-markers
            trans_table = {
                # High level, e.g. siv → 詩; High level checked, e.g. sikv → 色
                ord('1'): 'v',
                # Medium rising, e.g. six → 史
                ord('2'): 'x',
                # Medium level, e.g. siq→ 試; Medium level checked, e.g. sekq → 錫
                ord('3'): 'q',
                # Low falling, e.g. sivv → 時
                ord('4'): 'vv',
                # Low rising, e.g. sixx → 市
                ord('5'): 'xx',
                # Low level, e.g. siqq→ 事; Low level checked, e.g. sikqq → 食
                ord('6'): 'qq',
            }
            pinyin_letters = pinyin.translate(trans_table)
            pinyin_toneless = pinyin[:-1]
            cantonese = convert_jp_to_cantonese(pinyin_toneless)
            char = chr(int(codepoint, 16))
            frequency = '0'
            if (cantonese, char) in freq_table:
                frequency = freq_table[(cantonese, char)]
            table[(pinyin_toneless, char)] = {
                'pinyin': pinyin,
                'pinyin_letters': pinyin_letters,
                'cantonese': cantonese,
                'frequency': frequency,
            }
    return table

def improve_jyutping(
        inputfilename: str,
        outputfilename: str,
        all_pinyin: Dict[Tuple[str, str], Dict[str, str]] = {}) -> None:
    '''
    Read the jyutping.txt file and write an improved version
    '''
    head: List[str] = []
    tail: List[str] = []
    table: Dict[Tuple[str, str], str] = {}
    reading_head = True
    reading_table = True
    reading_tail = True
    with open(inputfilename, 'r') as inputfile:
        logging.info("input file=%s", inputfile)
        for line in inputfile:
            if reading_head and not line.startswith('BEGIN_TABLE'):
                head.append(line)
                continue
            if reading_head:
                logging.info('Header read.')
                head.append('BEGIN_TABLE\n')
                reading_head = False
                continue
            if reading_table and not line.startswith('END_TABLE'):
                (input,
                 chinese_character,
                 weight) = line.strip().split('\t')[:3]
                table[(input, chinese_character)] = weight
                continue
            if reading_table:
                logging.info('Table read.')
                reading_table = False
            tail.append(line)
    for (pinyin_toneless, chinese_character) in all_pinyin:
        if (pinyin_toneless, chinese_character) in table:
            frequency_orig = table[(pinyin_toneless, chinese_character)]
            frequency = all_pinyin[
                (pinyin_toneless, chinese_character)]['frequency']
            pinyin = all_pinyin[
                (pinyin_toneless, chinese_character)]['pinyin']
            pinyin_letters =  all_pinyin[
                (pinyin_toneless, chinese_character)]['pinyin_letters']
            if (int(frequency_orig) == 0 and int(frequency) > 0):
                logging.info(
                    'Adding frequency from cantonese.txt %s %s %s -> %s',
                    pinyin_toneless, chinese_character, frequency_orig, frequency)
                table[(pinyin_toneless, chinese_character)] = frequency
            if (pinyin_toneless != pinyin_letters
                and pinyin_letters.startswith(pinyin_toneless)
                and (pinyin_letters, chinese_character) not in table):
                logging.info(
                    'Adding tone %s %s -> %s -> %s',
                    pinyin_toneless, chinese_character, pinyin, pinyin_letters)
                table[(pinyin_letters, chinese_character)] = (
                    table[(pinyin_toneless, chinese_character)])
                # Keep entry with the toneless pinyin to make typing
                # without pinyin still get exact matches, i.e. do not
                # delete the toneless entry:
                # del table[(pinyin_toneless, chinese_character)]
    with open(outputfilename, 'w') as outputfile:
        logging.info("output file=%s", outputfile)
        for line in head:
            outputfile.write('%s' % line)
        for ((input, chinese_character), weight) in sorted(table.items(),
                                                   key=lambda x: (
                                                       x[0][0],   # input
                                                       #x[0][1],   # Chinese character
                                                       -int(x[1]) # weight
                                                   )):
            outputfile.write(
                f'{input}\t{chinese_character}\t{weight}\n')
        for line in tail:
            outputfile.write('%s' % line)

def main() -> None:
    '''Main program'''
    args = parse_args()
    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)
    freq_table = create_freq_table(args.frequencyfilename)
    all_pinyin = create_all_pinyin_table(args.unihanreadingsfilename, freq_table)
    improve_jyutping(args.inputfilename,
                     args.outputfilename,
                     all_pinyin)

if __name__ == '__main__':
    main()
