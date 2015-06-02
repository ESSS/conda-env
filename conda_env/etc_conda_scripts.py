from __future__ import print_function

import os
import sys


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
        os.path.join(os.path.dirname(__file__), 'print_env.py'),
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
