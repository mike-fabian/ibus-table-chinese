#!/usr/bin/python3
#
# Copyright (c) 2021 Mike FABIAN <mfabian@redhat.com>
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
Improves the cangjie5.txt table to resolve:

https://github.com/mike-fabian/ibus-table/issues/76
https://github.com/mike-fabian/ibus-table-chinese/issues/11

The weight of each Chinese character is set by how common it is,
using the Big5 and HKSCS character sets as a frequency tier:

    Big5 level 1 (常用字)            1000
    Big5 level 2 (次常用字), HKSCS    800
    other BMP                         600
    outside the BMP                   500

For all lines starting with x check whether there is another line
containing the same Chinese character with the same input to type
without the x. If such a line exists, lower its weight by 100.

Entries which are not CJK ideographs (punctuation etc.) keep their
weights, these are ordered by hand.
'''

from typing import Any
from typing import List
from typing import Dict
from typing import Set
from typing import Tuple
import re
import unicodedata
import urllib.request
import logging

IMPORT_CHINESE_VARIANTS_SUCCESSFUL = False
try:
    import chinese_variants
    IMPORT_CHINESE_VARIANTS_SUCCESSFUL = True
except (ImportError,):
    IMPORT_CHINESE_VARIANTS_SUCCESSFUL = False

TIER_WEIGHTS = {'big5-L1': 1000, 'big5-L2': 800, 'hkscs': 800,
                'other-bmp': 600, 'non-bmp': 500}

def tier(char: str) -> str:
    '''Classify a character by the most common character set containing it'''
    try:
        encoded = char.encode('big5')
        if len(encoded) == 2:
            if 0xA440 <= int.from_bytes(encoded, 'big') <= 0xC67E:
                return 'big5-L1'
            return 'big5-L2'
    except UnicodeEncodeError:
        pass
    try:
        char.encode('big5hkscs')
        return 'hkscs'
    except UnicodeEncodeError:
        pass
    return 'other-bmp' if ord(char) <= 0xFFFF else 'non-bmp'

def is_cjk_ideograph(char: str) -> bool:
    '''Whether char is a CJK (unified or compatibility) ideograph'''
    return unicodedata.name(char, '').startswith(
        ('CJK UNIFIED IDEOGRAPH', 'CJK COMPATIBILITY IDEOGRAPH'))

def parse_args() -> Any:
    '''Parse the command line arguments'''
    import argparse
    parser = argparse.ArgumentParser(
        description=(
            'Generate a script containing a table and a function '
            + 'to check whether a string of Chinese characters '
            + 'is simplified or traditional'))
    parser.add_argument('-i', '--inputfilename',
                        nargs='?',
                        type=str,
                        default='cangjie5.txt',
                        help='input file, default is %(default)s')
    parser.add_argument('-o', '--outputfilename',
                        nargs='?',
                        type=str,
                        default='cangjie5.txt.new',
                        help='output file, default is %(default)s')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='print debugging output')
    return parser.parse_args()

def improve_cangjie5(inputfilename: str, outputfilename: str) -> None:
    '''
    Read the cangjie5.txt file and write an improved version
    '''
    head: List[str] = []
    tail: List[str] = []
    table: Dict[Tuple[str, str], Dict[str, Any]] = {}
    lowered: Set[Tuple[str, str]] = set()
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
                stripped_line = line.strip().split('\t')
                if len(stripped_line) < 4:
                    stripped_line.append('')
                (input,
                 chinese_character,
                 weight,
                 comment) = stripped_line
                table[(input, chinese_character)] = {
                    'weight': int(weight),
                    'comment': comment,
                    }
                continue
            if reading_table:
                logging.info('Table read.')
                reading_table = False
            tail.append(line)
    for (input, chinese_character) in table:
        unicode_name = unicodedata.name(chinese_character, '')
        if False and unicode_name.startswith('CJK COMPATIBILITY IDEOGRAPH'):
            unicode_decomposition = unicodedata.decomposition(
                chinese_character)
            unicode_decomposition_char = ''
            if unicode_decomposition:
                unicode_decomposition_char = chr(
                    int(unicode_decomposition, 16))
            logging.info('%s\t%s\t%s %s %s %s',
                         input,
                         chinese_character,
                         table[(input, chinese_character)],
                         unicode_name,
                         unicode_decomposition,
                         unicode_decomposition_char)
        if IMPORT_CHINESE_VARIANTS_SUCCESSFUL:
            category = chinese_variants.detect_chinese_category(
                chinese_character)
            if category == 1:
                used_in_taiwan = False
                utf8_for_url = ''
                for byte in chinese_character.encode('utf-8'):
                    utf8_for_url += f'%{byte:X}'
                url = (f'https://dict.revised.moe.edu.tw/'
                       f'search.jsp?md=1&word={utf8_for_url}#searchL')
                with urllib.request.urlopen(url) as f:
                    page = f.read().decode('utf-8')
                    if page and '查無資料' not in page:
                        used_in_taiwan = True
                logging.info(
                    'Classified as simplified only: %s\t%s\tused_in_taiwan=%s',
                    input, chinese_character, repr(used_in_taiwan))
        if input.startswith('x'):
            short_input = input[1:]
            if (short_input, chinese_character) in table:
                lowered.add((short_input, chinese_character))
            valid_input_chars = 'abcdefghijklmnopqrstuvwxyz'
            max_key_length = 5
            if len(short_input) < max_key_length:
                for extra_input in valid_input_chars:
                    if (short_input + extra_input, chinese_character) in table:
                        lowered.add((short_input + extra_input,
                                     chinese_character))
    for (input, chinese_character), value in table.items():
        if all(is_cjk_ideograph(char) for char in chinese_character):
            value['weight'] = min(TIER_WEIGHTS[tier(char)]
                                  for char in chinese_character)
            if (input, chinese_character) in lowered:
                value['weight'] -= 100
    with open(outputfilename, 'w') as outputfile:
        logging.info("output file=%s", outputfile)
        for line in head:
            outputfile.write('%s' % line)
        for ((input, chinese_character), value) in sorted(table.items(),
                                                   key=lambda x: (
                                                       x[0][0],
                                                       -x[1]['weight']
                                                   )):
            if value['comment']:
                outputfile.write('%s\t%s\t%s\t%s\n'
                                 % (input, chinese_character, value['weight'],
                                    value['comment']))
            else:
                outputfile.write('%s\t%s\t%s\n'
                                 % (input, chinese_character, value['weight']))
        for line in tail:
            outputfile.write('%s' % line)

def main() -> None:
    '''Main program'''
    args = parse_args()
    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)
    improve_cangjie5(args.inputfilename, args.outputfilename)

if __name__ == '__main__':
    main()
