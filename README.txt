.. -*- mode: rst; coding: utf-8 -*-

======================================================================
bbfreeze - create standalone executables from python scripts
======================================================================


Overview
======================================================================
bbfreeze creates standalone executables from python scripts. It's
similar in purpose to the well known py2exe_ for windows, py2app_ for
OS X, PyInstaller_ and cx_Freeze_ (in fact it includes some bits from
cx_Freeze and PyInstaller. And it uses the modulegraph_ package,
which is also used by py2app).

It has the following features:

easy installation 
  bbfreeze can be installed with setuptools' easy_install command.

binary dependency tracking
  bbfreeze will track binary dependencies and will include DLLs and
  shared libraries needed by a frozen program.

multiple script freezing
  bbfreeze can freeze multiple scripts at once.

python interpreter included
  bbfreeze will create an extra executable named 'py', which might be
  used like the python executable itself.

bbfreeze works on windows and UNIX-like operating systems. It
currently does not work on OS X. bbfreeze has been tested with python
2.4 and 2.5. bbfreeze will not work with python versions prior to 2.3
as it uses the zipimport feature introduced with python 2.3.

Contact Information
-------------------
bbfreeze has been developed by `brainbot technologies AG`__. Questions
and suggestions should be send to schmir@gmail.com

Source
-------------------
Windows Eggs and the source code can be downloaded from 
http://cheeseshop.python.org/pypi/bbfreeze/.

http://systemexit.de/repo/bbfreeze carries a mercurial_ repository of
the in-development version.



Installation 
---------------
You need to have setuptools/easy_install installed. Installation
should be as easy as typing:
  
  $ easy_install bbfreeze

This should download bbfreeze and it's dependencies modulegraph and
altgraph and install them.

Limitations
---------------
- bbfreeze does not track dependencies inside zipped egg files.
- bbfreeze does not work on OS X
- documentation



bb-freeze - command line tool
======================================================================
bbfreeze provides a command line utility called bb-freeze, which
freezes all python scripts given on the command line into the
directory dist, which then contains for each script an executable and
all dependencies needed by those executables.

Example Usage::

  $ cat hello-world.py
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
  $ bb-freeze hello-world.py
  *** applied <function recipe_email at 0xb7ba702c>
  $ dist/hello-world
  hello world!
  ...
  $ dist/py
  Python 2.5.1c1 (r251c1:54692, Apr 11 2007, 01:40:50)
  [GCC 4.1.2 20061115 (prerelease) (Debian 4.1.1-21)] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  (MyConsole)
  >>> import email
  $

   
  

bbfreeze - API
======================================================================
The following code shows how to freeze scripts using the bbfreeze API::
  
  from bbfreeze import Freezer
  f = Freezer("hello-world-1.0", includes=("_strptime"))
  f.addScript("hello-world.py")
  f.addScript("hello-version.py")
  f()    # starts the freezing process



ChangeLog
======================================================================

2007-4-27       release 0.92.0
-----------------------------------------------
- better binary dependency cache handling
- fix recipe for time module on windows
- use pefile module on windows for binary dependency tracking
- add gui_only flag to addScript method (which builds GUI programs
  on windows, i.e. without console)
- strip shared libraries on non windows platforms
- add showxref method
- working recipe for py.magic.greenlet


2007-4-24	Initial release 0.91.0
-----------------------------------------------


.. _py2exe: http://www.py2exe.org/
.. _py2app: http://undefined.org/python/#py2app
.. _PyInstaller: http://pyinstaller.python-hosting.com/
.. _cx_Freeze: http://www.python.net/crew/atuining/cx_Freeze/
.. _modulegraph: http://undefined.org/python/#modulegraph
.. __: http://brainbot.com
.. _mercurial: http://www.selenic.com/mercurial/wiki/
