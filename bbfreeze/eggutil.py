#! /usr/bin/env python

import zipfile
import os

## import stat
## def copystat(src, dst):
##     """Copy all stat info (mode bits, atime and mtime) from src to dst"""
##     st = os.stat(src)
##     mode = stat.S_IMODE(st.st_mode)
##     if hasattr(os, 'utime'):
##         os.utime(dst, (st.st_atime, st.st_mtime))
##     if hasattr(os, 'chmod'):
##         os.chmod(dst, mode)

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
        if not x.name.endswith(".py"):
            yield x
        
def write_zipfile(path, entries):
    zf = zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED)
    for x in entries:
        if x.isdir():
            continue

        zf.writestr(x.name, x.read())
    zf.close()



def copyDistribution(distribution, destdir):
    dest = os.path.join(destdir, distribution.egg_name()+".egg")
    print "Copying", distribution.location, "to", dest
    write_zipfile(dest, default_filter(walk(distribution.location)))
