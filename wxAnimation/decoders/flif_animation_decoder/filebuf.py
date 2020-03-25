#!/usr/bin/env python3
# Helper for getting buffers from file objects

from __future__ import unicode_literals, division

import mmap


class FileBuffer(object):
    def __init__(self, fileobj):
        self.file = fileobj

        try:
            self.fileno = self.file.fileno()
        except OSError:
            self.fileno = -1

        if self.fileno != -1:# and self.fd.seekable(): # Python 2.x doesn't have seekable()
            # size
            self.file.seek(0, 2)
            self.size = self.file.tell()
            self.buffer = mmap.mmap(self.fileno, self.size, access=mmap.ACCESS_READ)
            self.type = "mmap"
        elif hasattr(self.file, "getbuffer"): # BytesIO
            self.buffer = self.file.getbuffer()
            self.size = len(self.buffer)
            self.type = "buffer"
        else:
            self.buffer = self.file.read()
            self.size = len(self.buffer)
            self.type = "bytes"

    def close(self):
        if self.type == "mmap":
            self.file.close()
        elif self.type == "bytes":
            del self.buffer
        elif self.type == "buffer":
            self.buffer = None
        else:
            raise RuntimeError("Unknown FileBuffer type %s" % self.type)

    def __enter__(self):
        return self

    def __exit__(self, t, e, tb):
        self.close()
