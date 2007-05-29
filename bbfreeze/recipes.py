import sys
import os

def find_all_packages(name):    
    def recipe(mf):
        m = mf.findNode(name)
        if m is None or m.filename is None:
            return None

        import setuptools
        packages = setuptools.find_packages(os.path.dirname(m.filename))

        for pkg in packages:
            mf.import_hook('%s.%s' % (name, pkg), m, ['*'])
        return True
    recipe.__name__ = "recipe_"+name
    return recipe

recipe_flup = find_all_packages('flup')
recipe_django = find_all_packages('django')
recipe_py = find_all_packages("py")
recipe_email = find_all_packages("email")
recipe_IPython = find_all_packages("IPython")

def recipe_pydoc(mf):
    m = mf.findNode('pydoc')
    if m is None or m.filename is None:
        return None
    
    refs = [
        'Tkinter', 'tty', 'BaseHTTPServer', 'mimetools', 'select',
        'threading', 'ic', 'getopt',
    ]
    if sys.platform != 'win32':
        refs.append('nturl2path')
    for ref in refs:
        mf.removeReference(m, ref)
    return True

def recipe_docutils(mf):
    m = mf.findNode('docutils')
    if m is None or m.filename is None:
        return None

    for pkg in [
            'languages', 'parsers', 'readers', 'writers',
            'parsers.rst.directives', 'parsers.rst.languages']:
        try:
            mf.import_hook('docutils.' + pkg, m, ['*'])
        except SyntaxError: # in docutils/writers/newlatex2e.py
            pass
    return True

def recipe_py_magic_greenlet(mf):
    m = mf.findNode('py')
    if m is None or m.filename is None:
        return None

    pydir = os.path.dirname(m.filename)
    gdir = os.path.join(pydir, "c-extension", "greenlet")
    mf.path.append(gdir)
    mf.import_hook("greenlet", m, ['*'])



    gr = mf.findNode('py.magic.greenlet')
    if gr is None or gr.filename is None:
        return None

    gr.code = compile("""
__path__ = []    
import sys
mod = sys.modules[__name__]
from greenlet import greenlet
sys.modules[__name__] = mod
del mod
""", "py/magic/greenlet.py", "exec")
    
    return True

def recipe_time(mf):
    m = mf.findNode('time')
    
    # time is a BuiltinModule on win32, therefor m.filename is None
    if m is None: # or m.filename is None:
        return None
    
    mf.import_hook('_strptime', m, ['*'])
    return True


def recipe_pkg_resources(mf):
    m = mf.findNode('pkg_resources')
    if m is None or m.filename is None:
        return None

    print "WARNING: replacing pkg_resources module with dummy implementation"
    


    m.code = compile("""
def require(*args, **kwargs):
    return
def declare_namespace(name):
    pass

""", "pkg_resources.py", "exec")
    
    return True



def recipe_tkinter(mf):
    m = mf.findNode('_tkinter')
    if m is None or m.filename is None:
        return None

    if sys.platform=='win32':
        import Tkinter
        tcldir = os.environ.get("TCL_LIBRARY")
        if tcldir:
            mf.copyTree(tcldir, "lib-tcl", m)

        tkdir = os.environ.get("TK_LIBRARY")
        if tkdir:
            mf.copyTree(tkdir, "lib-tk", m)
            
        
    else:
        import _tkinter
        from bbfreeze import getdeps

        deps = getdeps.getDependencies(_tkinter.__file__)
        for x in deps:
            if os.path.basename(x).startswith("libtk"):
                tkdir = os.path.join(os.path.dirname(x), "tk%s" % _tkinter.TK_VERSION)
                if os.path.isdir(tkdir):
                    mf.copyTree(tkdir, "lib-tk", m)

        for x in deps:
            if os.path.basename(x).startswith("libtcl"):
                tcldir = os.path.join(os.path.dirname(x), "tcl%s" % _tkinter.TCL_VERSION)
                if os.path.isdir(tcldir):
                    mf.copyTree(tcldir, "lib-tcl", m)

    return True

def recipe_gtk_and_friends(mf):
    retval = False
    from bbfreeze.freezer import SharedLibrary
    for x in list(mf.flatten()):
        if not isinstance(x, SharedLibrary):
            continue

        prefixes = ["libpango", "libpangocairo", "libpangoft", "libgtk", "libgdk", "libglib", "libgmodule", "libgobject", "libgthread"]

        for p in prefixes:        
            if x.identifier.startswith(p):
                print "SKIPPING:", x
                mf.removeNode(x)
                retval = True                
                break

    return retval
