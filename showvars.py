#! /usr/bin/env python
"""show distutils's config variables"""

import sys


def main():
    import distutils.sysconfig
    items = sorted(distutils.sysconfig.get_config_vars().items())
    for k, v in items:
        sys.stdout.write("%s: %r\n" % (k, v))

if __name__ == '__main__':
    main()
