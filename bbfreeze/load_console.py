#! /usr/bin/env python

import sys, os, zlib, zipimport

installdir = os.path.normpath(os.path.dirname(sys.path[0]))  # sys.path[0] == '.../library.zip'


def find_eggs():
    for x in os.listdir(installdir):
        if x.endswith(".egg"):
            fp = os.path.join(installdir, x)
            sys.path.append(fp)

find_eggs()


def addldlibrarypath():

    if sys.platform == 'darwin':
        LD_LIBRARY_PATH = 'DYLD_LIBRARY_PATH'
    else:
        LD_LIBRARY_PATH = 'LD_LIBRARY_PATH'

    #p = os.path.normpath(os.path.dirname(sys.executable))
    p = installdir
    try:
        paths = os.environ[LD_LIBRARY_PATH].split(os.pathsep)
    except KeyError:
        paths = []

    if p not in paths:
        paths.insert(0, p)
        os.environ[LD_LIBRARY_PATH] = os.pathsep.join(paths)
        #print "SETTING", LD_LIBRARY_PATH, os.environ[LD_LIBRARY_PATH]
        os.execv(sys.executable, sys.argv)


def addpath():
    # p = os.path.normpath(os.path.dirname(sys.executable))
    p = installdir
    try:
        paths = os.environ['PATH'].split(os.pathsep)
    except KeyError:
        paths = []

    if p not in paths:
        paths.insert(0, p)
        os.environ['PATH'] = os.pathsep.join(paths)
        #print "SETTING PATH:", os.environ['PATH']


def addtcltk():
    libtk = os.path.join(installdir, "lib-tk")
    libtcl = os.path.join(installdir, "lib-tcl")

    if os.path.isdir(libtk):
        os.environ['TK_LIBRARY'] = libtk

    if os.path.isdir(libtcl):
        os.environ['TCL_LIBRARY'] = libtcl


def fixwin32com():
    """setup win32com to 'genpy' in a tmp directory
    """
    if sys.platform != 'win32':
        return

    # hide imports by using exec. bbfreeze analyzes this file.
    exec """
try:
    import win32com.client
    import win32com.gen_py
    import win32api
except ImportError:
    pass
else:
    win32com.client.gencache.is_readonly=False
    tmpdir = os.path.join(win32api.GetTempPath(),
                          "frozen-genpy-%s%s" % sys.version_info[:2])
    if not os.path.isdir(tmpdir):
        os.makedirs(tmpdir)
    win32com.__gen_path__ = tmpdir
    win32com.gen_py.__path__=[tmpdir]
"""

#print "EXE:", sys.executable
#print "SYS.PATH:", sys.path

addpath()
#if sys.platform!='win32': # and hasattr(os, 'execv'):
#    addldlibrarypath()

addtcltk()

try:
    import encodings
except ImportError:
    pass

fixwin32com()

exe = os.path.basename(sys.argv[0])
if exe.lower().endswith(".exe"):
    exe = exe[:-4]


m = __import__("__main__")

# add '.py' suffix to prevent garbage from the warnings module
m.__dict__['__file__'] = exe + '.py'
exe = exe.replace(".", "_")
importer = zipimport.zipimporter(sys.path[0])
while 1:
    # if exe is a-b-c, try loading a-b-c, a-b and a
    try:
        code = importer.get_code("__main__%s__" % exe)
    except zipimport.ZipImportError, err:
        if '-' in exe:
            exe = exe[:exe.find('-')]
        else:
            raise err
    else:
        break
if exe == "py":
    exec code
else:
    exec code in m.__dict__
