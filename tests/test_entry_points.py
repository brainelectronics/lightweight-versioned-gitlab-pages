#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Unittest for testing the package entry points"""

import subprocess
import unittest


class TestEntryPoints(unittest.TestCase):

    def setUp(self) -> None:
        """Run before every test method"""
        pass

    def tearDown(self) -> None:
        """Run after every test method"""
        pass

    def test_help(self) -> None:
        """Test help command of package"""
        cmd = ['generate-versioned-pages', '--help']
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        self.assertIn(
            'Generate index page of available versioned pages',
            result.stdout.decode('utf-8')
        )


if __name__ == '__main__':
    unittest.main()
