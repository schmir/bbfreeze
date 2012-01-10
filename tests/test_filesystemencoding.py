#! /usr/bin/env py.test

import py, sys, os

pyexe = py.path.local(sys.executable)


def check_encoding():
    enc = pyexe.sysexec("ex-fsenc.py")
    print "ENC:", enc
    enc_frozen = py.path.local("dist/ex-fsenc").sysexec()
    assert enc == enc_frozen


def test_getfilesystemencoding(monkeypatch):
    os.system("bb-freeze ex-fsenc.py")

    monkeypatch.setenv("LANG", "en_US.UTF-8")
    check_encoding()

    monkeypatch.setenv("LANG", "")
    check_encoding()

    monkeypatch.setenv("LANG", "de_AT@euro")
    check_encoding()
