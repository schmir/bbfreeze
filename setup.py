#! /usr/bin/env python

# setup.py adapted from py2exe's setup.py

import sys, os, platform

try:
    from setuptools import setup, Extension
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, Extension


from distutils.command import build_ext
from distutils import sysconfig


def get_version():
    d = {}
    try:
        execfile("bbfreeze/__init__.py", d)
    except Exception:
        pass
    return d["__version__"]

version = get_version()

os.environ['LD_RUN_PATH'] = "${ORIGIN}:${ORIGIN}/../lib"

conf = None


class Conf(object):
    def __init__(self):
        self.platform = platform.platform()
        self.darwin = (sys.platform == 'darwin')
        self.win32 = (sys.platform == 'win32')
        self.unix = not (self.darwin or self.win32)  # other unix
        VERSION = sysconfig.get_config_var("VERSION")
        if VERSION:
            self.PYTHONVERSION = "python%s" % (VERSION,)
        else:
            self.PYTHONVERSION = ""
        self.linker = self._linker()
        self.symbolic_functions_bug = self._symbolic_functions()
        self.static_library = self._static_library()

    def _linker(self):
        LINKFORSHARED = sysconfig.get_config_var("LINKFORSHARED")
        if LINKFORSHARED and sys.platform != 'darwin':
            linker = " ".join([sysconfig.get_config_var(x) for x in 'LINKCC LDFLAGS LINKFORSHARED'.split()])
            return linker
        return ""

    def _symbolic_functions(self):
        return self.unix and '-Bsymbolic-functions' in self._linker()

    def _static_library(self):
        libpl = sysconfig.get_config_var("LIBPL")
        if not libpl:
            return ""
        lib = sysconfig.get_config_var("LIBRARY")
        if not lib:
            lib = "lib%s" % (self.PYTHONVERSION,)
        p = os.path.join(libpl, lib)
        if os.path.exists(p):
            return p
        return ""

    def __repr__(self):
        d = self.__dict__.copy()
        d['sys.version'] = sys.version
        d['sys.maxunicode'] = hex(sys.maxunicode)
        d['sys.maxint'] = hex(sys.maxint)
        d['sys.executable'] = sys.executable
        d['platform'] = platform.platform()

        items = d.items()

        items.sort()
        res = ['']
        first = "------ bbfreeze %s configuration ------" % (version,)
        res.append(first)
        for k, v in items:
            res.append("%s = %s" % (k, v))
        res.append("-" * len(first))
        res.append('')
        return "\n".join(res)


def read_long_description():
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.rst")
    return open(fn).read()


def maybe_strip(exe):
    """strip executable"""
    if conf.win32:
        return
    if conf.darwin:
        return

    os.environ['S'] = exe
    print "====> Running 'strip %s'" % (exe,)
    err = os.system("strip $S")
    if err:
        print "strip command failed"


class BuildInterpreters(build_ext.build_ext):
    _patched = False

    def get_ext_filename(self, ext_name):
        r"""Convert the name of an extension (eg. "foo.bar") into the name
        of the file from which it will be loaded (eg. "foo/bar.so", or
        "foo\bar.pyd").
        """
        ext_path = ext_name.split('.')
        # OS/2 has an 8 character module (extension) limit :-(
        if os.name == "os2":
            ext_path[len(ext_path) - 1] = ext_path[len(ext_path) - 1][:8]
        if sys.platform == 'win32':
            ext = ''
        else:
            ext = '.exe'
        return apply(os.path.join, ext_path) + ext

    def _patch(self):
        if self._patched:
            return

        LOCALMODLIBS = ""
        LINKFORSHARED = sysconfig.get_config_var("LINKFORSHARED")
        if LINKFORSHARED and sys.platform != 'darwin':
            linker = " ".join([sysconfig.get_config_var(x) for x in 'LINKCC LDFLAGS LINKFORSHARED'.split()])
            if '-Xlinker' in linker:
                linker += ' -Xlinker -zmuldefs'
                linker += ' -Xlinker --disable-new-dtags'
            LOCALMODLIBS = sysconfig.get_config_var("LOCALMODLIBS") or ""

            self.compiler.set_executables(linker_exe=linker)

        def hacked(*args, **kwargs):
            for x in ('export_symbols', 'build_temp'):
                try:
                    del kwargs[x]
                except KeyError:
                    pass

            if LOCALMODLIBS:
                kwargs["extra_postargs"] = LOCALMODLIBS.split()

            retval = self.compiler.link_executable(*args, **kwargs)
            maybe_strip(args[1])
            return retval

        self.compiler.link_shared_object = hacked

        self._patched = True

    def build_extension(self, ext):
        self._patch()
        return build_ext.build_ext.build_extension(self, ext)


def main():
    global conf
    conf = Conf()
    print conf

    extra_objects = []

    # --- libs
    cfglibs = sysconfig.get_config_var("LIBS") or ""
    libs = []
    extra_link_args = []
    for part in cfglibs.split():
        if part[:2] == '-l':
            libs.append(part[2:])
        else:
            extra_link_args.append(part)

    if sysconfig.get_config_var("LIBM"):
        libs += [sysconfig.get_config_var("LIBM")[2:]]

    if conf.symbolic_functions_bug and conf.static_library:
        extra_objects.append(conf.static_library)
    else:
        if conf.PYTHONVERSION:
            libs.append(conf.PYTHONVERSION)

    # --- library_dirs
    library_dirs = []
    libdir = sysconfig.get_config_var("LIBDIR")
    if libdir:
        library_dirs.append(libdir)

    libpl = sysconfig.get_config_var("LIBPL")
    if libpl:
        library_dirs.append(libpl)

    # --- extra_sources, define_macros, ext_modules
    extra_sources = []
    define_macros = []
    install_requires = ["altgraph>=0.6.7"]

    if sys.platform == 'win32':
        define_macros.append(('WIN32', 1))
    else:
        extra_sources.append('bbfreeze/getpath.c')

    if sys.platform == 'win32':
        extra_link_args = ['/LARGEADDRESSAWARE']

    ext_modules = []

    def ext(name, source, libraries):
        e = Extension(name, source + extra_sources,
                      libraries=libraries,
                      library_dirs=library_dirs,
                      extra_objects=extra_objects,
                      extra_link_args=extra_link_args,
                      define_macros=define_macros)
        ext_modules.append(e)

    ext("bbfreeze/console", ['bbfreeze/console.c'], libs)
    if sys.platform == 'win32':
        ext("bbfreeze/consolew", ['bbfreeze/consolew.c'], libs + ['user32'])
        install_requires.append("pefile>=1.2.4")

    setup(name="bbfreeze",
          cmdclass=dict(build_ext=BuildInterpreters),
          version=version,
          entry_points={
             "console_scripts": ['bb-freeze = bbfreeze:main'],
             "distutils.commands": [
                 "bdist_bbfreeze = bbfreeze.bdist_bbfreeze:bdist_bbfreeze"]},
          ext_modules=ext_modules,
          install_requires=install_requires,
          packages=['bbfreeze', 'bbfreeze.modulegraph'],
          zip_safe=False,
          maintainer="Ralf Schmitt",
          maintainer_email="ralf@systemexit.de",
          url="http://pypi.python.org/pypi/bbfreeze/",
          description="create standalone executables from python scripts",
          platforms="Linux Windows",
          license="zlib/libpng license",
          classifiers=[
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: zlib/libpng License",
            "Intended Audience :: Developers",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.4",
            "Programming Language :: Python :: 2.5",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Topic :: Software Development :: Build Tools",
            "Topic :: System :: Software Distribution"],
          long_description=read_long_description())

if __name__ == '__main__':
    main()
