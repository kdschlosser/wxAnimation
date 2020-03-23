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

import wx.adv
import wx
import io

from .png_animation_decoder import wxPNGDecoder

wxANIMATION_TYPE_INVALID = 0
wxANIMATION_TYPE_ANI = 2
wxANIMATION_TYPE_GIF = 1
wxANIMATION_TYPE_PNG = 4
wxANIMATION_TYPE_ANY = 3

wxAC_NO_AUTORESIZE = 0x0010
wxAC_DEFAULT_STYLE = wx.BORDER_NONE


class wxAnimation(wx.adv.Animation):
    sm_handlers = []

    def __init__(self, name=None, type=wxANIMATION_TYPE_ANY):
        self.m_refData = None

        if name is None:
            self.m_isSuper = True
            super(wxAnimation, self).__init__()
        else:
            self.m_isSuper = False
            if self.LoadFile(name, type):
                super(wxAnimation, self).__init__()
            else:
                self.m_isSuper = True
                super(wxAnimation, self).__init__(name, type)

    def IsOk(self):
        if self.m_isSuper:
            return super(wxAnimation, self).IsOk()

        return self.m_refData is not None

    def GetFrameCount(self):
        if self.m_isSuper:
            return super(wxAnimation, self).GetFrameCount()

        return self.m_refData.GetFrameCount()

    def GetDelay(self, i):
        if self.m_isSuper:
            return super(wxAnimation, self).GetDelay(i)

        return self.m_refData.GetDelay(i)

    def GetFrame(self, i):
        if self.m_isSuper:
            return super(wxAnimation, self).GetFrame(i)

        img = self.m_refData.ConvertToImage(i)
        if not img or not img.IsOk():
            return wx.NullImage

        return img

    def GetSize(self):
        if self.m_isSuper:
            return super(wxAnimation, self).GetSize()

        return self.m_refData.GetAnimationSize()

    def LoadFile(self, filename, type=wxANIMATION_TYPE_ANY):
        if self.m_isSuper:
            return super(wxAnimation, self).LoadFile(filename, type)
        try:
            with open(filename, 'rb') as f:
                stream = io.BytesIO(bytearray(f.read()))
        except:
            return False

        return self.Load(stream, type)

    def Load(self, stream, type=wxANIMATION_TYPE_ANY):
        if self.m_isSuper:
            return super(wxAnimation, self).Load(stream, type)

        # self.UnRef()

        if type == wxANIMATION_TYPE_ANY:
            for handler in wxAnimation.sm_handlers:
                if handler.CanRead(stream):
                    # do a copy of the handler from the static list which we will own
                    # as our reference data
                    self.m_refData = handler.Clone()
                    return self.m_refData.Load(stream)

            return False

        handler = self.FindHandler(type)

        if handler == 0:
            return False

        # do a copy of the handler from the static list which we will own
        # as our reference data
        self.m_refData = handler.Clone()

        if hasattr(stream, 'seek') and not self.m_refData.CanRead(stream):
            return False
        else:
            return self.m_refData.Load(stream)

    def GetFramePosition(self, frame):
        if not self.m_isSuper:
            return self.m_refData.GetFramePosition(frame)

    def GetFrameSize(self, frame):
        if not self.m_isSuper:
            return self.m_refData.GetFrameSize(frame)

    def GetDisposalMethod(self, frame):
        if not self.m_isSuper:
            return self.m_refData.GetDisposalMethod(frame)

    def GetTransparentColour(self, frame):
        if not self.m_isSuper:
            return self.m_refData.GetTransparentColour(frame)

    def GetBackgroundColour(self):
        if not self.m_isSuper:
            return self.m_refData.GetBackgroundColour()

    @staticmethod
    def GetHandlers():
        return wxAnimation.sm_handlers[:]

    @staticmethod
    def AddHandler(handler):
        # Check for an existing handler of the type being added.
        if wxAnimation.FindHandler(handler.GetType()) == 0:
            wxAnimation.sm_handlers.append(handler)
        else:
            # This is not documented behaviour, merely the simplest 'fix'
            # for preventing duplicate additions.  If someone ever has
            # a good reason to add and remove duplicate handlers (and they
            # may) we should probably refcount the duplicates.
            pass

    @staticmethod
    def InsertHandler(handler):
        wxAnimation.AddHandler(handler)

    @staticmethod
    def FindHandler(animType):
        for handler in wxAnimation.sm_handlers:
            if handler.GetType() == animType:
                return handler

        return 0

    @staticmethod
    def CleanUpHandlers():
        del wxAnimation.sm_handlers[:]

    @staticmethod
    def InitStandardHandlers():
        wxAnimation.sm_handlers.append(wxPNGDecoder())


wxAnimation.InitStandardHandlers()

