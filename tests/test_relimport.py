#! /usr/bin/env py.test

import sys

if sys.version_info >= (2, 5):
    def test_freeze_relimport():
        from bbfreeze import Freezer
        f = Freezer(includes=['relimport'])
        f()

if __name__ == '__main__':
    test_freeze_relimport()
