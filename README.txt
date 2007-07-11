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

zip/egg file import tracking
  bbfreeze tracks imports from zip files and includes whole egg files
  if some module is used from an eggfile. Packages using setuputils'
  pkg_resources module will now work (new in 0.95.0)

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
The preferred way to use bbfreeze is by writing short python scripts,
which use bbfreeze's API. Let's start with a short example::

  from bbfreeze import Freezer
  f = Freezer("hello-world-1.0", includes=("_strptime",))
  f.addScript("hello-world.py")
  f.addScript("hello-version.py")
  f()    # starts the freezing process


`bbfreeze.Freezer(distdir="dist", includes=(), excludes=())`
instantiates a Freezer object. It will create the frozen executables
and dependencies inside the `distdir` directory. `includes` is a list
or tuple of modules to include, `excludes` is a list or tuple of
modules to exclude. Note that the freezer will *delete* the directory
`distdir` before freezing!

bbfreeze.Freezer objects have the following members:

- `use_compression`: flag whether to use compression inside the created
  zipfile (default True).
- `include_py`: flag whether to create the included python interpreter
  `py` (default True)
- `addScript(path, gui_only=False)`: register a python script for
  freezing. `path` must be the path to a python script.
  The freezer will scan the file for dependencies and will create an
  executable with the same name in `distdir`. The `gui_only` flag only
  has a meaning on windows: If set, the executable created for this
  script will not open a console window.


Recipes
----------------------------------------------------------------------
Recipes provide a way to control the freezing process. Have a look at
bbfreeze/recipes.py if you need to implement your own. Note that the
API might change.


ChangeLog
======================================================================

2007-7-12       release 0.95.2
-----------------------------------------------
- fix issues with c modules with suffix 'module.so',
  e.g. zlibmodule.so, timemodule.so, ... (fedora core 7 uses that
  naming scheme; thanks to Neil Becker for reporting)
  The frozen executable did bail out with zipimport.ZipImportError:
  can't decompress data; zlib not available".

2007-7-11       release 0.95.1
-----------------------------------------------
- compile .py files from eggs when there is no accompanying .pyc file
- skip egg/zip files in find_all_packages (makes some recipes work)

2007-7-6       release 0.95.0
-----------------------------------------------
- support for egg files: bbfreeze scans zipped egg files and now
  includes whole egg files/directories in the distribution. Programs
  using setuptools' pkg_resources module will now work (thanks to
  Eirik Svendsen for testing this).

2007-6-28      release 0.94.1
-----------------------------------------------
- fix bug in setup script, now the patched modulegraph is really used
- better recipe handling

2007-6-22      release 0.94.0
-----------------------------------------------
- support relative imports (backported from modulefinder, bbfreeze now
  ships with its' own patched copy of modulegraph).
- fix xml/_xmlplus issues
- add recipe for cElementTree

2007-5-31      release 0.93.2
-----------------------------------------------
- include tcl/tk runtime files (really makes Tkinter work)
- exclude gtk, pango and friends (i.e. they must be installed on
  the target system)

2007-5-14      release 0.93.1
-----------------------------------------------
- make py executable work when readline is not installed
- fix dll search path issue (makes Tkinter work)

2007-5-3       release 0.93.0
-----------------------------------------------
- dependency on libpython.so should now always be recognized
- support for namespace packages
- basic support for zipfiles/eggs (bbfreeze will scan zipfiles/eggs
  for dependencies and will implement a dummy pkg_resources.require in
  frozen executables). Note that the remaining pkg_resources
  functionality just isn't available.
- documentation updates


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
