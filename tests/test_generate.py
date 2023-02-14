#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Unittest for testing the documentation index page"""

import argparse
from datetime import datetime
import gitlab
import jinja2
import logging
from nose2.tools import params
from pathlib import Path
from sys import stdout
from typing import Optional
import unittest
from unittest.mock import patch, MagicMock

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

        self._tests_directory = (Path(__file__).parent).resolve()

    def tearDown(self) -> None:
        """Run after every test method"""
        pass

    @patch('sys.argv', ['main', '--project-id', '1234', '--job-name', 'carl'])
    def test_parse_arguments_default(self):
        expectation = {
            'debug': False,
            'verbosity': 0,
            'url': 'https://gitlab.com',
            'private_token': None,
            'project_id': '1234',
            'job_name': 'carl',
            'output_dir':
                Path(__file__).parent.parent.expanduser().resolve() / 'public',
            'pages_base_url': None,
            'create_version_info_file': False,
            'template_file': None,
        }
        args = generate.parse_arguments()
        self.test_logger.debug(args)
        args_as_dict = vars(args)

        for k, v in expectation.items():
            self.assertEqual(args_as_dict[k], v)

    @patch(
        'sys.argv', [
            'main', '--project-id', '1234', '--job-name', 'carl',
            '--url', 'http://git.my-url.com',
            '--private-token', 'qwertz1234',
            '--output-dir', 'one/dir',
            '--template-file', 'tests/data/index.txt',
            '--debug', '-vvvv'
        ]
    )
    def test_parse_arguments_specific(self):
        expectation = {
            'debug': True,
            'verbosity': 4,
            'url': 'http://git.my-url.com',
            'private_token': 'qwertz1234',
            'project_id': '1234',
            'job_name': 'carl',
            'output_dir': Path('one/dir'),
            'pages_base_url': None,
            'create_version_info_file': False,
            'template_file': Path(__file__).parent / 'data' / 'index.txt',
        }
        args = generate.parse_arguments()
        self.test_logger.debug(args)
        args_as_dict = vars(args)

        for k, v in expectation.items():
            self.assertEqual(args_as_dict[k], v)

    def test_parser_valid_file(self):
        parser = argparse.ArgumentParser()
        file_path = __file__

        result = generate.parser_valid_file(parser=parser, arg=file_path)
        self.assertEqual(result, Path(file_path).resolve())

    def test_parser_invalid_file(self):
        parser = argparse.ArgumentParser()
        file_path = 'asdf.qwertz'

        with self.assertRaises(SystemExit) as context:
            generate.parser_valid_file(parser=parser, arg=file_path)

        self.assertEqual('2', str(context.exception))

    def test_get_project(self):
        url = 'https://gitlab.com'
        token = None
        project_id = 43170198

        project = generate.get_project(
            url=url,
            private_token=token,
            project_id=project_id
        )

        self.assertIsInstance(project, gitlab.v4.objects.projects.Project)
        self.assertEqual(project.id, project_id)

    def test_get_project_tags(self):
        project = MagicMock()

        first_project_tag = MagicMock()
        second_project_tag = MagicMock()

        first_project_tag.attributes = {'commit': {'id': 'bcf01494'}}
        first_project_tag.commits.get = 'bcf01494'
        first_project_tag.commit = {
            'created_at': '2023-02-03T15:04:40.000+00:00'
        }

        second_project_tag.attributes = {'commit': {'id': '23fb4d72'}}
        second_project_tag.commits.get = '23fb4d72'
        second_project_tag.commit = {
            'created_at': '2023-02-03T14:15:26.000+00:00'
        }

        project_tags = [first_project_tag, second_project_tag]
        project.tags.list = MagicMock(return_value=project_tags)

        with patch.object(generate, 'get_pipeline_job', return_value=None):
            tags = generate.get_project_tags(
                project=project,
                job_name='carl',
                web_url='asdf'
            )
        self.test_logger.debug(tags)
        self.assertIsInstance(tags, list)
        self.assertEqual(len(tags), 2)
        for tag in tags:
            self.assertIsInstance(tag, generate.TagInfo)
            self.assertIsInstance(tag.created_at, datetime)
            self.test_logger.debug(tag)

    @unittest.skip("Not yet implemented")
    def test_get_pipeline_job(self):
        pass

    def test_get_artifact_url(self):
        web_url = 'https://brainelectronics.gitlab.io/-/asdf'
        job_id = 1234
        folder = 'public'
        index_file = 'index.html'
        expectation = \
            'https://brainelectronics.gitlab.io/-/asdf/-/jobs/1234/artifacts/public/index.html'   # noqa: E501

        result = generate.get_artifact_url(
            web_url=web_url,
            job_id=job_id,
            folder=folder,
            index_file=index_file
        )
        self.assertEqual(result, expectation)

        web_url = 'https://gitlab.com/brainelectronics/quertz'
        job_id = 42
        folder = 'other'
        index_file = 'root.php'
        expectation = \
            'https://gitlab.com/brainelectronics/quertz/-/jobs/42/artifacts/external_file/other/root.php'   # noqa: E501

        result = generate.get_artifact_url(
            web_url=web_url,
            job_id=job_id,
            folder=folder,
            index_file=index_file
        )
        self.assertEqual(result, expectation)

    @unittest.skip("Not yet implemented")
    def test_save_version_info_file(self):
        pass

    @params(
        ('index.html', None),           # use template folder of package
        ('not_existing.html', None),    # use template folder of package
        ('index.txt', 'data/'),         # use custom folder path
        ('not_existing.txt', 'data/'),  # use custom folder path
    )
    def test_get_template_file(self,
                               file_name: str,
                               template_folder: Optional[str]):
        if template_folder is not None:
            template_folder = self._tests_directory / template_folder

        if file_name.startswith('not_existing'):
            with self.assertRaises(jinja2.exceptions.TemplateNotFound) as ctx:
                template = generate.get_template_file(
                    file_name=file_name,
                    template_folder=template_folder
                )

            self.assertEqual(file_name, str(ctx.exception))
        else:
            template = generate.get_template_file(
                file_name=file_name,
                template_folder=template_folder
            )

            self.assertIsInstance(template, jinja2.environment.Template)

    @unittest.skip("Not yet implemented")
    def test_save_file(self):
        pass

    @unittest.skip("Not yet implemented")
    def test_create_output_directory(self):
        pass

    @unittest.skip("Not yet implemented")
    def test_create_html_files(self):
        pass

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
           return_value=argparse.Namespace(project_id=1234, job_name='carl'))
    def test_main(self, mock_pargse_args) -> None:
        generate.main()
    '''


if __name__ == '__main__':
    unittest.main()
