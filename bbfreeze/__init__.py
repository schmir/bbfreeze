class _Version(tuple):
    """internal version object, subclass of C{tuple},
    but implements a more nice __str__ representation
    """
    def __str__(self):
        return '.'.join([str(x) for x in self])

version = _Version((0,94,0))
del _Version
from bbfreeze.freezer import Freezer

def main():
    import sys
    scripts = sys.argv[1:]
    if not scripts:
        print "Version: %s (Python %s)" % (version, ".".join([str(x) for x in sys.version_info]))
        print "Usage: bb-freeze SCRIPT1 [SCRIPT2...]"
        print "   creates standalone executables from python scripts SCRIPT1,..."
        print
        
        sys.exit(0)
        
    f=Freezer()
    for x in scripts:
        f.addScript(x)
    f()


