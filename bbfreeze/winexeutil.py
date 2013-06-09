#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import win32api


class Icon:
    """
    Icon class. Represents an Ico file.
    """
    # Parsing constants
    HEADER_FORMAT = "hhh"
    ENTRY_FORMAT = "bbbbhhii"
    ENTRY_FORMAT_ID = "bbbbhhih"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    ENTRY_SIZE = struct.calcsize(ENTRY_FORMAT)
    
    def __init__(self, filename):
        """
        Create a Icon object from the path to a .ico file.
        """
        # Icon sections
        self._header = ""
        self._entries = []
        self._images = []
        
        with open(filename, 'rb') as fd:
            self._header = fd.read(self.HEADER_SIZE)
            # Get the tuple of the header and get how many entries we have
            count = self.header()[2]
            
            # Collect entries in the ico file
            for i in range(count):
                # Read entry
                e = fd.read(self.ENTRY_SIZE)
                self._entries.append(e)
            
            # Now collect images
            for i, bentry in enumerate(self._entries):
                entry = struct.unpack(self.ENTRY_FORMAT, bentry)
                # Go to image and read bytes
                fd.seek(entry[7], 0)
                data = fd.read(entry[6])
                self._images.append(data)
                # Remove last item (offset) and add the id
                entry = entry[:-1] + (i+1,)
                # Save change back in bytes
                self._entries[i] = struct.pack(self.ENTRY_FORMAT_ID,
                                               *entry)
                
    
    def header(self):
        """
        Return a tuple with the values in the header of the Icon.
        
        Header is made of three values:
        - a reserved value
        - the type id
        - entries count
        """
        return struct.unpack(self.HEADER_FORMAT, self._header)
    
    def entries(self):
        """
        Return an array with the tuples of the icons entries. An icon entry
        is a special header that describes an image. A single .ico file can
        contain multiple entries.
        
        Each entry contains:
        - width
        - height
        - color count
        - reserved value
        - planes
        - bit count
        - size of image
        - id
        """
        res = []
        for e in self._entries:
            res.append(struct.unpack(self.ENTRY_FORMAT_ID, e))
        return res
    
    def images(self):
        """
        Return an array with the bytes for each of the images in the icon.
        """
        return _images


def set_icon(exe_filename, ico_filename):
    """
    Set the icon on a windows executable.
    """
    # Icon file
    icon = Icon(ico_filename)

    # Begin update of executable
    hdst = win32api.BeginUpdateResource (exe_filename, 0)

    # Update entries
    data = icon._header + reduce(str.__add__, icon._entries)
    win32api.UpdateResource (hdst, 14, 1, data)

    # Update images
    for i, image in enumerate(icon._images):
        win32api.UpdateResource (hdst, 3, i+1, image)

    # Done
    win32api.EndUpdateResource (hdst, 0)
