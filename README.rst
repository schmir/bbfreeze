.. -*- mode: rst; coding: utf-8 -*-

======================================================================
bbfreeze - create stand-alone executables from python scripts
======================================================================

:Authors: Ralf Schmitt <ralf@systemexit.de>
:Version: 1.0.0
:Date:    2012-02-08
:Download: http://pypi.python.org/pypi/bbfreeze
:Code: https://github.com/schmir/bbfreeze


Overview
======================================================================
bbfreeze creates stand-alone executables from python scripts. It's
similar in purpose to the well known py2exe_ for windows, py2app_ for
OS X, PyInstaller_ and cx_Freeze_ (in fact ancient versions were based
on cx_Freeze. And it uses the modulegraph_ package, which is also used by
py2app).

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

automatic pathname rewriting
  pathnames in tracebacks are replaced with relative pathnames
  (i.e. if you import package foo.bar from /home/jdoe/pylib/
  tracebacks generated from functions in foo.bar will not show your
  local path /home/jdoe/pylib/foo/bar.py. They will instead show
  foo/bar.py)

distutils command 'bdist_bbfreeze'
  A new distutils/setuptools command bdist_bbfreeze integrates
  bbfreeze into your setup.py.

bbfreeze works on windows and UNIX-like operating systems. bbfreeze
has been tested with python 2.4, 2.5, 2.6 and 2.7 bbfreeze will not
work with python 3 or higher.

Contact Information
-------------------
bbfreeze has been developed by `brainbot technologies AG`__. Questions
and suggestions should be send to the bbfreeze-users mailing list:
bbfreeze-users@googlegroups.com

You can subscribe by sending email to
bbfreeze-users-subscribe@googlegroups.com

An archive is available at 
http://groups.google.com/group/bbfreeze-users

You can also reach the author via email to ralf@systemexit.de

Source
-------------------
Windows Eggs and the source code can be downloaded from 
http://pypi.python.org/pypi/bbfreeze/.

The source code is maintained in a git repository on github:
https://github.com/schmir/bbfreeze

Use::

  git clone https://github.com/schmir/bbfreeze.git

to create a copy of the repository, then::

  git pull

inside the copy to receive the latest version.



Installation 
---------------
You need to have setuptools/easy_install installed. Installation
should be as easy as typing::
  
  easy_install bbfreeze

This should download bbfreeze and it's dependencies modulegraph and
altgraph and install them.

Limitations
---------------
- documentation is a bit sparse


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
  WARNING: found encodings in multiple directories. Assuming it's a namespace package. (found in /home/ralf/py27/lib/python2.7/encodings, /usr/lib/python2.7/encodings)
  *** applied <function recipe_doctest at 0x1f01aa0>
  *** applied <function recipe_time at 0x1f01de8>
  *** applied <function recipe_urllib at 0x1f01c08>
  RPATH ${ORIGIN}:${ORIGIN}/../lib is fine
  $ dist/hello-world
  hello world!
  sys.path: ['/home/ralf/bbfreeze/tests/dist/library.zip', '/home/ralf/bbfreeze/tests/dist']
  __file__: hello-world.py
  __name__: __main__
  locals(): {'__builtins__': <module '__builtin__' (built-in)>, '__file__': 'hello-world.py', '__package__': None, 'sys': <module 'sys' (built-in)>, 'email': <module 'email' from '/home/ralf/bbfreeze/tests/dist/library.zip/email/__init__.pyc'>, '__name__': '__main__', '__doc__': None}
  sys.argv ['/home/ralf/bbfreeze/tests/dist/hello-world']
  sys.executable: /home/ralf/bbfreeze/tests/dist/hello-world
  $ dist/py
  Python 2.7.2 (default, Nov 21 2011, 17:25:27)
  [GCC 4.6.2] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  (MyConsole)
  >>> import email
  >>>


bdist_bbfreeze - distutils command
======================================================================

bbfreeze provides a distutils command which works much like the
'bb-freeze' command line tool, but integrates nicely into distutils
and setuptools. It collects all 'console_scripts' 'gui_scripts'
entry-points, generates the wrapper scripts (like easy_install would
do) and freezes these scripts.

After installing bbfreeze, every setup.py which used setuptools, has a
new command 'bdist_bbfreeze'. To show the help message just run::

  python setup.py bdist_bbfreeze --help

Usage examples::

  # freeze all scripts into ./dist/<egg_name>-<egg_version>/
  python setup.py bdist_bbfreeze

  # same, but use tagging for "daily build" or "snapshot" releases
  python setup.py egg_info --tag-build=dev bdist_bbfreeze



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


Linux Notes
======================================================================
The glibc version on the system used for freezing will generally be
the minimum glibc version required to run the binaries.

gtk, gdk, pango, glib shared libraries will not be copied by the
freezing process. Those need a rather complicated runtime system and
copying them would probably only lead to problems.

Windows Notes
======================================================================
binaries created with python 2.6 or 2.7 will need the Microsoft Visual
C++ 2008 Redistributable Package (either the 32bit_ or the 64bit_ version) installed on the target
machine.


Change-Log
======================================================================
2012-02-08         release 1.0.0
-----------------------------------------------
- better test infrastructure
- update documentation
- remove bbfreeze.macholib
- fix build on ubuntu 11.10
- handle platform=='linux3' case in ensureRPath
- make py recipe work again.
- handle "pip -e" installed development eggs, that aren't even setuptools packages


2011-04-12         release 0.97.3
-----------------------------------------------
- exclude ms-win-api-* and query.dll.
- make py parse minimal set of options required to run py.test on the
  frozen executable.
- link with /LARGEADDRESSAWARE on win32
- ensure RPATH of application loader has the right value. try to fix
  it with patchelf if not.
- set dont_write_bytecode and no_user_site flags if they are
  available.
- handle pip installed namespace packages

2010-10-12         release 0.97.2
-----------------------------------------------
- workaround console.exe not being executable.
- switch to ez_setup.py from setuptools-0.6c11.
- make win32com work by using a temporary directory as it's
  __gen_path__.

2010-08-19         release 0.97.1
-----------------------------------------------
- add missing README.rst file.

2010-08-17         release 0.97.0
-----------------------------------------------
- make it compatible with latest altgraph
- add recipe for gevent
- fix build on latest ubuntu

2008-09-18         release 0.96.5
-----------------------------------------------
- added distutils command 'bdist_bbfreeze' contributed by Hartmut
  Goebel
- executables are now stripped with the 'strip' command. This makes a
  difference in file size when using a static libpython.a.

2008-8-29         release 0.96.4
-----------------------------------------------
- record previously missing dependencies for subpackage imports. This
  bug only showed up when dependencies where explicitly removed.

2008-8-18	  release 0.96.3
-----------------------------------------------
- fix issues with some packages, which where wrongly
  recognized as development eggs

2008-8-5	  release 0.96.2
-----------------------------------------------
- a slightly patched getpath.c from python trunk has been
  added. This should fix sys.getfilesystemencoding() for statically
  linked python. We also try to link with the static library in case
  the shared one has been linked with -Bsymbolic (which makes it
  impossible to override the necessary symbols). This happens e.g. on
  Ubuntu 8.04.
- __file__ in the main program now has a .py suffix. This prevents
  garbage output from the warnings module.
- some recipes have been added (mostly breaking some unneeded
  dependencies).
- explicit recipes for the email module have been added. the email
  module isn't added as a whole.
- the setup script now reports the configuration used.
- bbfreeze now tracks dependencies from eggs (i.e. dependencies
  specified in the egg's setup.py script).


2008-3-14         release 0.96.1
-----------------------------------------------
- fix bug in an internal function, which determines if eggs should 
  be used. It always returned False, so eggs where never packaged.

2008-3-13         release 0.96.0
-----------------------------------------------
- some egg packages have the site-packages directory as their
  location, which resulted in the whole site-packages directory being 
  copied as some egg file.
- fix issue with wxPython
- add recipe for mercurial
- handle development eggs ("python setup.py develop") by running
  setup.py bdist_egg
- handle easy install entry scripts
- add recipe for kinterbasdb (thanks to Werner F. Bruhin)
- fix LD_RUN_PATH issue, when --enable--new-dtags is the default for
  linking (e.g. on gentoo). (thanks to Collin Day)

2007-12-6         release 0.95.4
-----------------------------------------------
- workaround for virtualenv
- show execution time in py

2007-10-16        release 0.95.3
-----------------------------------------------
- recipes for pythoncom/pywintypes have been added
- make sys.getfilesystemencoding() work like in non-frozen versions
- automatic pathname rewriting
- make stdin, stdout and stderr unbuffered in frozen programs


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

LICENSE
======================================================================
bbfreeze contains a modified copy of modulegraph, which is distributed
under the MIT license and is copyrighted by Bob Ippolito.

bbfreeze contains a modified copy of getpath.c from the python
distribution, which is distributed under the python software
foundation license version 2 and copyrighted by the python software
foundation.

bbfreeze includes a module 'bdist_bbfreeze.py' which is

  Copyright 2008-2012 by Hartmut Goebel <h.goebel@goebel-consult.de>

The 'bdist_bbfreeze' module may be distributed under the same licence
as bbfreeze itself.


The remaining part is distributed under the zlib/libpng license:

Copyright (c) 2007-2012 brainbot technologies AG

This software is provided 'as-is', without any express or implied
warranty. In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required.

2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.

3. This notice may not be removed or altered from any source
   distribution.

.. _py2exe: http://www.py2exe.org/
.. _py2app: http://undefined.org/python/#py2app
.. _PyInstaller: http://pyinstaller.python-hosting.com/
.. _cx_Freeze: http://www.python.net/crew/atuining/cx_Freeze/
.. _modulegraph: http://undefined.org/python/#modulegraph
.. __: http://brainbot.com
.. _32bit: http://www.microsoft.com/downloads/en/details.aspx?familyid=9B2DA534-3E03-4391-8A4D-074B9F2BC1BF
.. _64bit: http://www.microsoft.com/downloads/en/details.aspx?FamilyID=BD2A6171-E2D6-4230-B809-9A8D7548C1B6
