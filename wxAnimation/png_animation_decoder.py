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

from . import animation_decoder
import wx
import io
import struct
import binascii

wxANIMATION_TYPE_PNG = 4

PNG_HEADER = bytearray('\x89\x50\x4E\x47\x0D\x0A\x1A\x0A')

PNG_MARKER_IHDR = 'IHDR'  # (single use) Shall be first
PNG_MARKER_PLTE = 'PLTE'  # (single use) Before first IDAT
PNG_MARKER_IDAT = 'IDAT'  # (multiple use) Multiple IDAT chunks shall be consecutive
PNG_MARKER_IEND = 'IEND'  # (single use) Shall be last
PNG_MARKER_cHRM = 'cHRM'  # (single use) Before PLTE and IDAT
PNG_MARKER_gAMA = 'gAMA'  # (single use) Before PLTE and IDAT
PNG_MARKER_sBIT = 'sBIT'  # (single use) Before PLTE and IDAT
PNG_MARKER_bKGD = 'bKGD'  # (single use) After PLTE; before IDAT
PNG_MARKER_hIST = 'hIST'  # (single use) After PLTE; before IDAT
PNG_MARKER_tRNS = 'tRNS'  # (single use) After PLTE; before IDAT
PNG_MARKER_pHYs = 'pHYs'  # (single use) Before IDAT
PNG_MARKER_sPLT = 'sPLT'  # (multiple use) Before IDAT
PNG_MARKER_tIME = 'tIME'  # (single use) None
PNG_MARKER_iTXt = 'iTXt'  # (multiple use) utf-8 encoding
PNG_MARKER_tEXt = 'tEXt'  # (multiple use) latin-1 encoding
PNG_MARKER_zTXt = 'zTXt'  # (multiple use) latin-1 encoding compressed with zlib
PNG_MARKER_fdAT = 'fdAT'  # frame data (png data)
PNG_MARKER_fcTL = 'fcTL'  # frame control data - width, height, x offset, y offset, blend_op, dispose_op, delay....
PNG_MARKER_acTL = 'acTL'  # animation control data

# (single use) Before PLTE and IDAT. If the iCCP chunk is present, the sRGB chunk should not be present.
PNG_MARKER_iCCP = 'iCCP'
# (single use) Before PLTE and IDAT. If the sRGB chunk is present, the iCCP chunk should not be present.
PNG_MARKER_sRGB = 'sRGB'

MARKERS_BEFORE_IDAT = [
    PNG_MARKER_cHRM,
    PNG_MARKER_gAMA,
    PNG_MARKER_iCCP,
    PNG_MARKER_sBIT,
    PNG_MARKER_sRGB,
    PNG_MARKER_bKGD,
    PNG_MARKER_hIST,
    PNG_MARKER_tRNS,
    PNG_MARKER_pHYs,
    PNG_MARKER_sPLT,
    PNG_MARKER_PLTE,
]


def _parse_apng(data):
    i = 8
    while i < len(data):
        data_len, = struct.unpack("!I", data[i:i + 4])
        chunk_type = data[i + 4:i + 8].decode("latin-1")

        yield chunk_type, data[i:i + data_len + 12]

        i += data_len + 12


def _make_chunk(chunk_type, chunk_data):
    out = struct.pack("!I", len(chunk_data))

    chunk_data = chunk_type.encode("latin-1") + chunk_data

    out += chunk_data + struct.pack("!I", binascii.crc32(chunk_data) & 0xFFFFFFFF)
    return chunk_type, out


class wxPNGDecoder(animation_decoder.wxAnimationDecoder):

    def __init__(self):
        self.m_frames = []
        self.m_plays = 0
        super(wxPNGDecoder, self).__init__()

    def GetData(self, frame):
        return self.m_frames[frame].image

    def GetPalette(self, frame):
        return self.m_frames[frame].pal

    def GetFrameSize(self, frame):
        frame = self.m_frames[frame]
        return wx.Size(frame.width, frame.height)

    def GetFramePosition(self, frame):
        frame = self.m_frames[frame]
        return wx.Point(frame.x_offset, frame.y_offset)

    def GetDisposalMethod(self, frame):
        return self.m_frames[frame].dispose_op

    def GetBlendMethod(self, frame):
        return self.m_frames[frame].blend_op

    def GetDelay(self, frame):
        return self.m_frames[frame].delay

    def IsAnimation(self):
        return self.m_nFrames > 1

    def LoadPNG(self, stream):
        stream.seek(0)
        stream_data = bytearray(stream.read())
        if stream_data[:8] != PNG_HEADER:
            return wxPNG_INVFORMAT

        hdr = None
        head_chunks = []
        end = _make_chunk(PNG_MARKER_IEND, bytearray())

        frame_chunks = []
        frames = []
        num_frames = 0
        num_plays = 0
        frame_has_head_chunks = False

        control = None

        for chunk_type, chunk_data in _parse_apng(stream_data):
            if chunk_type == PNG_MARKER_IHDR:
                hdr = (chunk_type, chunk_data)
                frame_chunks.append((chunk_type, chunk_data))

            elif chunk_type == PNG_MARKER_acTL:
                num_frames, num_plays = struct.unpack("!II", chunk_data[8:-4])
                continue

            elif chunk_type == PNG_MARKER_fcTL:
                if any(type_ == PNG_MARKER_IDAT for type_, data in frame_chunks):
                    frame_chunks.append(end)
                    control.image = PNGImage(frame_chunks)
                    frames.append(control)
                    frame_has_head_chunks = False
                    control = PNGFrame(*struct.unpack("!IIIIIHHbb", chunk_data.split(PNG_MARKER_fcTL)[-1][:-4]))
                    hdr = _make_chunk(
                        PNG_MARKER_IHDR,
                        struct.pack("!II", control.width, control.height) + hdr[1][16:-4]
                    )

                    frame_chunks = [hdr]
                else:
                    control = PNGFrame(*struct.unpack("!IIIIIHHbb", chunk_data.split(PNG_MARKER_fcTL)[-1][:-4]))

            elif chunk_type == PNG_MARKER_IDAT:
                if not frame_has_head_chunks:
                    frame_chunks.extend(head_chunks)
                    frame_has_head_chunks = True

                frame_chunks.append((chunk_type, chunk_data))

            elif chunk_type == PNG_MARKER_fdAT:
                if not frame_has_head_chunks:
                    frame_chunks.extend(head_chunks)
                    frame_has_head_chunks = True
                frame_chunks.append(_make_chunk(PNG_MARKER_IDAT, chunk_data[12:-4]))

            elif chunk_type == PNG_MARKER_IEND:
                frame_chunks.append(end)
                control.image = PNGImage(frame_chunks)
                frames.append(control)
                break

            elif chunk_type in MARKERS_BEFORE_IDAT:
                head_chunks.append((chunk_type, chunk_data))

            else:
                frame_chunks.append((chunk_type, chunk_data))

        self.m_frames = sorted(frames, key=lambda x: x.index)
        self.m_plays = num_plays
        self.m_nFrames = num_frames

        max_width = 0
        max_height = 0
        for frame in self.m_frames:
            max_width = max(frame.width, max_width)
            max_height = max(frame.height, max_height)

        self.m_szAnimation = wx.Size(max_width, max_height)
        return wxPNG_OK

    def Destroy(self):
        assert self.m_nFrames == len(self.m_frames)

        for frame in self.m_frames:
            frame.Destroy()

        del self.m_frames[:]
        self.m_nFrames = 0

    def Load(self, stream):
        return self.LoadPNG(stream) == wxPNG_OK

    def ConvertToImage(self, frame):
        frame = self.m_frames[frame]
        bmp = wx.Bitmap(frame.image, wx.BITMAP_TYPE_PNG)
        return bmp.ConvertToImage()

    def Clone(self):
        return wxPNGDecoder()

    def GetType(self):
        return wxANIMATION_TYPE_PNG

    def DoCanRead(self, stream):
        data = stream.read(8)
        return data == PNG_HEADER


NullPNGDecoder = wxPNGDecoder()

# all color components of the frame, including alpha,
# overwrite the current contents of the frame's output buffer region.
wxANIM_APNG_BLENDOP_SOURCE = 0

# frame should be composited onto the output buffer based on its alpha,
# using a simple OVER operation
wxANIM_APNG_BLENDOP_OVER = 1

wxPNG_OK = 0  # everything was OK
wxPNG_INVFORMAT = 1  # error in PNG header
wxPNG_MEMERR = 2  # error allocating memory
wxPNG_TRUNCATED = 3  # file appears to be truncated


def PNGImage(frame_chunks):
    chunks = bytearray(PNG_HEADER)
    for c in frame_chunks:
        chunks.extend(c[1])

    stream = io.BytesIO(chunks)
    return wx.Image(stream, wx.BITMAP_TYPE_PNG)


class PNGFrame(object):

    def __init__(
            self,
            index,
            width,
            height,
            x_offset,
            y_offset,
            delay_num,
            delay_den,
            dispose_op,
            blend_op
    ):
        self.index = index
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.delay_num = delay_num
        self.delay_den = delay_den
        self.dispose_op = dispose_op
        self.blend_op = blend_op
        self.image = None

        if delay_num == 0:
            self.delay = 0.0
        else:
            if delay_den == 0:
                delay_den = 100.0

            self.delay = (float(delay_num) / float(delay_den)) * 1000.0

