#! /usr/bin/env python

import sys
import os
import re
import cPickle

if sys.platform=='win32':

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
         'WSOCK32.DLL'])


    def getImports(path):
        """Find the binary dependencies of PTH.

            This implementation walks through the PE header"""
        import pefile
        pe=pefile.PE(path, True)
        dlls = [x.dll for x in pe.DIRECTORY_ENTRY_IMPORT]
        return dlls



    _bpath = None
    def getWindowsPath():
        """Return the path that Windows will search for dlls."""
        global _bpath
        if _bpath is None:
            _bpath = []
            if sys.platform=='win32':
                try:
                    import win32api
                except ImportError:
                    print "Warning: Cannot determine your Windows or System directories"
                    print "Warning: Please add them to your PATH if .dlls are not found"
                    print "Warning: or install starship.python.net/skippy/win32/Downloads.html"
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
        winpath = getWindowsPath()
        deps = set()
        for dll in dlls:
            if dll.upper() in excludes:
                continue

            for x in winpath:
                fp = os.path.join(x, dll)
                if os.path.exists(fp):
                    deps.add(fp)
                    break
        return deps

    def exclude(fp):
        return os.path.basename(fp).upper() in excludes
        
elif sys.platform=='darwin':
    def _getDependencies(fp):
        return []

    def exclude(fp):
        return False
    
else:    
    def _getDependencies(path):
        os.environ["P"] = path
        s=os.popen4("ldd $P")[1].read()
        res = [x for x in re.compile(r"^ *.* => (.*) \(.*", re.MULTILINE).findall(s) if x]
        return res

    
    def exclude(fp):
        return re.match(r"^libc\.|^libcrypt\.|^libm\.|^libdl\.|^libpthread\.|^libnsl\.|^libutil\.", os.path.basename(fp))


class Cache(object):
    def __init__(self):
        self.c = {}

        try:
            uname = os.uname()
        except:
            uname = sys.platform

        self.machine_id = str((uname,
                              os.environ.get("LD_LIBRARY_PATH"),
                              os.environ.get("DYLD_LIBRARY_PATH"),
                              os.environ.get("PATH")))

        self.cachedir = None
        try:
            cachedir = self.getCachedir()
            if cachedir is None:
                return

            if not os.path.exists(cachedir):
                os.makedirs(cachedir)
            self.cachedir = cachedir
            print "using binary dependency cache in %r" % (self.cachedir,)
        except Exception, err:
            print "Error while trying to create cachedir:", err
     
    def getCachedir(self):
        if sys.platform=='win32':
            appdata = os.environ.get("APPDATA")
            if appdata:
                cachedir = os.path.join(appdata, "bbfreeze", "cache")
            else:
                cachedir = None
        else:
            cachedir = os.path.expanduser("~/.bbfreeze/cache")
            if cachedir.startswith("~"):
                print "Not using cachedir (environment variable HOME not set.)"
                cachedir = None

        return cachedir




        
    def computeId(self, *args):
        import StringIO
        import md5

        f=StringIO.StringIO()
        print >>f, "regular expression bug fixed"
        for x in args:
            print >>f, x
        m=md5.new()
        m.update(f.getvalue())
        return m.hexdigest()


    def _getcachepath(self, fp):
        f=os.stat(fp)
        p = os.path.join(self.cachedir, self.computeId(self.machine_id, fp, f.st_mtime, f.st_size))
        return p
    
    def __getitem__(self, fp):
        try:
            return self.c[fp]
        except:
            pass

        if self.cachedir is not None:            
            p = self._getcachepath(fp)
            if os.path.exists(p):
                return cPickle.loads(open(p, 'rb').read())
        
        raise KeyError()

    def __setitem__(self, fp, val):
        self.c[fp] = val
        if self.cachedir is None:
            return
        
        p = self._getcachepath(fp)
        open(p, 'wb').write(cPickle.dumps(val))
                            
        

        
_cache = Cache()

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
        newdeps = set(deps) # copy
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
        

if __name__=='__main__':
    main()
