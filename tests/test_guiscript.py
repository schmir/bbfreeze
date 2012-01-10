#! /usr/bin/env py.test
try:
    import win32ui
except:
    win32ui = None

import os
import bbfreeze

if win32ui:
    def test_guiscript():
        f = bbfreeze.Freezer()
        f.addScript("ex-mbox.py", True)
        f()
        err = os.system("dist\\ex-mbox")
        assert err == 0


def test_guiscript2():
    f = bbfreeze.Freezer()
    f.addScript("hello-world.py", True)
    f()

    cmd = os.path.join("dist", "hello-world")
    err = os.system(cmd)

    assert err == 0
