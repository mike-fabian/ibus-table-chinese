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

For all lines starting with x check whether there is another line
containing the same Chinese character with the same input to type
without the x. If such a line exists, change the priority from 1000 to
900.
'''

from typing import Any
from typing import List
from typing import Dict
import re
import logging

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
    table: Dict[Tuple[str, str], int] = {}
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
                table[(input, chinese_character)] = int(weight)
                continue
            if reading_table:
                logging.info('Table read.')
                reading_table = False
            tail.append(line)
    for (input, chinese_character) in table:
        if input.startswith('x'):
            short_input = input[1:]
            if (short_input, chinese_character) in table:
                table[(short_input, chinese_character)] = 900
            valid_input_chars = 'abcdefghijklmnopqrstuvwxyz'
            max_key_length = 5
            if len(short_input) < max_key_length:
                for extra_input in valid_input_chars:
                    if (short_input + extra_input, chinese_character) in table:
                        table[(short_input + extra_input, chinese_character)] = 900
    with open(outputfilename, 'w') as outputfile:
        logging.info("output file=%s", outputfile)
        for line in head:
            outputfile.write('%s' % line)
        for ((input, chinese_character), weight) in sorted(table.items(),
                                                   key=lambda x: (
                                                       x[0][0],
                                                       -x[1]
                                                   )):
            outputfile.write('%s\t%s\t%s\n'
                             % (input, chinese_character, weight))
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
