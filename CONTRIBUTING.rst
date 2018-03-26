============
Contributing
============

Dev setup
---------

To install development dependencies, clone the package from Github, and run within the folder:

.. code-block::  bash

    pip install -e ".[dev]"

Run tests from the root folder:

.. code-block::  bash

    pytest

You can run tests against multiple pythons:

.. code-block::  bash

    tox

Note that this invocation is expected to fail in the coverage upload stage (it needs access token to upload coverage report)

To build the documentation, run ``make html`` from the docs folder:

.. code-block::  bash

    cd docs
    make html

Then you run a static HTML server from ``docs/build/html``.

.. code-block::  bash

    cd build/html
    python -m http.server

By default, the server will listen on http://0.0.0.0:8000.
