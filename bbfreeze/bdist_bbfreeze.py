"""bbfreeze.bdist_bbfreeze

Implements the distutils 'bdist_bbfreeze' command.
"""

__author__ = "Hartmut Goebel <h.goebel@goebel-consult.de>"
__copyright__ = "Copyright 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>"
__licence__ = "Same as bbfreeze"
__version__ = "0.1"

import os

from distutils.util import get_platform
from distutils import log

from setuptools.command.easy_install import easy_install, get_script_args
from pkg_resources import Distribution, PathMetadata, normalize_path


class bdist_bbfreeze(easy_install):
    # this is a bit hackish: we inherit from easy_install,
    # but discard most of it

    description = "freeze scripts using bbfreeze"

    user_options = [
        ('bdist-base=', 'b',
         "temporary directory for creating built distributions"),
        ('plat-name=', 'p',
         "platform name to embed in generated filenames "
         "(default: %s)" % get_platform()),
        ('dist-dir=', 'd',
         "directory to put final built distributions in "
         "[default: dist/<egg_name-egg_version>]"),
        # todo: include_py
        ]

    boolean_options = []
    negative_opt = {}

    def initialize_options(self):
        self.bdist_base = None
        self.plat_name = None
        self.dist_dir = None
        self.include_py = False
        easy_install.initialize_options(self)
        self.outputs = []

    def finalize_options(self):
        # have to finalize 'plat_name' before 'bdist_base'
        if self.plat_name is None:
            self.plat_name = get_platform()

        # 'bdist_base' -- parent of per-built-distribution-format
        # temporary directories (eg. we'll probably have
        # "build/bdist.<plat>/dumb", "build/bdist.<plat>/rpm", etc.)
        if self.bdist_base is None:
            build_base = self.get_finalized_command('build').build_base
            self.bdist_base = os.path.join(build_base,
                                           'bbfreeze.' + self.plat_name)
        self.script_dir = self.bdist_base

        if self.dist_dir is None:
            self.dist_dir = "dist"

    def run(self, wininst=False):
        # import bbfreeze only thenabout to run the command
        from bbfreeze import Freezer

        # get information from egg_info
        ei = self.get_finalized_command("egg_info")
        target = normalize_path(self.bdist_base)
        dist = Distribution(
            target,
            PathMetadata(target, os.path.abspath(ei.egg_info)),
            project_name=ei.egg_name)

        # install wrapper_Scripts into self.bdist_base == self.script_dir
        self.install_wrapper_scripts(dist)

        # now get a Freezer()
        f = Freezer(os.path.join(self.dist_dir,
                                 "%s-%s" % (ei.egg_name, ei.egg_version)))
        f.include_py = self.include_py

        # freeze each of the scripts
        for args in get_script_args(dist, wininst=wininst):
            name = args[0]
            if name.endswith('.exe') or name.endswith(".exe.manifest"):
                # skip .exes
                continue
            log.info('bbfreezing %s', os.path.join(self.script_dir, name))
            f.addScript(os.path.join(self.script_dir, name),
                        gui_only=name.endswith('.pyw'))
        # starts the freezing process
        f()
