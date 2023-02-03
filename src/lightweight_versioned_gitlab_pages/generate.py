#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Generate index page with links to all previously archived folders during a tag
build
"""

import argparse
import logging
from sys import stdout

from .version import __version__


def parse_arguments() -> argparse.Namespace:
    """
    Parse CLI arguments.
    :raise      argparse.ArgumentError  Argparse error
    :return:    argparse object
    """
    parser = argparse.ArgumentParser(description="""
    Generate index page of available versioned pages
    """, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # default arguments
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Output logger messages to stderr')
    parser.add_argument('-v',
                        default=0,
                        action='count',
                        dest='verbosity',
                        help='Set level of verbosity, default is CRITICAL')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {version}'.
                                format(version=__version__),
                        help="Print version of package and exit")

    parsed_args = parser.parse_args()

    return parsed_args


def main():
    # parse CLI arguments
    args = parse_arguments()

    log_levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }
    custom_format = '[%(asctime)s] [%(levelname)-8s] [%(filename)-15s @'\
                    ' %(funcName)-15s:%(lineno)4s] %(message)s'
    logging.basicConfig(level=logging.INFO,
                        format=custom_format,
                        stream=stdout)
    logger = logging.getLogger(__name__)
    logger.setLevel(level=log_levels[min(args.verbosity,
                                     max(log_levels.keys()))])
    logger.disabled = not args.debug


if __name__ == '__main__':
    main()  # pragma: no cover
