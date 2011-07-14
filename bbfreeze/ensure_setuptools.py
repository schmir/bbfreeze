#! /usr/bin/env python

"""
The sole purpose of this file is to start setup.py scripts with
setuptools already imported. 'pip install -e ...' installs
non-setuptools packages that look like development eggs. bbfreeze runs
setup.py bdist_egg for these, but that won't work since setuptools
didn't install it's code.

Can be used like:

  python -m bbfreeze.ensure_setuptools setup.py bdist_egg

or

  python -c 'from bbfreeze import ensure_setuptools; ensure_setuptools.main()' setup.py bdist_egg
"""

import sys, __main__
import setuptools  # don't remove


def main():
    del sys.argv[0]
    d = __main__.__dict__
    __main__.__file__ = sys.argv[0]
    execfile(sys.argv[0], d, d)


if __name__ == "__main__":
    main()
