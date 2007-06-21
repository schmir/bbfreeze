#! /usr/bin/env python

import xml.etree.cElementTree as ET

xml = """<?xml version='1.0'?>
<methodCall>
<methodName>echo</methodName>
<params>
<param>
<value><string>bla</string></value>
</param>
</params>
</methodCall>
"""

ET.fromstring(xml)
