#! /usr/bin/env python

# setup.py adapted from py2exe's setup.py

import os
import sys

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, Extension


from distutils.command import build_ext
from distutils import sysconfig
import distutils.util
execfile(distutils.util.convert_path('bbfreeze/_version.py')) 
# adds 'version' to local namespace

os.environ['LD_RUN_PATH'] = "${ORIGIN}:${ORIGIN}/../lib"

def read_long_description():
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.txt")
    return open(fn).read()

class BuildInterpreters(build_ext.build_ext):
    _patched = False

    def get_ext_filename (self, ext_name):
        r"""Convert the name of an extension (eg. "foo.bar") into the name
        of the file from which it will be loaded (eg. "foo/bar.so", or
        "foo\bar.pyd").
        """
        ext_path = ext_name.split('.')
        # OS/2 has an 8 character module (extension) limit :-(
        if os.name == "os2":
            ext_path[len(ext_path) - 1] = ext_path[len(ext_path) - 1][:8]
        if sys.platform=='win32':
            ext = ''
        else:
            ext = '.exe'
        return apply(os.path.join, ext_path) + ext
        
    def _patch(self):
        if self._patched:
            return

        LINKFORSHARED = sysconfig.get_config_var("LINKFORSHARED")
        if LINKFORSHARED and sys.platform != 'darwin':            
            linker = " ".join([sysconfig.get_config_var(x) for x in 'LINKCC LDFLAGS LINKFORSHARED'.split()])
            if '-Xlinker' in linker:
                linker += ' -Xlinker -zmuldefs'
                linker += ' -Xlinker --disable-new-dtags'
            self.compiler.set_executables(linker_exe = linker)

        def hacked(*args, **kwargs):
            for x in ('export_symbols', 'build_temp'):
                try:
                    del kwargs[x]
                except KeyError:
                    pass
            
            return self.compiler.link_executable(*args, **kwargs)
            
        self.compiler.link_shared_object = hacked

        self._patched = True
        
    def build_extension(self, ext):
        self._patch()
        return build_ext.build_ext.build_extension(self, ext)



def main():
    # --- libs
    libs = sysconfig.get_config_var("LIBS") or ""
    libs = [x[2:] for x in libs.split()]
    if sysconfig.get_config_var("LIBM"):
        libs += [sysconfig.get_config_var("LIBM")[2:]]

    if sysconfig.get_config_var("VERSION"):
        libs.append("python%s" % sysconfig.get_config_var("VERSION"))


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
    install_requires=["altgraph>=0.6.7"]
    
    if sys.platform=='win32':
        define_macros.append(('WIN32', 1))
    else:
        extra_sources.append('bbfreeze/getpath.c')

    ext_modules=[]
    def ext(name, source, libraries):
        e = Extension(name, source+extra_sources,
                      libraries=libraries,
                      library_dirs=library_dirs,
                      define_macros=define_macros)
        ext_modules.append(e)
        
    ext("bbfreeze/console", ['bbfreeze/console.c'], libs)
    if sys.platform=='win32':
        ext("bbfreeze/consolew", ['bbfreeze/consolew.c'], libs+['user32'])
        install_requires.append("pefile>=1.2.4")

    setup(name = "bbfreeze",
          cmdclass = dict(build_ext=BuildInterpreters),
          version = str(version),  # see execfile from above
          entry_points = dict(console_scripts=['bb-freeze = bbfreeze:main']),
          ext_modules = ext_modules,
          install_requires=install_requires,
          packages = ['bbfreeze', 'bbfreeze.modulegraph'],
          zip_safe = False,
          maintainer="Ralf Schmitt",
          maintainer_email="schmir@gmail.com",
          url = "http://cheeseshop.python.org/pypi/bbfreeze/",
          description="create standalone executables from python scripts",
          platforms="Linux Windows",
          license="zlib/libpng license",
          long_description = read_long_description(),
          )

if __name__=='__main__':
    main()
