import os
import sys
import re
import time
import shutil
import struct
import zipfile
import imp
import marshal
import zipimport
import commands

from modulegraph import modulegraph
modulegraph.ReplacePackage("_xmlplus", "xml")

# workaround for win32com hacks.
# see: http://starship.python.net/crew/theller/moin.cgi/WinShell

try:
    import win32com
    for p in win32com.__path__[1:]:
        modulegraph.AddPackagePath("win32com", p)
    for extra in ["win32com.shell", "win32com.mapi"]:
        try:
            __import__(extra)
        except ImportError:
            continue
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulegraph.AddPackagePath(extra, p)
except ImportError:
    pass

try:
    import xml
except ImportError:
    pass
else:
    for p in xml.__path__:
        modulegraph.AddPackagePath("xml", p)

from bbfreeze import recipes, eggutil

try:
    import pkg_resources
except ImportError:
    pkg_resources = None


class EggAnalyzer(object):
    def __init__(self):
        self.used = set()

        if pkg_resources is None:
            return

        self.locations = [x.location for x in list(pkg_resources.working_set)]
        self.usable = None

    def add(self, dist):
        if dist in self.used:
            return

        self.used.add(dist)
        deps = pkg_resources.working_set.resolve(dist.requires())
        for x in deps:
            if x not in self.used:
                print "adding %s as a dependency of %s" % (x, dist)
                self.used.add(x)

    def usableWorkingSet(self):
        from distutils.sysconfig import get_python_lib as gl
        pathcount = {}
        for lib in [gl(0, 0), gl(0, 1), gl(1, 0), gl(1, 1)]:
            pathcount[lib] = 2
            pathcount[os.path.realpath(lib)] = 2  # handle symlinks!

        for x in pkg_resources.working_set:
            try:
                pathcount[x.location] += 1
            except KeyError:
                pathcount[x.location] = 1

        def is_good(dist):
            if dist.project_name == "bbfreeze":
                return False

            if not dist.has_metadata("top_level.txt"):
                return False

            if type(dist._provider) == pkg_resources.FileMetadata:  # no real egg
                return False

            return True

        ws = []
        for x in pkg_resources.working_set:
            if pathcount[x.location] == 1 and is_good(x):
                x._freeze_usable = True
                ws.append(x)
            else:
                x._freeze_usable = False
        return ws

    def findDistribution(self, m):
        if isinstance(m, modulegraph.Script):
            return None

        if pkg_resources is None:
            return None
        if m.filename is None:
            return None
        if self.usable is None:
            self.usable = self.usableWorkingSet()

        fn = m.filename
        for dist in self.usable:
            if fn.startswith(dist.location):
                # do not include eggs if this is a namespace package
                # e.g. "import zope" can find any of "zope.deferredimport", "zope.interface",...
                if dist.has_metadata("namespace_packages.txt"):
                    ns = list(dist.get_metadata_lines("namespace_packages.txt"))
                    if isinstance(m, modulegraph.Package) and m.identifier in ns:
                        #print "SKIP:", ns, m
                        return None

                self.add(dist)
                return dist

    def report(self):
        tmp = [(x.project_name, x) for x in self.used]
        tmp.sort()
        if tmp:
            print "=" * 50
            print "The following eggs are being used:"
            for x in tmp:
                print repr(x[1])
            print "=" * 50

    def copy(self, destdir):
        for x in self.used:
            if x._freeze_usable:
                eggutil.copyDistribution(x, destdir)
            else:
                try:
                    path = x._provider.path
                except AttributeError:
                    print "Warning: cannot copy egg-info for", x
                    continue
                print "Copying egg-info of %s from %r" % (x, path)
                shutil.copy2(path, destdir)


def fullname(p):
    return os.path.join(os.path.dirname(__file__), p)


def getRecipes():
    res = []
    for x in dir(recipes):
        if x.startswith("recipe_"):
            r = getattr(recipes, x)
            if r:
                res.append(r)

    return res


class SharedLibrary(modulegraph.Node):
    def __init__(self, identifier):
        self.graphident = identifier
        self.identifier = identifier
        self.filename = None


class Executable(modulegraph.Node):
    def __init__(self, identifier):
        self.graphident = identifier
        self.identifier = identifier
        self.filename = None


class CopyTree(modulegraph.Node):
    def __init__(self, identifier, dest):
        self.graphident = identifier
        self.identifier = identifier
        self.filename = identifier
        self.dest = dest


class ZipModule(modulegraph.BaseModule):
    pass


class MyModuleGraph(modulegraph.ModuleGraph):
    def _find_single_path(self, name, p, parent=None):
        """find module or zip module in directory or zipfile p"""
        if parent is not None:
            # assert path is not None
            fullname = parent.identifier + '.' + name
        else:
            fullname = name

        try:
            return modulegraph.ModuleGraph.find_module(self, name, [p], parent)
        except ImportError, err:
            pass

        if not os.path.isfile(p):
            raise err

        zi = zipimport.zipimporter(p)
        m = zi.find_module(fullname.replace(".", "/"))
        if m:
            code = zi.get_code(fullname.replace(".", "/"))
            return zi, p, ('', '', 314)
        raise err

    def copyTree(self, source, dest, parent):
        n = self.createNode(CopyTree, source, dest)
        self.createReference(parent, n)

    def find_module(self, name, path, parent=None):
        paths_seen = set()

        if parent is not None:
            # assert path is not None
            fullname = parent.identifier + '.' + name
        else:
            fullname = name

        #print "FIND_MODULE:", name, path, parent

        if path is None:
            path = self.path

        found = []

        def append_if_uniq(r):
            for t in found:
                if r[1] == t[1]:
                    return
            found.append(r)

        for p in path:
            try:
                p = os.path.normcase(os.path.normpath(os.path.abspath(p)))
                if p in paths_seen:
                    continue
                paths_seen.add(p)
                #res = modulegraph.ModuleGraph.find_module(self, name, [p], parent)
                res = self._find_single_path(name, p, parent)
                if found:
                    if res[2][2] == imp.PKG_DIRECTORY:
                        append_if_uniq(res)
                else:
                    if res[2][2] == imp.PKG_DIRECTORY:
                        append_if_uniq(res)
                    else:
                        return res
            except ImportError, err:
                pass

        if len(found) > 1:
            print "WARNING: found %s in multiple directories. Assuming it's a namespace package. (found in %s)" % (
                fullname, ", ".join(x[1] for x in found))
            for x in found[1:]:
                modulegraph.AddPackagePath(fullname, x[1])

        if found:
            return found[0]

        raise err

    def load_module(self, fqname, fp, pathname, (suffix, mode, typ)):
        if typ == 314:
            m = self.createNode(ZipModule, fqname)
            code = fp.get_code(fqname.replace(".", "/"))
            m.filename = fp.archive
            m.packagepath = [fp.archive]
            m.code = code
            m.is_package = fp.is_package(fqname.replace(".", "/"))

            self.scan_code(m.code, m)
            return m
        else:
            return modulegraph.ModuleGraph.load_module(self, fqname, fp, pathname, (suffix, mode, typ))


def replace_paths_in_code(co, newname):
    import new
    if newname.endswith('.pyc'):
        newname = newname[:-1]

    consts = list(co.co_consts)

    for i in range(len(consts)):
        if isinstance(consts[i], type(co)):
            consts[i] = replace_paths_in_code(consts[i], newname)

    return new.code(co.co_argcount, co.co_nlocals, co.co_stacksize,
                     co.co_flags, co.co_code, tuple(consts), co.co_names,
                     co.co_varnames, newname, co.co_name,
                     co.co_firstlineno, co.co_lnotab,
                     co.co_freevars, co.co_cellvars)

# NOTE: the try: except: block in this code is not necessary under Python 2.4
# and higher and can be removed once support for Python 2.3 is no longer needed
EXTENSION_LOADER_SOURCE = \
"""
import sys
import os
import imp

found = False
for p in sys.path:
    if not os.path.isdir(p):
        continue
    f = os.path.join(p, "%s")
    if not os.path.exists(f):
        continue
    try:
        m = imp.load_dynamic(__name__, f)
    except ImportError:
        del sys.modules[__name__]
        raise
    sys.modules[__name__] = m
    found = True
    break
if not found:
    del sys.modules[__name__]
    raise ImportError, "No module named %%s" %% __name__
"""


def get_implies():
    implies = {
        "wxPython.wx": modulegraph.Alias('wx'),
        }

    try:
        from email import _LOWERNAMES, _MIMENAMES
    except ImportError:
        return implies

    for x in _LOWERNAMES:
        implies['email.' + x] = modulegraph.Alias('email.' + x.lower())
    for x in _MIMENAMES:
        implies['email.MIME' + x] = modulegraph.Alias('email.mime.' + x.lower())

    return implies


class Freezer(object):
    use_compression = True
    include_py = True
    implies = get_implies()

    def __init__(self, distdir="dist", includes=(), excludes=()):
        self.distdir = os.path.abspath(distdir)
        self._recipes = None

        self.mf = MyModuleGraph(excludes=excludes, implies=self.implies, debug=0)

        # workaround for virtualenv's distutils monkeypatching
        import distutils
        self.mf.load_package("distutils", distutils.__path__[0])

        self._loaderNode = None
        if sys.platform == 'win32':
            self.linkmethod = 'loader'
        else:
            self.linkmethod = 'hardlink'

        self.console = fullname("console.exe")
        if sys.platform == 'win32':
            self.consolew = fullname("consolew.exe")

        self._have_console = False
        self.binaries = []

        for x in includes:
            self.addModule(x)

    def _get_mtime(self, fn):
        if fn and os.path.exists(fn):
            mtime = os.stat(fn).st_mtime
        else:
            mtime = time.time()
        return mtime

    def _entry_script(self, path):
        f = open(path, 'r')
        lines = [f.readline(), f.readline()]
        del f
        eicomment = "# EASY-INSTALL-ENTRY-SCRIPT: "
        for line in lines:
            if line.startswith(eicomment):
                values = [x.strip("'\"") for x in line[len(eicomment):].strip().split(",")]
                print path, "is an easy install entry script. running pkg_resources.require(%r)" % (values[0],)
                pkg_resources.require(values[0])
                ep = pkg_resources.get_entry_info(*values)
                print "entry point is", ep
                return ep.module_name
        return None

    def addScript(self, path, gui_only=False):
        dp = os.path.dirname(os.path.abspath(path))
        self.mf.path.insert(0, dp)
        ep_module_name = self._entry_script(path)
        s = self.mf.run_script(path)
        s.gui_only = gui_only
        del self.mf.path[0]
        if ep_module_name:
            self.mf.import_hook(ep_module_name, s)

    def addModule(self, name):
        if name.endswith(".*"):
            self.mf.import_hook(name[:-2], fromlist="*")
        else:
            if name not in sys.builtin_module_names:
                self.mf.import_hook(name)

    def _add_loader(self):
        if self._loaderNode is not None:
            return
        loader = fullname("load_console.py")
        assert os.path.exists(loader)

        m = self.mf.run_script(loader)
        self._loaderNode = m

    def _handleRecipes(self):
        if self._recipes is None:
            self._recipes = getRecipes()

        numApplied = 0
        for x in self._recipes:
            if x(self.mf):
                print "*** applied", x
                self._recipes.remove(x)
                numApplied += 1
        return numApplied

    def _handle_CopyTree(self, n):
        shutil.copytree(n.filename, os.path.join(self.distdir, n.dest))

    def addExecutable(self, exe):
        from bbfreeze import getdeps
        e = self.mf.createNode(Executable, os.path.basename(exe))
        e.filename = exe
        self.mf.createReference(self.mf, e)

        for so in getdeps.getDependencies(exe):
            n = self.mf.createNode(SharedLibrary, os.path.basename(so))
            n.filename = so
            self.mf.createReference(e, n)

    def findBinaryDependencies(self):
        from bbfreeze import getdeps
        assert os.access(self.console, os.X_OK), "%r is not executable" % (self.console,)

        for so in getdeps.getDependencies(self.console):
            n = self.mf.createNode(SharedLibrary, os.path.basename(so))
            n.filename = so
            self.mf.createReference(self.mf, n)

        for x in list(self.mf.flatten()):
            if isinstance(x, modulegraph.Extension):
                for so in getdeps.getDependencies(x.filename):
                    n = self.mf.createNode(SharedLibrary, os.path.basename(so))
                    n.filename = so
                    self.mf.createReference(x, n)

    def _getRPath(self, exe):
        os.environ["S"] = exe

        status, out = commands.getstatusoutput("patchelf --version")

        if status == 0:
            print out
            status, out = commands.getstatusoutput("patchelf --print-rpath $S")
            if status:
                raise RuntimeError("patchelf failed: %r" % out)
            return out.strip() or None

        status, out = commands.getstatusoutput("objdump -x $S")
        if status:
            print "WARNING: objdump failed: could not determine RPATH by running 'objdump -x %s'" % exe
            return None

        tmp = re.findall("[ \t]+RPATH[ \t]*(.*)", out)
        if len(tmp) == 1:
            return tmp[0].strip()

        if len(tmp) > 1:
            raise RuntimeError("Could not determine RPATH from objdump output: %r" % out)

        return ""

    def _setRPath(self, exe, rpath):
        os.environ["S"] = exe
        os.environ["R"] = rpath
        print "running 'patchelf --set-rpath '%s' %s'" % (rpath, exe)
        status, out = commands.getstatusoutput("patchelf --set-rpath $R $S")
        if status != 0:
            print "WARNING: failed to set RPATH for %s: %s" % (exe, out)
        else:
            print "RPATH adjusted successfully"

    def ensureRPath(self, exe):
        if sys.platform not in ("linux2", "linux3"):
            return

        expected_rpath = "${ORIGIN}:${ORIGIN}/../lib"
        current_rpath = self._getRPath(exe)
        if current_rpath is None:
            return

        if current_rpath == expected_rpath:
            print "RPATH %s is fine" % (current_rpath,)
            return

        print "RPATH=%s" % (current_rpath,)
        print "RPATH needs adjustment. make sure you have the patchelf executable installed."
        self._setRPath(exe, expected_rpath)

    def __call__(self):
        if self.include_py:
            pyscript = os.path.join(os.path.dirname(__file__), 'py.py')
            self.addScript(pyscript)

        self.addModule("encodings.*")
        self._add_loader()

        if os.path.exists(self.distdir):
            shutil.rmtree(self.distdir)
        os.makedirs(self.distdir)

        # work around easy_install which doesn't preserve the
        # executable bit
        if not os.access(self.console, os.X_OK):
            xconsole = os.path.join(self.distdir, "bbfreeze-console.exe")
            shutil.copy2(self.console, xconsole)
            os.chmod(xconsole, 0755)
            self.console = xconsole
        else:
            xconsole = None

        while 1:
            self.findBinaryDependencies()
            if not self._handleRecipes():
                break

        zipfilepath = os.path.join(self.distdir, "library.zip")
        self.zipfilepath = zipfilepath
        if self.linkmethod == 'loader' and sys.platform == 'win32':
            pass  # open(library, 'w')
        else:
            shutil.copy(self.console, zipfilepath)
            self.ensureRPath(zipfilepath)

        if os.path.exists(zipfilepath):
            mode = 'a'
        else:
            mode = 'w'

        self.outfile = zipfile.PyZipFile(zipfilepath, mode, zipfile.ZIP_DEFLATED)

        mods = [(x.identifier, x) for x in self.mf.flatten()]
        mods.sort()
        mods = [x[1] for x in mods]

        analyzer = EggAnalyzer()

        use_mods = []
        for x in mods:
            if x is self._loaderNode:
                use_mods.append(x)
                continue

            dist = analyzer.findDistribution(x)
            if not dist:
                use_mods.append(x)

        analyzer.report()
        analyzer.copy(self.distdir)

        for x in use_mods:
            try:
                m = getattr(self, "_handle_" + x.__class__.__name__)
            except AttributeError:
                print "WARNING: dont know how to handle", x
                continue
            m(x)

        self.outfile.close()

        if xconsole:
            os.unlink(xconsole)

        self.finish_dist()

        if os.environ.get("XREF") or os.environ.get("xref"):
            self.showxref()

    def finish_dist(self):
        if sys.platform != 'darwin':
            return

        from macholib.MachOStandalone import MachOStandalone
        d = os.path.join(os.path.abspath(self.distdir), "")
        m = MachOStandalone(d, d)
        m.run(contents="@executable_path/")

    def _handle_ExcludedModule(self, m):
        pass

    def _handle_MissingModule(self, m):
        pass

    def _handle_BuiltinModule(self, m):
        pass

    def _handle_AliasNode(self, m):
        pass

    def _handle_NamespaceModule(self, m):
        fn = "%s/__init__.py" % (m.identifier.replace(".", "/"),)
        code = compile("", fn, "exec")
        self._writecode(fn + "c", time.time(), code)

    def _handle_Extension(self, m):
        name = m.identifier

        basefilename = os.path.basename(m.filename)
        base, ext = os.path.splitext(basefilename)
        # fedora has zlibmodule.so, timemodule.so,...
        if base not in [name, name + "module"]:
            code = compile(EXTENSION_LOADER_SOURCE % (name + ext),
                           "ExtensionLoader.py", "exec")
            fn = name.replace(".", "/") + ".pyc"
            self._writecode(fn, time.time(), code)

        dst = os.path.join(self.distdir, name + ext)
        shutil.copy2(m.filename, dst)
        os.chmod(dst, 0755)
        # when searching for DLL's the location matters, so don't
        # add the destination file, but rather the source file
        self.binaries.append(m.filename)
        self.stripBinary(dst)

    def _handle_Package(self, m):
        fn = m.identifier.replace(".", "/") + "/__init__.pyc"
        mtime = self._get_mtime(m.filename)
        self._writecode(fn, mtime, m.code)

    def _handle_SourceModule(self, m):
        fn = m.identifier.replace(".", "/") + '.pyc'
        mtime = self._get_mtime(m.filename)
        self._writecode(fn, mtime, m.code)

    def _handle_ZipModule(self, m):
        fn = m.identifier.replace(".", "/")
        if m.is_package:
            fn += "/__init__"
        fn += ".pyc"
        mtime = self._get_mtime(m.filename)

        self._writecode(fn, mtime, m.code)

    def _handle_CompiledModule(self, m):
        fn = m.identifier.replace(".", "/") + '.pyc'
        print "WARNING: using .pyc file %r for which no source file could be found." % (fn,)
        mtime = self._get_mtime(m.filename)
        self._writecode(fn, mtime, m.code)

    def _handle_Script(self, m):
        exename = None
        mtime = self._get_mtime(m.filename)
        if m is self._loaderNode:
            fn = "__main__.pyc"
        else:
            fn = os.path.basename(m.filename)
            if fn.endswith(".py"):
                fn = fn[:-3]
            elif fn.endswith(".pyw"):
                fn = fn[:-4]

            exename = fn
            fn = '__main__%s__.pyc' % fn.replace(".", "_")

        self._writecode(fn, mtime, m.code)
        if exename:
            if sys.platform == 'win32':
                exename += '.exe'
            gui_only = getattr(m, 'gui_only', False)

            self.link(self.zipfilepath, os.path.join(self.distdir, exename), gui_only=gui_only)

    def _writecode(self, fn, mtime, code):
        code = replace_paths_in_code(code, fn)
        ziptime = time.localtime(mtime)[:6]
        data = imp.get_magic() + struct.pack("<i", mtime) + marshal.dumps(code)
        zinfo = zipfile.ZipInfo(fn, ziptime)
        if self.use_compression:
            zinfo.compress_type = zipfile.ZIP_DEFLATED
        self.outfile.writestr(zinfo, data)

    def link(self, src, dst, gui_only):
        if not self._have_console:
            self.binaries.append(dst)
            self._have_console = True

        if os.path.exists(dst) or os.path.islink(dst):
            os.unlink(dst)

        lm = self.linkmethod
        if lm == 'symlink':
            assert os.path.dirname(src) == os.path.dirname(dst)
            os.symlink(os.path.basename(src), dst)
            os.chmod(dst, 0755)
        elif lm == 'hardlink':
            os.link(src, dst)
            os.chmod(dst, 0755)
        elif lm == 'loader':
            if gui_only and sys.platform == 'win32':
                shutil.copy2(self.consolew, dst)
            else:
                shutil.copy2(self.console, dst)
            os.chmod(dst, 0755)
        else:
            raise RuntimeError("linkmethod %r not supported" % (self.linkmethod,))

    def stripBinary(self, p):
        if sys.platform == 'win32' or sys.platform == 'darwin':
            return
        os.environ['S'] = p
        os.system('strip $S')

    def _handle_Executable(self, m):
        dst = os.path.join(self.distdir, os.path.basename(m.filename))
        shutil.copy2(m.filename, dst)
        os.chmod(dst, 0755)
        self.stripBinary(dst)

    def _handle_SharedLibrary(self, m):
        dst = os.path.join(self.distdir, os.path.basename(m.filename))
        shutil.copy2(m.filename, dst)
        os.chmod(dst, 0755)
        self.stripBinary(dst)

    def showxref(self):
        import tempfile

        fd, htmlfile = tempfile.mkstemp(".html")
        ofi = open(htmlfile, "w")
        os.close(fd)

        self.mf.create_xref(ofi)
        ofi.close()

        import webbrowser
        try:
            webbrowser.open("file://" + htmlfile)
        except webbrowser.Error:
            # sometimes there is no browser (e.g. in chroot environments)
            pass
        # how long does it take to start the browser?
        import threading
        threading.Timer(5, os.remove, args=[htmlfile])
