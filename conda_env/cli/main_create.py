from __future__ import print_function
from argparse import RawDescriptionHelpFormatter
import os
import sys
import textwrap

from conda.cli import common
from conda.cli import install as cli_install
from conda.install import rm_rf
from conda.misc import touch_nonadmin
from conda.plan import is_root_prefix

from ..installers.base import get_installer, InvalidInstaller
from .. import exceptions
from .. import specs

description = """
Create an environment based on an environment file
"""

example = """
examples:
    conda env create
    conda env create -n name
    conda env create vader/deathstar
    conda env create -f=/path/to/environment.yml
    conda env create -f=/path/to/requirements.txt -n deathstar
"""


def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'create',
        formatter_class=RawDescriptionHelpFormatter,
        description=description,
        help=description,
        epilog=example,
    )
    p.add_argument(
        '-f', '--file',
        action='store',
        help='environment definition file (default: environment.yml)',
        default='environment.yml',
    )
    p.add_argument(
        '-n', '--name',
        action='store',
        help='environment definition',
        default=None,
        dest='name'
    )
    p.add_argument(
        '-q', '--quiet',
        action='store_true',
        default=False,
    )
    p.add_argument(
        'remote_definition',
        help='remote environment definition / IPython notebook',
        action='store',
        default=None,
        nargs='?'
    )
    p.add_argument(
        '--force',
        help='force creation of environment (removing a previously existing environment of the same name).',
        action='store_true',
        default=False,
    )
    common.add_parser_json(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    name = args.remote_definition or args.name
    try:
        spec = specs.detect(name=name, filename=args.file,
                            directory=os.getcwd())
        env = spec.environment

        # FIXME conda code currently requires args to have a name or prefix
        if args.name is None:
            args.name = env.name

    except exceptions.SpecNotFound as e:
        common.error_and_exit(str(e), json=args.json)

    prefix = common.get_prefix(args, search=False)
    if args.force and not is_root_prefix(prefix) and os.path.exists(prefix):
        rm_rf(prefix)
    cli_install.check_prefix(prefix, json=args.json)

    # TODO, add capability
    # common.ensure_override_channels_requires_channel(args)
    # channel_urls = args.channel or ()

    for installer_type, pkg_specs in env.dependencies.items():
        try:
            installer = get_installer(installer_type)
            installer.install(prefix, pkg_specs, args, env)
        except InvalidInstaller:
            sys.stderr.write(textwrap.dedent("""
                Unable to install package for {0}.

                Please double check and ensure you dependencies file has
                the correct spelling.  You might also try installing the
                conda-env-{0} package to see if provides the required
                installer.
                """).lstrip().format(installer_type)
            )
            return -1

    write_activate_deactivate(env, prefix)

    touch_nonadmin(prefix)
    if not args.json:
        cli_install.print_activate(args.name if args.name else prefix)


def write_activate_deactivate(env, prefix):
    '''Write activate/deactivate environment variable/aliases scripts'''
    if not env.environment and not env.aliases:
        return

    # Create directories
    conda_dir = os.path.join(prefix, 'etc', 'conda')
    activate_dir = os.path.join(conda_dir, 'activate.d')
    deactivate_dir = os.path.join(conda_dir, 'deactivate.d')
    for directory in [conda_dir, activate_dir, deactivate_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Copy print_env.py
    import shutil
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), '..', 'print_env.py'),
        os.path.join(conda_dir, 'print_env.py'),
    )

    # Create activate and deactivate scripts
    if sys.platform == 'win32':
        ext = '.bat'
        source = 'call'
        rm = 'del'
        set_temp_file = '''set TEMP_FILE=\nfor /f "delims=" %%%%A in ('%s') do @set TEMP_FILE=%%%%A'''
        temp_file = '%TEMP_FILE%'
    else:
        ext = '.sh'
        source = 'source'
        rm = 'rm'
        set_temp_file = 'TEMP_FILE=`%s`'
        temp_file = '$TEMP_FILE'

    python_create_temp_file = 'python -c "import tempfile; print(tempfile.mkstemp(suffix=\\"%s\\")[1])"' % ext
    set_temp_file = set_temp_file % python_create_temp_file

    with open(os.path.join(activate_dir, '_activate' + ext), 'w') as activate:
        activate.write('%s\n' % set_temp_file)
        activate.write('python "%s" activate "%s" "%s" > %s\n' % \
            (os.path.join(conda_dir, 'print_env.py'), repr(env.environment), repr(env.aliases), temp_file))
        activate.write(source + ' %s\n' % temp_file)
        activate.write(rm + ' %s\n' % temp_file)

    with open(os.path.join(deactivate_dir, '_deactivate' + ext), 'w') as deactivate:
        deactivate.write('%s\n' % set_temp_file)
        deactivate.write('python "%s" deactivate "%s" "%s" > %s\n' % \
            (os.path.join(conda_dir, 'print_env.py'), repr(env.environment), repr(env.aliases), temp_file))
        deactivate.write(source + ' %s\n' % temp_file)
        deactivate.write(rm + ' %s\n' % temp_file)
