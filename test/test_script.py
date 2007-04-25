#! /usr/bin/env py.test

import sys
import os

def fullpath(x):
    dn = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dn, x)

def compile_and_run(p):
    err=os.system("bb-freeze $S")
    assert err==0, "bb-freeze failed"
    if p.endswith('.py'):
        p = p[:-3]
    err=os.system(os.path.abspath(os.path.join('dist', p)))
    assert err==0, "frozen executable failed"

def maybe_compile_and_run(x):
    assert os.path.exists(x)
    os.environ['S'] = fullpath(x)
    err=os.system("%s $S" % (sys.executable,))
    if err==0:
        compile_and_run(x)
    
def test_ex_time():
    maybe_compile_and_run("ex-time.py")

def test_hello_world():
    maybe_compile_and_run("hello-world.py")

def test_pylog():
    maybe_compile_and_run("ex-pylog.py")
