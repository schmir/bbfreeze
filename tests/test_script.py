#! /usr/bin/env py.test

import sys, os


def fullpath(x):
    dn = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dn, x)


def compile_and_run(p):
    err = os.system("bb-freeze %s" % p)
    assert err == 0, "bb-freeze failed"
    if p.endswith('.py'):
        p = p[:-3]
    err = os.system(os.path.abspath(os.path.join('dist', p)))
    assert err == 0, "frozen executable failed"


def maybe_compile_and_run(x):
    print "\n\n-----------------> building", x, "<------------"

    assert os.path.exists(x)
    os.environ['S'] = fullpath(x)
    err = os.system("%s %s" % (sys.executable, fullpath(x)))
    if err == 0:
        compile_and_run(x)
    else:
        print "failed"


def test_ex_time():
    maybe_compile_and_run("ex-time.py")


def test_hello_world():
    maybe_compile_and_run("hello-world.py")


def test_pylog():
    maybe_compile_and_run("ex-pylog.py")


def test_celementtree():
    maybe_compile_and_run("ex-celementtree.py")


def test_email_mimetext():
    maybe_compile_and_run("ex-email_mimetext.py")

if sys.platform == 'win32':
    def test_pythoncom():
        maybe_compile_and_run("ex-pythoncom.py")

    def test_pywintypes():
        maybe_compile_and_run("ex-pywintypes.py")
