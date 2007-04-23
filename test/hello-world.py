#! /usr/bin/env python

import sys
import email

print unicode("hello", "utf8"), unicode("world!", "ascii")

print "sys.path:", sys.path
print "__file__:", __file__
print "__name__:", __name__

print "locals():", locals()

print "sys.argv", sys.argv
print "sys.executable:", sys.executable
