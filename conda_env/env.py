from __future__ import absolute_import, print_function
from collections import OrderedDict
from copy import copy
import os
import re
import sys

# TODO This should never have to import from conda.cli
from itertools import chain

from conda.cli import common
from conda import install
from conda import config

from . import compat
from . import exceptions
from . import yaml
from conda_env.pip_util import add_pip_installed


def load_from_directory(directory):
    """Load and return an ``Environment`` from a given ``directory``"""
    files = ['environment.yml', 'environment.yaml']
    while True:
        for f in files:
            try:
                return from_file(os.path.join(directory, f))
            except exceptions.EnvironmentFileNotFound:
                pass
        old_directory = directory
        directory = os.path.dirname(directory)
        if directory == old_directory:
            break
    raise exceptions.EnvironmentFileNotFound(files[0])


# TODO This should lean more on conda instead of divining it from the outside
# TODO tests!!!
def from_environment(name, prefix, no_builds=False):
    installed = install.linked(prefix)
    conda_pkgs = copy(installed)
    # json=True hides the output, data is added to installed
    add_pip_installed(prefix, installed, json=True)

    pip_pkgs = sorted(installed - conda_pkgs)

    if no_builds:
        dependencies = ['='.join(a.rsplit('-', 2)[0:2]) for a in sorted(conda_pkgs)]
    else:
        dependencies = ['='.join(a.rsplit('-', 2)) for a in sorted(conda_pkgs)]
    if len(pip_pkgs) > 0:
        dependencies.append({'pip': ['=='.join(a.rsplit('-', 2)[:2]) for a in pip_pkgs]})

    # conda uses ruamel_yaml which returns a ruamel_yaml.comments.CommentedSeq
    # this doesn't dump correctly using pyyaml
    channels = list(config.get_rc_urls())

    return Environment(name=name, dependencies=dependencies, channels=channels, prefix=prefix)


# TODO: This is duplicated from conda_build. Could yaml parsing from both libraries
# be merged instead of duplicated? This could include jinja2 and "# [unix]" flags.
def render_jinja(content, **kwargs):
    try:
        import jinja2
    except ImportError:
        return content

    # Add {{ root }} to render dict
    if 'filename' in kwargs:
        kwargs['root'] = os.path.dirname(os.path.abspath(kwargs['filename']))

    # Add {{ os }} to render dict
    kwargs['os'] = os

    return jinja2.Template(content).render(**kwargs)


def from_yaml(yamlstr, **kwargs):
    """Load and return a ``Environment`` from a given ``yaml string``"""
    yamlstr = render_jinja(yamlstr, **kwargs)

    try:
        data = yaml.load(yamlstr)
    except yaml.parser.ParserError:
        try:
            import jinja2
        except ImportError:
            raise exceptions.UnableToParseMissingJinja2()
        raise

    if kwargs is not None:
        for key, value in kwargs.items():
            data[key] = value
    return Environment(**data)


def from_file(filename, **kwargs):
    if not os.path.exists(filename):
        raise exceptions.EnvironmentFileNotFound(filename)
    with open(filename, 'r') as fp:
        yamlstr = fp.read()
        return from_yaml(yamlstr, filename=os.path.abspath(filename), **kwargs)


# TODO test explicitly
class Dependencies(OrderedDict):
    def __init__(self, raw, *args, **kwargs):
        super(Dependencies, self).__init__(*args, **kwargs)
        self.raw = raw
        self.parse()

    def parse(self):
        if not self.raw:
            return

        self.update({'conda': []})

        for line in self.raw:
            if type(line) is dict:
                for installer, dependencies in line.items():
                    self[installer] = self.get(installer, []) + dependencies
            else:
                self['conda'].append(common.arg2spec(line))

    # TODO only append when it's not already present
    def add(self, package_name):
        self.raw.append(package_name)
        self.parse()

    def include(self, other):
        # Insert included dependencies in front of self's to maintain order.
        self.raw = other.raw + self.raw
        self.parse()

def unique(seq, key=None):
    """ Return only unique elements of a sequence
    >>> tuple(unique((1, 2, 3)))
    (1, 2, 3)
    >>> tuple(unique((1, 2, 1, 3)))
    (1, 2, 3)
    Uniqueness can be defined by key keyword
    >>> tuple(unique(['cat', 'mouse', 'dog', 'hen'], key=len))
    ('cat', 'mouse')
    """
    seen = set()
    seen_add = seen.add
    if key is None:
        for item in seq:
            if item not in seen:
                seen_add(item)
                yield item
    else:  # calculate key
        for item in seq:
            val = key(item)
            if val not in seen:
                seen_add(val)
                yield item


class Environment(object):
    def __init__(self, name=None, filename=None, channels=None,
                 dependencies=None, prefix=None, environment=None, aliases=None,
                 includes=None, _included_files=None):
        self.name = name
        self.filename = filename
        self.prefix = prefix
        self.dependencies = Dependencies(dependencies or [])
        if channels is None:
            channels = []
        self.channels = channels
        self.environment = environment or []
        self.aliases = aliases or {}
        self.includes = includes or []

        # Internal field kept to avoid recursion errors.
        self._included_files = _included_files or []

        self._included_files.append(self.filename)
        for included_file in self.includes:
            if os.path.abspath(included_file) in self._included_files:
                continue

            # Insert every included field in front of self's to maintain order.
            included_env = from_file(included_file, _included_files=self._included_files)
            self.dependencies.include(included_env.dependencies)
            self.channels = included_env.channels + self.channels
            self.environment = included_env.environment + self.environment

            aliases = included_env.aliases.copy()
            aliases.update(self.aliases)
            self.aliases = aliases

            self._included_files = list(OrderedDict.fromkeys(included_env._included_files + self._included_files))

    def add_channels(self, channels):
        self.channels = list(unique(chain.from_iterable((channels, self.channels))))

    def remove_channels(self):
        self.channels = []

    def to_dict(self):
        d = yaml.dict([('name', self.name)])
        if self.channels:
            d['channels'] = self.channels
        if self.dependencies:
            d['dependencies'] = self.dependencies.raw
        if self.prefix:
            d['prefix'] = self.prefix
        if self.environment:
            d['environment'] = self.environment
        if self.aliases:
            d['aliases'] = self.aliases
        return d

    def to_yaml(self, stream=None):
        d = self.to_dict()
        out = compat.u(yaml.dump(d, default_flow_style=False))
        if stream is None:
            return out
        stream.write(compat.b(out, encoding="utf-8"))

    def save(self):
        with open(self.filename, "wb") as fp:
            self.to_yaml(stream=fp)
