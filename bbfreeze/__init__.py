__version_info__ = (1, 1, 0)
version = __version__ = "1.1.0dev"

import sys
from bbfreeze.freezer import Freezer


def main():
    scripts = sys.argv[1:]
    if not scripts:
        sys.stdout.write("Version: %s (Python %s)\n" % (version, ".".join([str(x) for x in sys.version_info])))
        sys.stdout.write("""Usage: bbfreeze SCRIPT1 [SCRIPT2...]
   creates standalone executables from python scripts SCRIPT1,...
""")

        sys.exit(0)

    f = Freezer()
    for x in scripts:
        f.addScript(x)
    f()
