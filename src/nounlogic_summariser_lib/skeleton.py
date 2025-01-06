"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = nounlogic_summariser_lib.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import logging
import sys

from nounlogic_summariser_lib import __version__
from nounlogic_summariser_lib.summariser import process_file, load_config

__author__ = "nathfavour"
__copyright__ = "nathfavour"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from nounlogic_summariser_lib.skeleton import fib`,
# when using this Python module as a library.


def fib(n):
    """Fibonacci example function

    Args:
      n (int): integer

    Returns:
      int: n-th Fibonacci number
    """
    assert n > 0
    a, b = 1, 1
    for _i in range(n - 1):
        a, b = b, a + b
    return a


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Text Summarization Tool")
    subparsers = parser.add_subparsers(dest='command')

    # Summarize command
    summarize_parser = subparsers.add_parser('summarize', help='Summarize a text file')
    summarize_parser.add_argument('file', help='Path to the input file')
    summarize_parser.add_argument('--config', help='Path to config file', default='config.json')
    summarize_parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')

    return parser.parse_args(args)


def setup_logging(verbose):
    """Setup basic logging

    Args:
      verbose (bool): If True, set loglevel to DEBUG
    """
    loglevel = logging.DEBUG if verbose else logging.INFO
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Wrapper for CLI commands

    Args:
      args (List[str]): command line parameters as list of strings
    """
    args = parse_args(args)
    setup_logging(args.verbose)

    if args.command == 'summarize':
        _logger.info(f"Processing file: {args.file}")
        config = load_config(args.config)
        process_file(args.file, config)
        _logger.info("Summarization completed.")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m nounlogic_summariser_lib.skeleton 42
    #
    run()
