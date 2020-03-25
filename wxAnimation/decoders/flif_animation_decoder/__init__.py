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

from ... import animation_decoder
from ...animation import wxAnimation

import wx
import io
from .filebuf import FileBuffer

from ._libflif import (
    lib as libflif,
    ffi
)

wxANIMATION_TYPE_FLIF = 5

wxFLIF_OK = 0  # everything was OK
wxFLIF_INVFORMAT = 1  # error in PNG header
wxFLIF_MEMERR = 2  # error allocating memory

FLIF_HEADER = 'FLIF'


class wxFLIFDecoder(animation_decoder.wxAnimationDecoder):

    def __init__(self):
        self.m_frames = []
        self.m_plays = 0
        super(wxFLIFDecoder, self).__init__()

    def GetData(self, frame):
        return self.m_frames[frame].image

    def GetPalette(self, frame):
        pass

    def GetFrameSize(self, frame):
        frame = self.m_frames[frame]
        return wx.Size(frame.width, frame.height)

    def GetFramePosition(self, frame):
        return wx.Point(0, 0)

    def GetDisposalMethod(self, frame):
        return 0

    def GetDelay(self, frame):
        return self.m_frames[frame].delay

    def IsAnimation(self):
        return self.m_nFrames > 1

    def LoadFLIF(self, stream):
        stream.seek(0)
        stream_data = bytearray(stream.read())

        header = stream_data[:30]
        info = libflif.flif_read_info_from_memory(header, 30)

        try:
            channels = libflif.flif_info_get_nb_channels(info)
            if channels == 1:
                if libflif.flif_info_get_depth(info) == 1:
                    mode = 2
                else:
                    mode = 2
            elif channels == 3:
                mode = 3
            elif channels == 4:
                mode = 4
            else:
                return wxFLIF_INVFORMAT

            context = libflif.flif_create_decoder()

            try:
                buf = io.BytesIO()

                with FileBuffer(buf) as fb:
                    libflif.flif_decoder_decode_memory(context, ffi.from_buffer(fb.buffer), fb.size)

                self.m_nFrames = libflif.flif_info_num_images(info)
                self.m_plays = libflif.flif_decoder_num_loops(context)
                self.m_szAnimation = wx.Size(
                    libflif.flif_info_get_width(info),
                    libflif.flif_info_get_height(info)
                )

                for i in range(self.m_nFrames):
                    image_context = libflif.flif_decoder_get_image(context, i)
                    delay = libflif.flif_image_get_frame_delay(image_context)
                    height = libflif.flif_image_get_height(image_context)
                    width = libflif.flif_image_get_width(image_context)

                    if mode in (1, 2):
                        buf_size = width * height
                        image_buf = bytearray(buf_size)
                        libflif.flif_image_read_into_GRAY8(image_context, ffi.from_buffer(image_buf), buf_size)
                    elif mode == 3:
                        buf_size = width * height * 3 + width
                        image_buf = bytearray(buf_size)
                        libflif.flif_image_read_into_RGB8(image_context, ffi.from_buffer(image_buf), buf_size)
                    else:
                        buf_size = width + height * 4
                        image_buf = bytearray(buf_size)
                        libflif.flif_image_read_into_RGBA8(image_context, ffi.from_buffer(image_buf), buf_size)

                    image_buf = bytes(image_buf)

                    image = wx.Image()
                    image.InitAlpha()
                    image.SetData(image_buf, width, height)

                    frame = FLIFFrame(
                        i,
                        width,
                        height,
                        delay
                    )

                    frame.image = image

                    self.m_frames += [frame]
            finally:
                libflif.flif_destroy_decoder(context)

        finally:
            libflif.flif_destroy_info(info)

        return wxFLIF_OK

    def Destroy(self):
        assert self.m_nFrames == len(self.m_frames)

        for frame in self.m_frames:
            frame.Destroy()

        del self.m_frames[:]
        self.m_nFrames = 0

    def Load(self, stream):
        return self.LoadFLIF(stream) == wxFLIF_OK

    def ConvertToImage(self, frame):
        frame = self.m_frames[frame]
        bmp = wx.Bitmap(frame.image, wx.BITMAP_TYPE_PNG)
        return bmp.ConvertToImage()

    def Clone(self):
        return wxFLIFDecoder()

    def GetType(self):
        return wxANIMATION_TYPE_FLIF

    def DrawFrame(self, dc, frame):
        bmp = wx.Bitmap(self.GetData(frame))
        dc.DrawBitmap(
            bmp,
            self.GetFramePosition(frame),
            True  # use mask
        )

    def DoCanRead(self, stream):
        data = stream.read(4)
        return data == FLIF_HEADER


NullFLIFDecoder = wxFLIFDecoder()


class FLIFFrame(object):

    def __init__(
            self,
            index,
            width,
            height,
            delay,
    ):
        self.index = index
        self.width = width
        self.height = height
        self.image = None
        self.delay = delay

    def Destroy(self):
        self.image.Destroy()


wxAnimation.AddHandler(wxFLIFDecoder())
