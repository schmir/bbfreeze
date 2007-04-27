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
        err=os.system("dist\\ex-mbox")
        assert err==0

    
