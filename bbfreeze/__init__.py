__version_info__ = (1, 0, 0)
version = __version__ = "1.0.0"

import sys
from bbfreeze import modulegraph
sys.modules['modulegraph'] = modulegraph

from bbfreeze.freezer import Freezer


def main():
    scripts = sys.argv[1:]
    if not scripts:
        print "Version: %s (Python %s)" % (version, ".".join([str(x) for x in sys.version_info]))
        print "Usage: bb-freeze SCRIPT1 [SCRIPT2...]"
        print "   creates standalone executables from python scripts SCRIPT1,..."
        print

        sys.exit(0)

    f = Freezer()
    for x in scripts:
        f.addScript(x)
    f()
