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
Improves the wubi-haifeng86 and the wubi-jidian86.txt tables to resolve:

https://github.com/kaio/ibus-table/issues/76

by removing all lines containing CJK COMPATIBILITY IDEOGRAPHs.
'''

from typing import Any
from typing import List
import re
import unicodedata
import logging

def parse_args() -> Any:
    '''Parse the command line arguments'''
    import argparse
    parser = argparse.ArgumentParser(
        description=(
            'Remove lines containing CJK COMPATIBILITY IDEOGRAPHs '
            'from a file'))
    parser.add_argument('-i', '--inputfilename',
                        nargs='?',
                        type=str,
                        default='wubi-haifeng86.UTF-8',
                        help='input file, default is %(default)s')
    parser.add_argument('-o', '--outputfilename',
                        nargs='?',
                        type=str,
                        default='wubi-haifeng86.UTF-8.new',
                        help='output file, default is %(default)s')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='print debugging output')
    return parser.parse_args()

def remove_cjk_compatibility_ideographs(inputfilename: str, outputfilename: str) -> None:
    '''
    Read the file and write a version without the lines
    containing CJK COMPATIBILITY IDEOGRAPHs
    '''
    output_lines: List[str] = []
    with open(inputfilename, 'r') as inputfile:
        logging.info("input file=%s", inputfile)
        for line in inputfile:
            skip_line = False
            for char in line:
                unicode_name = unicodedata.name(char, '')
                if unicode_name.startswith('CJK COMPATIBILITY IDEOGRAPH'):
                    skip_line = True
            if not skip_line:
                output_lines.append(line)
    with open(outputfilename, 'w') as outputfile:
        logging.info("output file=%s", outputfile)
        for line in output_lines:
            outputfile.write('%s' % line)

def main() -> None:
    '''Main program'''
    args = parse_args()
    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)
    remove_cjk_compatibility_ideographs(args.inputfilename, args.outputfilename)

if __name__ == '__main__':
    main()
