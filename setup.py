#! /usr/bin/env python

# setup.py adapted from py2exe's setup.py

import os
import sys

try:
    from setuptools import setup, Extension
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, Extension

from distutils.command import build, build_ext
from distutils import dist, dep_util, sysconfig

os.environ['LD_RUN_PATH'] = "${ORIGIN}:${ORIGIN}/../lib"


class BuildInterpreters(build_ext.build_ext):
    _patched = False

    def get_ext_filename (self, ext_name):
        r"""Convert the name of an extension (eg. "foo.bar") into the name
        of the file from which it will be loaded (eg. "foo/bar.so", or
        "foo\bar.pyd").
        """
        from distutils.sysconfig import get_config_var
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
        if LINKFORSHARED:            
            linker = " ".join(sysconfig.get_config_var(x) for x in 'LINKCC LDFLAGS LINKFORSHARED'.split())
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
                
libs = sysconfig.get_config_var("LIBS") or ""
libs = [x[2:] for x in libs.split()]
if sysconfig.get_config_var("LIBM"):
    libs += [sysconfig.get_config_var("LIBM")[2:]]

library_dirs = []
libdir = sysconfig.get_config_var("LIBDIR")
if libdir:
    library_dirs.append(libdir)
    
libpl = sysconfig.get_config_var("LIBPL")
if libpl:
    library_dirs.append(libpl)

if sysconfig.get_config_var("VERSION"):
    libs.append("python%s" % sysconfig.get_config_var("VERSION"))

define_macros = []
if sys.platform=='win32':
    define_macros.append(('WIN32', 1))
    
console = Extension("bbfreeze/console", ['bbfreeze/console.c'],
                    libraries=libs,
                    library_dirs=library_dirs,
                    define_macros=define_macros
                    )
    
setup(name = "bbfreeze",
      cmdclass         = {'build_ext': BuildInterpreters,
                          },
      version = '0.91.0',
      entry_points = dict(console_scripts=['bb-freeze = bbfreeze:main']),
      ext_modules = [console],
      install_requires=["altgraph>=0.6.7",
                        "modulegraph>=0.7"],
      packages = ['bbfreeze'],
      zip_safe = False,
      maintainer="Ralf Schmitt",
      maintainer_email="schmir@gmail.com",
      url = "http://systemexit.de/bbfreeze/",
      description="create standalone executables from python scripts"
      )
