#! /usr/bin/env python
"""show distutils's config variables"""


def main():
    import distutils.sysconfig
    items = distutils.sysconfig.get_config_vars().items()
    items.sort()
    for k, v in items:
        print "%s: %r" % (k, v)

if __name__ == '__main__':
    main()
