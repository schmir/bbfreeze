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
    return True
