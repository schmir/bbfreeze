#! /usr/bin/env python

import os

def main():
    files = [x.strip() for x in os.popen("hg manifest")]
    files.append("README.html")

    files.sort()

    f = open("MANIFEST.in", "w")
    for x in files:
        if x==".hgtags":
            continue
        f.write("include %s\n" % x)
    f.close()


if __name__=='__main__':
    main()
