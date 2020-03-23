# -*- coding: utf-8 -*-
#
# ***********************************************************************************
# MIT License
#
# Copyright (c) 2020 Kevin G. Schlosser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# ***********************************************************************************

import wx


wxANIM_UNSPECIFIED = -1
# no disposal is done on this frame before rendering the next;
# the contents of the output buffer are left as is.
wxANIM_DONOTREMOVE = 0
# the frame's region of the output buffer is to be cleared to
# fully transparent black before rendering the next frame.
wxANIM_TOBACKGROUND = 1
# the frame's region of the output buffer is to be reverted to
# the previous contents before rendering the next frame.
wxANIM_TOPREVIOUS = 2


wxObjectRefData = wx.RefCounter


class wxAnimationDecoder(wxObjectRefData):

    def __init__(self):
        self.m_nFrames = 0
        self.m_szAnimation = wx.Size(0, 0)
        self.m_background = wx.Colour(0, 0, 0, 0)

        super(wxAnimationDecoder, self).__init__()

    def Load(self, stream):
        return 0

    def CanRead(self, stream):

        if not hasattr(stream, 'seek'):
            return False  #  can't test unseekable stream

        posOld = stream.tell()
        ok = self.DoCanRead(stream)

        # restore the old position to be able to test other formats and so on
        stream.seek(posOld)
        if stream.tell() != posOld:
            return False

        return ok

    def Clone(self):
        return 0

    def GetType(self):
        return 0

    def ConvertToImage(self, frame):
        return 0

    def GetFrameSize(self, frame):
        return 0

    def GetFramePosition(self, frame):
        return 0

    def GetDisposalMethod(self, frame):
        return 0

    def GetDelay(self, frame):
        return 0

    def GetTransparentColour(self, frame):
        return 0

    def GetAnimationSize(self):
        return self.m_szAnimation

    def GetBackgroundColour(self):
        return self.m_background

    def GetFrameCount(self):
        return self.m_nFrames

    def DoCanRead(self, stream):
        return 0


NullAnimationDecoder = wxAnimationDecoder()
