#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Generate index page with links to all previously archived folders during a tag
build
"""

import argparse
import json
import logging
from dataclasses import dataclass, field
from re import sub
from gitlab import Gitlab
from gitlab.v4.objects.commits import ProjectCommit
from gitlab.v4.objects.projects import Project
from gitlab.v4.objects.tags import ProjectTag
from jinja2 import Environment, FileSystemLoader
from jinja2.environment import Template
from sys import stdout
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

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

    # specific arguments
    parser.add_argument('--url',
                        default='https://gitlab.com',
                        help='Basic GitLab URL')
    parser.add_argument('--private-token',
                        default=None,
                        help='Project Access Token with API scope')
    parser.add_argument('--project-id',
                        default=None,
                        required=True,
                        help='Project ID')
    parser.add_argument('--job-name',
                        default=None,
                        required=True,
                        help='Job name which generated the public folder')
    parser.add_argument('--output-dir',
                        default=Path('public').expanduser().resolve(),
                        type=Path,
                        help='Output directory of versioned pages index file')
    parser.add_argument('--pages-base-url',
                        default=None,
                        help='URL of GitLab page, see Settings -> Pages')
    parser.add_argument('--create-version-info-file',
                        action='store_true',
                        help='Create version info JSON file in output folder')
    parser.add_argument('--template-file',
                        type=lambda x: parser_valid_file(parser=parser, arg=x),
                        help='Path to custom index template file')

    parsed_args = parser.parse_args()

    return parsed_args


def parser_valid_file(parser: argparse.ArgumentParser, arg: str) -> Path:
    """
    Determine whether file exists.

    :param      parser:                 The parser
    :type       parser:                 parser object
    :param      arg:                    The file to check
    :type       arg:                    str
    :raise      argparse.ArgumentError: Argument is not a file

    :returns:   Input file path, parser error is thrown otherwise.
    :rtype:     Path
    """
    if not Path(arg).is_file():
        parser.error("The file {} does not exist!".format(arg))
    else:
        return Path(arg).resolve()


@dataclass
class TagInfo:
    tag: ProjectTag
    commit: ProjectCommit
    created_at: datetime
    job_id: int = -1
    pages_url: str = ''
    job_ids: List[Dict[str, int]] = field(default_factory=list)


def get_project(url: str, private_token: str, project_id: int) -> Project:
    """
    Get the GitLab project.

    :param      url:            The url
    :type       url:            str
    :param      private_token:  The private token
    :type       private_token:  str
    :param      project_id:     The project identifier
    :type       project_id:     int

    :returns:   The project.
    :rtype:     Project
    """
    gl = Gitlab(url=url, private_token=private_token)
    project = gl.projects.get(project_id)

    return project


def get_project_tags(project: Project,
                     job_name: str,
                     web_url: str) -> List[TagInfo]:
    """
    Get all project tags.

    :param      project:   The project
    :type       project:   Project
    :param      job_name:  The job name
    :type       job_name:  str
    :param      web_url:   The web url
    :type       web_url:   str

    :returns:   The project tags.
    :rtype:     List[TagInfo]
    """
    tags: List[TagInfo] = []

    for tag in project.tags.list(all=True, as_list=False):
        tag_info = TagInfo(
            tag=tag,    # type: ignore
            commit=project.commits.get(tag.attributes['commit']['id']),
            created_at=datetime.strptime(
                sub(pattern=r'\+.*', repl='', string=tag.commit['created_at']),
                "%Y-%m-%dT%H:%M:%S.%f"
            ),
        )

        get_pipeline_job(
            project=project,
            tag_info=tag_info,
            job_name=job_name,
            web_url=web_url
        )

        tags.append(tag_info)

    return tags


def get_pipeline_job(project: Project,
                     tag_info: TagInfo,
                     job_name: str,
                     web_url: str) -> None:
    """
    Get the pipeline job informations and set the tag info values.

    :param      project:   The project
    :type       project:   Project
    :param      tag_info:  The tag information
    :type       tag_info:  TagInfo
    :param      job_name:  The job name
    :type       job_name:  str
    :param      web_url:   The web url
    :type       web_url:   str
    """
    pages_url: str = ''
    job_id: int = -1
    pipeline_ids: List[Dict[str, int]] = []

    last_pipeline_id = tag_info.commit.last_pipeline['id']
    pipeline = project.pipelines.get(last_pipeline_id)

    for job in pipeline.jobs.list(all=True, as_list=False):
        pipeline_ids.append({job.name: job.id})

        if job.status == "success" and (
            job_name is None or job.name == job_name
        ):
            job_id = job.id
            pages_url = get_artifact_url(
                web_url=web_url,
                job_id=job_id,
                folder='public',
                index_file='index.html'
            )

    tag_info.job_id = job_id
    tag_info.job_ids = pipeline_ids
    tag_info.pages_url = pages_url


def get_artifact_url(web_url: str,
                     job_id: int,
                     folder: str,
                     index_file: str) -> str:
    """
    Create the artifact URL.

    :param      web_url:     The web url
    :type       web_url:     str
    :param      job_id:      The job identifier
    :type       job_id:      int
    :param      folder:      The folder
    :type       folder:      str
    :param      index_file:  The index file
    :type       index_file:  str

    :returns:   The artifact URL.
    :rtype:     str
    """
    url = (
        '{web_url}/-/jobs/{id}/artifacts/{external}{folder}/{index_file}'.
        format(
            web_url=web_url,
            id=job_id,
            external='external_file/' if '.gitlab.io' not in web_url else '',
            folder=folder,
            index_file=index_file
        )
    )

    return url


def save_version_info_file(tag_list: List[TagInfo], file_path: Path) -> None:
    """
    Save a version information file.

    :param      tag_list:   The tag list
    :type       tag_list:   List[TagInfo]
    :param      file_path:  The file path
    :type       file_path:  Path
    """
    version_info = []

    for tag in tag_list:
        info = dict(tag.tag.attributes)
        info['pages_url'] = tag.pages_url
        info['job_id'] = tag.job_id
        info['commit_info'] = tag.commit.attributes
        version_info.append(info)

    save_file(
        content=json.dumps(version_info, indent=4, sort_keys=True),
        path=file_path
    )


def get_template_file(file_name: str,
                      template_folder: Optional[Path] = None) -> Template:
    """
    Get the Jinja2 template file.

    :param      file_name:        The template file name
    :type       file_name:        str
    :param      template_folder:  The template folder
    :type       template_folder:  Path

    :returns:   The template.
    :rtype:     Template
    """
    if template_folder is None:
        template_folder = Path(__file__).parent / "templates"

    environment = Environment(loader=FileSystemLoader(template_folder))
    template = environment.get_template(file_name)

    return template


def save_file(content: str, path: Path) -> None:
    """
    Save data to a file.

    :param      content:  The content
    :type       content:  str
    :param      path:     The path
    :type       path:     Path
    """
    if not path.parent.exists():
        create_output_directory(path=path.parent)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def create_output_directory(path: Path) -> None:
    """
    Create the output directory.

    :param      path:  The path to the output directory
    :type       path:  Path
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def create_html_files(tag_list: List[TagInfo],
                      path: Path,
                      template: Optional[Path] = None) -> None:
    """
    Create all HTML files.

    :param      tag_list:  The tag list
    :type       tag_list:  List[TagInfo]
    :param      path:      The path to the output folder
    :type       path:      Path
    :param      template:  Path to custom template file
    :type       template:  Optional[Path]
    """
    file_name = 'index.html'
    template_folder = None

    if template is not None:
        file_name = template.name
        template_folder = template.parent

    index_template = get_template_file(file_name=file_name,
                                       template_folder=template_folder)

    tag_base_url = sub(
        pattern=r'\/-\/commit\/.*',
        repl='/-/tags/',
        string=tag_list[0].commit.web_url
    )
    index_content = index_template.render(
        items=tag_list,
        tag_base_url=tag_base_url
    )
    save_file(content=index_content, path=path / file_name)


def main() -> None:
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

    logger.debug(args)
    url = args.url
    private_token = args.private_token
    project_id = args.project_id
    job_name = args.job_name
    output_path = args.output_dir
    pages_base_url = args.pages_base_url
    create_version_info_file = args.create_version_info_file
    template_file = args.template_file

    project = get_project(
        url=url,
        private_token=private_token,
        project_id=project_id
    )

    create_output_directory(path=output_path)

    if pages_base_url is None:
        pages_base_url = 'https://{owner}.gitlab.io/-/{name}'.format(
            owner=project.attributes['namespace']['name'],
            name=project.attributes['name']
        )

    if pages_base_url is not None:
        web_url = pages_base_url
    else:
        web_url = project.attributes['web_url']

    # get all tags of the project
    tag_list = get_project_tags(
        project=project,
        job_name=job_name,
        web_url=web_url
    )

    if create_version_info_file:
        save_version_info_file(
            tag_list=tag_list,
            file_path=output_path / 'versions.json'
        )

    create_html_files(
        tag_list=tag_list,
        path=output_path,
        template=template_file
    )


if __name__ == '__main__':
    main()  # pragma: no cover
