# Lightweight Versioned GitLab Pages

[![Downloads](https://pepy.tech/badge/lightweight-versioned-gitlab-pages)](https://pepy.tech/project/lightweight-versioned-gitlab-pages)
[![pipeline status](https://gitlab.com/brainelectronics/lightweight-versioned-gitlab-pages/badges/main/pipeline.svg)](https://gitlab.com/brainelectronics/lightweight-versioned-gitlab-pages/-/commits/main)
[![Documentation Status](https://readthedocs.org/projects/lightweight-gitlab-pages/badge/?version=latest)](https://lightweight-gitlab-pages.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gitlab/brainelectronics/lightweight-versioned-gitlab-pages/branch/main/graph/badge.svg)](https://codecov.io/gitlab/brainelectronics/lightweight-versioned-gitlab-pages)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lightweight-versioned-gitlab-pages)
[![License: MIT](https://img.shields.io/gitlab/license/brainelectronics/lightweight-versioned-gitlab-pages?color=green)](https://opensource.org/licenses/MIT)

Generate index page with links to all previously archived folders during a tag
build.

This repo developed in and mirrored from [GitLab brainelectronics](https://gitlab.com/brainelectronics/lightweight-versioned-gitlab-pages).
Please raise your issues and submit your pull requests/merge requests there.

---------------

## Installation

```bash
pip install lightweight-versioned-gitlab-pages
```

## Documentation

📚 The latest documentation is available at

- [Lightweight versioned GitLab Pages GitLab Pages](https://brainelectronics.gitlab.io/lightweight-versioned-gitlab-pages)
- [Lightweight versioned GitLab Pages ReadTheDocs](https://lightweight-gitlab-pages.readthedocs.io/en/latest/)

## Reasoning

GitLab offers the possibility to create or place a folder named `public` in the
root of the repo. The contents of this folder are then displayed by
[GitLab pages](https://docs.gitlab.com/ee/user/project/pages/) and is
accessible from outside the repo via a custom URL.

For this package, the URL is
[`https://brainelectronics.gitlab.io/-/lightweight-versioned-gitlab-pages`](https://brainelectronics.gitlab.io/lightweight-versioned-gitlab-pages).
This is also the location of the (latest) documentation for this package.
Since only only one "thing" can be displayed there, usually only the most
recent content is available at this URL. This is where this package is supposed to help.

## Usage

It is assumed that only tagged states of the documentation or other content
will be displayed on the GitLab Pages web page, see also chapter Limitations.

For interaction with GitLab the
[`python-gitlab`](https://python-gitlab.readthedocs.io/en/stable/) package is
used.

A unique project ID must be specified with `--project-id`.
This ID can be found at the top of each repo. For this repository it is
`43170198`.

The second mandatory parameter is `--job-name`. This is the name of the job
that generates, for example, the documentation or other content that will be
displayed via the GitLab pages web page.

The generated `index.html` is placed in a folder named `public`. By default
this folder is created in the same directory from which this script is called.
A different destination folder can be specified with `--output-dir`. The folder
does not have to exist, it and its possibly needed parent directories will be
created if necessary.

If a self-hosted GitLab is used, the URL to the instance can be specified with
`--url` to not restrict this package to GitLab.com only.

In case the CICD artifacts are not publicly available, the script requires an
API token to make all requests through the API. This token must then be
specified via the `--private-token` argument. The token can be generated via
`Settings -> Access Tokens` and requires `api` scope.

### Help

```bash
generate-versioned-pages --help
```

### Generate lightweight versioned pages

The following command will create a folder named `public` at the current
location and place an index HTML file inside.

This index file contains a simple list of
[Bootstrap cards](https://getbootstrap.com/docs/5.0/components/card/)
with all previously built tags and the URL to the public pages archive files.

```bash
generate-versioned-pages \
--project-id 43170198 \
--job-name pages
```

Then use this generated folder in the `pages` job. The job configuration in the
file `.gitlab-ci.yml` can look like the following example and is used in that
way for this package.

```yaml
pages:
  stage: deploy
  before_script:
    - pip install lightweight-versioned-gitlab-pages
  script:
    - generate-versioned-pages
      --project-id ${CI_PROJECT_ID}
      --job-name generate-docs
  artifacts:
    expire_in: never
    paths:
      - public
  only:
    - main
```

## How it works

First, the available tags of the repo are requested/gathered by the
[get_project_tags](lightweight_versioned_gitlab_pages.generate.get_project_tags)
function. For each tag, the corresponding pipeline job is requested based on
the provided `job-name` argument. The job status must be successful to avoid
erroneous or currently generated artifacts. For each job, the URL to the index
file of the `public` folder is generated, see
[get_artifact_url](lightweight_versioned_gitlab_pages.generate.get_artifact_url)
The generated list of
[TagInfos](lightweight_versioned_gitlab_pages.generate.TagInfo) will then be
used to create a simple `index.html` file inside a generated `public` folder,
unless it is to be generated elsewhere.
The template is rendered with [Jinja2](https://github.com/pallets/jinja/).

## Advanced Usage

### Custom index file

To allow users the usage of a different style index file, the `--template-file`
is there to help.

By default the index template file delivered with this package is used for
rendering. A list of
[TagInfos](lightweight_versioned_gitlab_pages.generate.TagInfo) and the base
URL of tags (`tag_base_url`) is handed over to the Jinj2 render function.

The following informations are availabe for individual usage:

| Name | Type | Description |
| ---- | ----------------- | -------------------|
| `tag_base_url` | str | URL to the project tags, e.g. `https://gitlab.com/brainelectronics/lightweight-versioned-gitlab-pages/-/tags/` |
| `items` | List[TagInfos] | List of TagInfo elements |

Each [TagInfo](lightweight_versioned_gitlab_pages.generate.TagInfo) element
contains the following fields

| Name | Type | Description |
| ---- | ----------------- | -------------------|
| `tag` | ProjectTag | [GitLab ProjectTag](https://python-gitlab.readthedocs.io/en/stable/api/gitlab.v4.html#gitlab.v4.objects.ProjectTag) |
| `commit` | ProjectCommit | [GitLab ProjectCommit](https://python-gitlab.readthedocs.io/en/stable/api/gitlab.v4.html#gitlab.v4.objects.ProjectCommit) |
| `created_at` | datetime | [Datetime object](https://docs.python.org/3/library/datetime.html) with the datetime of the tag creation |
| `job_id` | int | ID of the Job created the tag |
| `pages_url` | str | Full URL to the generated public index file of the job |
| `job_ids` | List[Dict[str, int]] | List of pipeline IDs which ran during the job |

### Custom output directory

Save the rendered index file to a different folder than the default `public`
folder in the directory where the script is executed.

```bash
generate-versioned-pages \
--project-id 43170198 \
--job-name pages \
--output-dir somewhere/else
```

The folder and it's may required parent directories are automatically
generated. The output file name is fixed as `index.html`

### Version info file

To get more informations about the used tags, the `--create-version-info-file`
argument can be used. This will generate a `versions.json` file in the output
directory containing all
[GitLab ProjectTag](https://python-gitlab.readthedocs.io/en/stable/api/gitlab.v4.html#gitlab.v4.objects.ProjectTag)
and [GitLab ProjectCommit](https://python-gitlab.readthedocs.io/en/stable/api/gitlab.v4.html#gitlab.v4.objects.ProjectCommit)
attributes, the Job ID and the Pages URL.

## Limitations

- Only links to tagged and archived data of `public` folders are included in
the index
- Job artifacts must be publicly accessible if no API token is used
    - Make sure that `CI/CD` is activated and set to `Everyone With Access` at
    `Settings -> General -> Visibility`
