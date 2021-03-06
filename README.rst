=========
conda-env
=========

.. image:: https://travis-ci.org/conda/conda-env.svg
    :target: https://travis-ci.org/conda/conda-env

Provides the `conda env` interface to Conda environments.

Installing
----------

To install `conda env` with conda, run the following command in your root environment:

.. code-block:: bash

    $ conda install -c conda conda-env


Usage
-----
All of the usage is documented via the ``--help`` flag.

.. code-block:: bash

    $ conda env --help
    usage: conda-env [-h] {create,export,list,remove} ...

    positional arguments:
      {attach,create,export,list,remove,upload,update}
        attach              Embeds information describing your conda environment
                            into the notebook metadata
        create              Create an environment based on an environment file
        export              Export a given environment
        list                List the Conda environments
        remove              Remove an environment
        upload              Upload an environment to anaconda.org
        update              Updates the current environment based on environment
                            file

    optional arguments:
      -h, --help            show this help message and exit


``environment.yml``
-------------------
conda-env allows creating environments using the ``environment.yml``
specification file.  This allows you to specify a name, channels to use when
creating the environment, and the dependencies.  For example, to create an
environment named ``stats`` with numpy and pandas create an ``environment.yml``
file with this as the contents:

.. code-block:: yaml

    name: stats
    dependencies:
      - numpy
      - pandas

Then run this from the command line:

.. code-block:: bash

    $ conda env create
    Fetching package metadata: ...
    Solving package specifications: .Linking packages ...
    [      COMPLETE      ] |#################################################| 100%
    #
    # To activate this environment, use:
    # $ source activate numpy
    #
    # To deactivate this environment, use:
    # $ source deactivate
    #

Your output might vary a little bit depending on whether you have the packages
in your local package cache.

You can explicitly provide an environment spec file using ``-f`` or ``--file``
and the name of the file you would like to use.

The default channels can be excluded by adding ``nodefaults`` to the list of
channels. This is equivalent to passing the ``--override-channels`` option
to most ``conda`` commands, and is like ``defaults`` in the ``.condarc``
channel configuration but with the reverse logic.

Environment file example
------------------------

.. code-block:: yaml

    name: stats
    channels:
      - javascript
    dependencies:
      - python=3.4   # or 2.7 if you are feeling nostalgic
      - bokeh=0.9.2
      - numpy=1.9.*
      - nodejs=0.10.*
      - flask
      - pip:
        - Flask-Testing

**Recommendation:** Always create your `environment.yml` file by hand.

``environment.yml`` jinja2 rendering
------------------------------------

If you have ``jinja2`` available in the environment, ``environment.yml`` files will be
rendered with it before processing.

.. code-block:: yaml

    name: pytest
    dependencies:
    {% for i in ['xunit', 'coverage','mock'] %}
      - pytest-{{ i }}
    {% endfor %}

In this example, the previous file with ``jinja2`` syntax is equivalent to:

.. code-block:: yaml

    name: pytest
    dependencies:
      - pytest-xunit
      - pytest-coverage
      - pytest-mock


Available variables
^^^^^^^^^^^^^^^^^^^

When using ``jinja2``, on top of the usual template capabilities, you have access to the
following variables:

- ``root``: The directory containing ``environment.yml``
- ``os``: Python's ``os`` module.

``environment.yml`` with environment and aliases
------------------------------------------------

.. code-block:: yaml

    name: oracle
    dependencies:
      - oracle_instantclient

    # List type environment variables will be joined with os.pathsep (':' in unix, ';' in windows).
    # These values will be inserted in front of any existing value in the current environment.
    # e.g.:
    #   current PATH: "/usr/local/bin:/usr/bin"
    #   new     PATH: "{{ root }}/bin:/usr/local/bin:/usr/bin"
    environment:
      - ORACLE_HOME: /usr/local/oracle_instantclient
      - PATH:
        - {{ root }}/bin

    aliases:
      run_db: bash {{ root }}/bin/run_db.sh


Including other ``environment.yml`` files
-----------------------------------------

You can use an ``includes`` tag to include content from other ``environment.yml`` files.

This tag is a list of paths to other environment files:

.. code-block:: yaml

    name: project_a
    dependencies:
      - pytest

.. code-block:: yaml

    name: project_b
    dependencies:
      - pytest-xunit
    includes:
      - {{ root }}/project_a

In this example, the previous file for ``project_b`` is equivalent to:

.. code-block:: yaml

    name: project_b
    dependencies:
      - pytest
      - pytest-xunit


``conda-env`` will always try to maintain a proper dependency order (e.g. PATHs defined in ``A``
will appear before ``B``, or, an alias defined in ``A`` will be overridden by an alias with the
same name in ``B``).
