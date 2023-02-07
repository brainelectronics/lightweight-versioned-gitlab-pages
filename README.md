# Lightweight Versioned GitLab Pages

[![Downloads](https://pepy.tech/badge/lightweight-versioned-gitlab-pages)](https://pepy.tech/project/lightweight-versioned-gitlab-pages)
[![pipeline status](https://gitlab.com/brainelectronics/lightweight-versioned-gitlab-pages/badges/main/pipeline.svg)](https://gitlab.com/brainelectronics/lightweight-versioned-gitlab-pages/-/commits/main)
[![Documentation Status](https://readthedocs.org/projects/lightweight-versioned-gitlab-pages/badge/?version=latest)](https://lightweight-versioned-gitlab-pages.readthedocs.io/en/latest/?badge=latest)
[![coverage report](https://gitlab.com/brainelectronics/lightweight-versioned-gitlab-pages/badges/main/coverage.svg)](https://gitlab.com/brainelectronics/lightweight-versioned-gitlab-pages/-/commits/main)
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
- [Lightweight versioned GitLab Pages ReadTheDocs](https://lightweight-versioned-gitlab-pages.readthedocs.io/en/latest/)

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

The script will use an API token to make all requests through the
[`python-gitlab`](https://python-gitlab.readthedocs.io/en/stable/) package.
This token must be specified via the `--private-token` argument. The token can
be generated via `Settings -> Access Tokens` and requires `api` scope.

In addition, the unique project ID must be specified with `--project-id`.
This ID can be found at the top of each repo. For this repository it is
`43170198`.

The last mandatory parameter is `--job-name`. This is the name of the job
that generates, for example, the documentation or other content that will be
displayed via the GitLab pages web page.

The generated `index.html` is placed in a folder named `public`. By default
this folder is created in the same directory from which this script is called.
A different destination folder can be specified with `--output-dir`. The folder
does not have to exist, it and its possibly needed parent directories will be
created if necessary.

If a self-hosted GitLab is used, the URL to the instance can be specified with
`--url` to not restrict this package to GitLab.com only.

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
--private_token asdf-carlTheLamaIsHere \
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
      --private_token ${GITLAB_API_TOKEN}
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

## Limitations

- Only links to tagged and archived data of `public` folders are included in
the index
- Job artifacts must be publicly accessible
    - Make sure that `CI/CD` is activated and set to `Everyone With Access` at
    `Settings -> General -> Visibility`
