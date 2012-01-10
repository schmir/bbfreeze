#! /usr/bin/env python

import sys, os
print sys.getfilesystemencoding(), os.environ.get("LANG", "<>")
