#! /usr/bin/env python

import sys, os, re, commands

if sys.platform == 'win32':

    # -----------------------
    ## http://mail.python.org/pipermail/python-win32/2005-June/003446.html:
    ##
    ## Using it I found this: win32net.pyd from build 204 does *not* use the
    ## LsaLookupNames2 function in advapi32.dll.  However, win32net.pyd links
    ## to netapi32.dll (among others), and netapi32.dll links to advapi32.dll,
    ## using the name LsaLookupNames2.  This was on WinXP.

    ## On win2k, netapi32.dll will not link to advapi32's LsaLookupNames2 -
    ## otherwise it would not work.

    ## So, your exe *should* be able to run on win2k - except if you distribute
    ## XP's netapi32.dll with your exe (I've checked this with a trivial
    ## py2exe'd script).
    #
    # ----> EXCLUDE NETAPI32.DLL

    #-----------------------------------------
    # as found on the internet:
    # shlwapi.dll is installed as a tied component of Internet Explorer, and
    # the version should always match that of the installed version of Internet Explorer
    # so better exclude it
    #
    # ----> EXCLUDE SHLWAPI.DLL

    excludes = set(
        ['ADVAPI.DLL',
         'ADVAPI32.DLL',
         'COMCTL32.DLL',
         'COMDLG32.DLL',
         'CRTDLL.DLL',
         'DCIMAN32.DLL',
         'DDRAW.DLL',
         'GDI32.DLL',
         'GLU32.DLL',
         'GLUB32.DLL',
         'IMM32.DLL',
         'KERNEL32.DLL',
         'MFC42.DLL',
         'MSVCRT.DLL',
         'MSWSOCK.DLL',
         'NTDLL.DLL',
         'NETAPI32.DLL',
         'ODBC32.DLL',
         'OLE32.DLL',
         'OLEAUT32.DLL',
         'OPENGL32.DLL',
         'RPCRT4.DLL',
         'SHELL32.DLL',
         'SHLWAPI.DLL',
         'USER32.DLL',
         'VERSION.DLL',
         'WINMM.DLL',
         'WINSPOOL.DRV',
         'WS2HELP.DLL',
         'WS2_32.DLL',
         'WSOCK32.DLL',
         'MSVCR90.DLL',
         'POWRPROF.DLL',
         'SHFOLDER.DLL',
         'QUERY.DLL',
         ])

    def getImports(path):
        """Find the binary dependencies of PTH.

            This implementation walks through the PE header"""
        import pefile
        try:
            pe = pefile.PE(path, True)
            dlls = [x.dll for x in pe.DIRECTORY_ENTRY_IMPORT]
        except Exception, err:
            print "WARNING: could not determine binary dependencies for %r:%s" % (path, err)
            dlls = []
        return dlls

    _bpath = None

    def getWindowsPath():
        """Return the path that Windows will search for dlls."""
        global _bpath
        if _bpath is None:
            _bpath = []
            if sys.platform == 'win32':
                try:
                    import win32api
                except ImportError:

                    print "Warning: Cannot determine your Windows or System directories because pywin32 is not installed."
                    print "Warning: Either install it from http://sourceforge.net/projects/pywin32/ or"
                    print "Warning: add them to your PATH if .dlls are not found."
                else:
                    sysdir = win32api.GetSystemDirectory()
                    sysdir2 = os.path.join(sysdir, '../SYSTEM')
                    windir = win32api.GetWindowsDirectory()
                    _bpath = [sysdir, sysdir2, windir]
            _bpath.extend(os.environ.get('PATH', '').split(os.pathsep))
        return _bpath

    def _getDependencies(path):
        """Return a set of direct dependencies of executable given in path"""

        dlls = getImports(path)
        winpath = [os.path.dirname(os.path.abspath(path))] + getWindowsPath()
        deps = set()
        for dll in dlls:
            if exclude(dll):
                continue

            for x in winpath:
                fp = os.path.join(x, dll)
                if os.path.exists(fp):
                    deps.add(fp)
                    break
            else:
                print "WARNING: could not find dll %r needed by %r in %r" % (dll, path, winpath)
        return deps

    def exclude(fp):
        u = os.path.basename(fp).upper()
        return  u in excludes or u.startswith("API-MS-WIN-")

elif sys.platform.startswith("freebsd"):

    def _getDependencies(path):
        os.environ["P"] = path
        s = commands.getoutput("ldd $P")
        res = [x for x in re.compile(r"^ *.* => (.*) \(.*", re.MULTILINE).findall(s) if x]
        return res

    def exclude(fp):
        return bool(re.match(r"^/usr/lib/.*$", fp))

elif sys.platform.startswith("linux"):

    def _getDependencies(path):
        os.environ["P"] = path
        s = commands.getoutput("ldd $P")
        res = [x for x in re.compile(r"^ *.* => (.*) \(.*", re.MULTILINE).findall(s) if x]
        return res

    def exclude(fp):
        return re.match(r"^libc\.|^librt\.|^libcrypt\.|^libm\.|^libdl\.|^libpthread\.|^libnsl\.|^libutil\.|^ld-linux\.|^ld-linux-", os.path.basename(fp))
else:
    if sys.platform != 'darwin':
        print "Warning: don't know how to handle binary dependencies on this platform (%s)" % (sys.platform,)

    def _getDependencies(fp):
        return []

    def exclude(fp):
        return False

_cache = {}


def getDependencies(path):
    """Get direct and indirect dependencies of executable given in path"""
    def normedDeps(p):
        try:
            return _cache[p]
        except KeyError:
            r = set(os.path.normpath(x) for x in _getDependencies(p) if not exclude(x))
            _cache[p] = r
            return r

    if not isinstance(path, basestring):
        deps = set()
        for p in path:
            deps.update(getDependencies(p))
        return list(deps)

    deps = normedDeps(path)
    while True:
        newdeps = set(deps)  # copy
        for d in deps:
            newdeps.update(normedDeps(d))
        if deps == newdeps:
            return list(deps)
        deps = newdeps


def main():
    deps = set()
    deps = getDependencies(sys.argv[1:])
    deps = list(deps)
    deps.sort()
    print "\n".join(deps)


if __name__ == '__main__':
    main()
