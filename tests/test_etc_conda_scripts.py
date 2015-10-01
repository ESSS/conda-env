import os
import shutil
import sys
import textwrap
import unittest

from conda_env import env
from conda_env.etc_conda_scripts import write_activate_deactivate

from . import utils


class activate_deactivate_TestCase(unittest.TestCase):
    _ENV = env.Environment(environment=[{'FOO' : 'BAR'}], aliases={'my_ls' : 'ls -la'})
    _CONDA_DIR = utils.support_file('conda')
    _PREFIX = os.path.join(_CONDA_DIR, 'envs', 'test_write_activate_deactivate')
    _OBTAINED_PRINT_ENV = os.path.join(_PREFIX, 'etc', 'conda', 'print_env.py')
    _EXPECTED_PRINT_ENV = os.path.join(
        os.path.dirname(__file__),
        '..',
        'conda_env',
        'print_env.py'
    )

    def test_write_activate_deactivate_unix(self):
        old_platform = sys.platform
        sys.platform = 'linux2'
        try:
            write_activate_deactivate(self._ENV, self._PREFIX)

            with open(os.path.join(self._PREFIX, 'etc', 'conda', 'activate.d', '_activate.sh')) as activate:
                self.assertEqual(activate.read(), textwrap.dedent(
                    '''
                    TEMP_FILE=`python -c "import tempfile; print(tempfile.mkstemp(suffix=\\".sh\\")[1])"`
                    python "%s" activate "[{\'FOO\': \'BAR\'}]" "{\'my_ls\': \'ls -la\'}" > $TEMP_FILE
                    source $TEMP_FILE
                    rm $TEMP_FILE
                    '''
                ).lstrip() % self._OBTAINED_PRINT_ENV)

            with open(os.path.join(self._PREFIX, 'etc', 'conda', 'deactivate.d', '_deactivate.sh')) as deactivate:
                self.assertEqual(deactivate.read(), textwrap.dedent(
                    '''
                    TEMP_FILE=`python -c "import tempfile; print(tempfile.mkstemp(suffix=\\".sh\\")[1])"`
                    python "%s" deactivate "[{\'FOO\': \'BAR\'}]" "{\'my_ls\': \'ls -la\'}" > $TEMP_FILE
                    source $TEMP_FILE
                    rm $TEMP_FILE
                    '''
                ).lstrip() % self._OBTAINED_PRINT_ENV)

            with open(self._OBTAINED_PRINT_ENV) as obtained_print_env:
                with open(self._EXPECTED_PRINT_ENV) as expected_print_env:
                    self.assertEqual(obtained_print_env.read(), expected_print_env.read())
        finally:
            sys.platform = old_platform
            shutil.rmtree(self._CONDA_DIR)


    def test_write_activate_deactivate_win(self):
        if sys.platform != 'win32':
            return

        try:
            write_activate_deactivate(self._ENV, self._PREFIX)

            with open(os.path.join(self._PREFIX, 'etc', 'conda', 'activate.d', '_activate.bat')) as activate:
                self.assertEqual(activate.read(), textwrap.dedent(
                    '''
                    set TEMP_FILE=
                    for /f "delims=" %%%%A in (\'python -c "import tempfile; print(tempfile.mkstemp(suffix=\\".bat\\")[1])"\') do @set TEMP_FILE=%%%%A
                    python "%s" activate "[{\'FOO\': \'BAR\'}]" "{\'my_ls\': \'ls -la\'}" > %%TEMP_FILE%%
                    call %%TEMP_FILE%%
                    del %%TEMP_FILE%%
                    '''
                ).lstrip() % self._OBTAINED_PRINT_ENV)

            with open(os.path.join(self._PREFIX, 'etc', 'conda', 'deactivate.d', '_deactivate.bat')) as deactivate:
                self.assertEqual(deactivate.read(), textwrap.dedent(
                    '''
                    set TEMP_FILE=
                    for /f "delims=" %%%%A in (\'python -c "import tempfile; print(tempfile.mkstemp(suffix=\\".bat\\")[1])"\') do @set TEMP_FILE=%%%%A
                    python "%s" deactivate "[{\'FOO\': \'BAR\'}]" "{\'my_ls\': \'ls -la\'}" > %%TEMP_FILE%%
                    call %%TEMP_FILE%%
                    del %%TEMP_FILE%%
                    '''
                ).lstrip() % self._OBTAINED_PRINT_ENV)

            with open(self._OBTAINED_PRINT_ENV) as obtained_print_env:
                with open(self._EXPECTED_PRINT_ENV) as expected_print_env:
                    self.assertEqual(obtained_print_env.read(), expected_print_env.read())
        finally:
            shutil.rmtree(self._CONDA_DIR)
