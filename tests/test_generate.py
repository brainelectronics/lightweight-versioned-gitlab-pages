#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Unittest for testing the documentation index page"""

# import argparse
import logging
# from nose2.tools import params
from sys import stdout
import unittest
# from unittest.mock import patch

from lightweight_versioned_gitlab_pages import generate


class TestGenerate(unittest.TestCase):

    def setUp(self) -> None:
        """Run before every test method"""
        # define a format
        custom_format = '[%(asctime)s] [%(levelname)-8s] [%(filename)-15s @'\
                        ' %(funcName)-15s:%(lineno)4s] %(message)s'

        # set basic config and level for all loggers
        logging.basicConfig(level=logging.INFO,
                            format=custom_format,
                            stream=stdout)

        # create a logger for this TestSuite
        self.test_logger = logging.getLogger(__name__)
        self.package_logger = logging.getLogger('GeneratePage')

        # set the test logger level
        self.test_logger.setLevel(logging.DEBUG)
        self.package_logger.setLevel(logging.DEBUG)

    def tearDown(self) -> None:
        """Run after every test method"""
        pass

    def test_get_artifact_url(self):
        result = generate.get_artifact_url(
            web_url='https://brainelectronics.gitlab.io/-/asdf',
            job_id=1234,
            folder='public',
            index_file='index.html'
        )
        self.assertEqual(
            result,
            'https://brainelectronics.gitlab.io/-/asdf/-/jobs/1234/artifacts/public/index.html'   # noqa: E501
        )

    '''
    @patch('sys.argv', ['main', '--debug'])
    def test_parse_arguments_debug(self) -> None:
        """Test parsing command line arg debug option"""
        args = generate.parse_arguments()

        self.assertTrue(args.debug)

    @params(
        (None, 0),
        ('-v', 1),
        ('-vv', 2),
        ('-vvv', 3),
        ('-vvvv', 4),
        ('-vvvvv', 5),
    )
    def test_parse_arguments_verbosity(self,
                                       verbose_option: str,
                                       expectation: int) -> None:
        """
        Test parsing command line arg debug option

        :param      verbose_option:  The verbose option
        :type       verbose_option:  str
        :param      expectation:     The verbosity expectation value
        :type       expectation:     int
        """
        cmd_args = ['main', verbose_option] if verbose_option else ['main']
        with patch('sys.argv', cmd_args):
            args = generate.parse_arguments()

        self.assertEqual(args.verbosity, expectation)

    @patch('argparse.ArgumentParser.parse_args',
           return_value=argparse.Namespace(verbosity=3, debug=True))
    def test_main(self, mock_pargse_args) -> None:
        generate.main()
    '''


if __name__ == '__main__':
    unittest.main()
