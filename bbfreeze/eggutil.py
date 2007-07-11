#! /usr/bin/env python

import sys
import os
import stat
import zipfile
import struct
import imp
import marshal
import time

class Entry(object):
    read = None
    stat = None
    
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        return "<Entry %r>" % (self.__dict__,)

    def isdir(self):
        return self.read is None
        
def walk(path):
    if os.path.isfile(path):
        return walk_zipfile(path)
    else:
        return walk_dir(path)
    
def walk_zipfile(path):
    zfobj = zipfile.ZipFile(path)
    for name in zfobj.namelist():
        if name.endswith("/"):
            yield Entry(name=name)
        else:
            yield Entry(name=name, read=lambda name=name: zfobj.read(name))
            
def walk_dir(path):
    path=os.path.normpath(path)
    def relname(n):
        return os.path.join(dirpath, n)[len(path)+1:]
        
    for dirpath, dirnames, filenames in os.walk(path):
        for x in dirnames:
            fp = os.path.join(path, dirpath, x)            
            yield Entry(name=relname(x), stat=lambda fp=fp: os.stat(fp))

        for x in filenames:
            fp = os.path.join(path, dirpath, x)
            yield Entry(name=relname(x),
                        read=lambda fp=fp: open(fp, "rb").read(),
                        stat=lambda fp=fp: os.stat(fp))

def default_filter(entries):
    for x in entries:
        if x.name.endswith(".py"):
            continue

        if x.name.endswith(".pyo"):
            continue

        yield x
        
def write_zipfile(path, entries):
    zf = zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED)
    for x in entries:
        if x.isdir():
            continue

        zf.writestr(x.name, x.read())
    zf.close()

def write_directory(path, entries):
    os.mkdir(path)
    for x in entries:
        fn = os.path.join(path, x.name)
        if x.isdir():
            os.mkdir(fn)
        else:
            open(fn, "wb").write(x.read())

        if x.stat is None:
            continue

        if x.isdir() and sys.platform=='win32':
            continue
        
        
        st = x.stat()
        mode = stat.S_IMODE(st.st_mode)
        if hasattr(os, 'utime'):
            os.utime(fn, (st.st_atime, st.st_mtime))
        if hasattr(os, 'chmod'):
            os.chmod(fn, mode)
        

def copyDistribution(distribution, destdir):
    dest = os.path.join(destdir, distribution.egg_name()+".egg")
    print "Copying", distribution.location, "to", dest

    entries = list(walk(distribution.location))
    name2compile = {}

    for x in entries:
        if x.name.endswith(".py"):
            name2compile[x.name]=x
    
    entries = list(default_filter(entries))
    for x in entries:
        if x.name.endswith(".pyc"):
            try:
                del name2compile[x.name[:-1]]
            except KeyError:
                pass

    mtime = int(time.time())

    for x in name2compile.values():
        try:
            code = compile(x.read()+'\n', x.name, 'exec')
        except Exception, err:
            print "WARNING: Could not compile %r: %r" % (x.name, err)
            continue

        data = imp.get_magic() + struct.pack("<i", mtime) + marshal.dumps(code)        
        entries.append(Entry(name=x.name+'c', read=lambda data=data: data))

    if distribution.has_metadata("zip-safe") or not os.path.isdir(distribution.location):        
        write_zipfile(dest, entries)
    else:
        write_directory(dest, entries)
