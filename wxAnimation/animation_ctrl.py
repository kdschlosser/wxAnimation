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

from .animation import (
    wxANIMATION_TYPE_INVALID,
    wxANIMATION_TYPE_ANI,
    wxANIMATION_TYPE_GIF,
    wxANIMATION_TYPE_PNG,
    wxANIMATION_TYPE_ANY,
    wxAC_NO_AUTORESIZE,
    wxAC_DEFAULT_STYLE,
    wxAnimation
)

from .animation_decoder import (
    wxANIM_DONOTREMOVE,
    wxANIM_TOBACKGROUND,
    wxANIM_UNSPECIFIED,
    wxANIM_TOPREVIOUS
)


class wxAnimationCtrl(wx.adv.wxAnimationCtrl):

    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        anim=wx.adv.NullAnimation,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.adv.AC_DEFAULT_STYLE,
        name=wx.adv.AnimationCtrlNameStr
    ):
        self.m_animation = anim

        if anim.GetType() != wxANIMATION_TYPE_PNG:
            super(wxAnimationCtrl, self).__init__(parent, id, anim, pos, size, style, name)
        else:
            self.m_bmpStatic = wx.Bitmap(0, 0)
            self.m_bmpStaticReal = wx.Bitmap(0, 0)
            self.m_currentFrame = 0
            self.m_looped = False
            self.m_timer = None
            self.m_animation = wxAnimation()
            self.m_isPlaying = False
            self.m_useWinBackgroundColour = True
            self.m_backingStore = wx.Bitmap(0, 0)

    def Init(self):
        self.m_currentFrame = 0
        self.m_looped = False
        self.m_isPlaying = False
        # use the window background colour by default to be consistent
        # with the GTK+ native version
        self.m_useWinBackgroundColour = True

    def Create(
        self,
        parent,
        id=wx.ID_ANY,
        animation=wx.adv.NullAnimation,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.adv.AC_DEFAULT_STYLE,
        name=wx.adv.AnimationCtrlNameStr
    ):
        if animation.GetType() != wxANIMATION_TYPE_PNG:
            return super(wxAnimationCtrl, self).Create(parent, id, animation, pos, size, style, name)

        self.m_timer = wx.Timer()
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetAnimation(animation)
        return True

    def LoadFile(self, filename, type=wxANIMATION_TYPE_ANY):
        if type != wxANIMATION_TYPE_PNG:
            return super(wxAnimationCtrl, self).LoadFile(filename, type)

        try:
            with open(filename, 'rb') as f:
                fis = io.BytesIO(f.read())
        except IOError:
            return False

        return self.Load(fis, type)

    def Load(self, stream, type=wxANIMATION_TYPE_ANY):
        if type != wxANIMATION_TYPE_PNG:
            return super(wxAnimationCtrl, self).Load(stream, type)

        anim = wxAnimation()
        if not anim.Load(stream, type):
            return False

        self.SetAnimation(anim)

    def Stop(self):
        if self.m_animation.GetType() != wxANIMATION_TYPE_PNG:
            return super(wxAnimationCtrl, self).Stop()

        self.m_timer.Stop()
        self.m_isPlaying = False
        self.m_currentFrame = 0
        self.DisplayStaticImage()

    def Play(self, looped=True):
        if self.m_animation.GetType() != wxANIMATION_TYPE_PNG:
            return super(wxAnimationCtrl, self).Play()

        if not self.m_animation.IsOk():
            return False

        self.m_looped = looped
        self.m_currentFrame = 0

        if not self.RebuildBackingStoreUpToFrame(0):
            return False

        self.m_isPlaying = True

        self.ClearBackground()
        clientDC = wx.ClientDC(self)
        self.DrawCurrentFrame(clientDC)

        delay = self.m_animation.GetDelay(0)
        if delay == 0:
            delay = 1

        self.m_timer.Start(delay, True)

        return True

    def IsPlaying(self):
        if self.m_animation.GetType() != wxANIMATION_TYPE_PNG:
            return super(wxAnimationCtrl, self).IsPlaying()

        return self.m_isPlaying

    def SetAnimation(self, animation):
        if self.m_animation.GetType() != wxANIMATION_TYPE_PNG:
            if super(wxAnimationCtrl, self).IsPlaying():
                super(wxAnimationCtrl, self).Stop()

        if animation.GetType() != wxANIMATION_TYPE_PNG:
            return super(wxAnimationCtrl, self).SetAnimation(animation)

        self.m_animation = animation
        if not self.m_animation.IsOk():
            self.DisplayStaticImage()
            return

        if self.m_animation.GetBackgroundColour() == wx.NullColour:
            self.SetUseWindowBackgroundColour()

        if not self.HasFlag(wxAC_NO_AUTORESIZE):
            self.FitToAnimation()

        self.DisplayStaticImage()

    def GetAnimation(self):
        if self.m_animation.GetType() != wxANIMATION_TYPE_PNG:
            return super(wxAnimationCtrl, self).GetAnimation()

        return self.m_animation

    def SetInactiveBitmap(self, bmp):
        if self.m_animation.GetType() != wxANIMATION_TYPE_PNG:
            return super(wxAnimationCtrl, self).SetInactiveBitmap(bmp)

        self.m_bmpStatic = bmp
        self.m_bmpStaticReal = bmp

        # if not playing, update the control now
        # NOTE: DisplayStaticImage() will call UpdateStaticImage automatically
        if not self.IsPlaying():
            self.DisplayStaticImage()

    def SetBackgroundColour(self, col):
        if not super(wx.Control, self).SetBackgroundColour(col):
            return False

        if not self.IsPlaying():
            self.DisplayStaticImage()

        return True

    def OnPaint(self, _):
        # VERY IMPORTANT: the wxPaintDC *must* be created in any case
        dc = wx.PaintDC(self)

        if self.m_backingStore.IsOk():
            # NOTE: we draw the bitmap explicitly ignoring the mask (if any);
            #       i.e. we don't want to combine the backing store with the
            #       possibly wrong preexisting contents of the window!
            dc.DrawBitmap(self.m_backingStore, 0, 0, False)  # no mask
        else:
            # m_animation is not valid and thus we don't have a valid backing store...
            # clear then our area to the background colour
            self.DisposeToBackground(dc)

    def OnTimer(self, _):
        self.m_currentFrame += 1
        if self.m_currentFrame == self.m_animation.GetFrameCount():
            # Should a non-looped animation display the last frame?
            if not self.m_looped:
                self.Stop()
                return

            else:
                self.m_currentFrame = 0  # let's restart

        self.IncrementalUpdateBackingStore()

        dc = wx.ClientDC(self)
        self.DrawCurrentFrame(dc)

        delay = self.m_animation.GetDelay(self.m_currentFrame)
        if delay == 0:
            delay = 1  # 0 is invalid timeout for wxTimer.
        self.m_timer.Start(delay, True)

    def OnSize(self, _):
        # NB: resizing an animation control may take a lot of time
        #     for big animations as the backing store must be
        #     extended and rebuilt. Try to avoid it e.g. using
        #     a null proportion value for your wxAnimationCtrls
        #     when using them inside sizers.
        if self.m_animation.IsOk():
            # be careful to change the backing store *only* if we are
            # playing the animation as otherwise we may be displaying
            # the inactive bitmap and overwriting the backing store
            # with the last played frame is wrong in this case
            if self.IsPlaying():
                if not self.RebuildBackingStoreUpToFrame(self.m_currentFrame):
                    self.Stop()  # in case we are playing

    def SetUseWindowBackgroundColour(self, useWinBackground=True):
        if self.m_animation.GetType() != wxANIMATION_TYPE_PNG:
            return

        self.m_useWinBackgroundColour = useWinBackground

    def IsUsingWindowBackgroundColour(self):
        if self.m_animation.GetType() != wxANIMATION_TYPE_PNG:
            return True

        return self.m_useWinBackgroundColour

    def DrawCurrentFrame(self, dc):
        assert self.m_backingStore.IsOk()

        #  m_backingStore always contains the current frame
        dc.DrawBitmap(self.m_backingStore, 0, 0, True)  # use mask in case it's present

    def GetBackingStore(self):
        return self.m_backingStore

    def FitToAnimation(self):
        self.SetSize(self.m_animation.GetSize())

    def DisposeToBackground(self, dc=None, pos=None, sz=None):
        if dc is None:
            # clear the backing store
            dc = wx.MemoryDC()
            dc.SelectObject(self.m_backingStore)
            if dc.IsOk():
                self.DisposeToBackground(dc)
        else:
            if self.IsUsingWindowBackgroundColour():

                col = self.GetBackgroundColour()
            else:
                col = self.m_animation.GetBackgroundColour()

            brush = wx.Brush(col)

            if pos is None and sz is None:
                dc.SetBackground(brush)
                dc.Clear()

            else:
                dc.SetBrush(brush)
                dc.SetPen(wx.TRANSPARENT_PEN)
                dc.DrawRectangle(pos, sz)

    def IncrementalUpdateBackingStore(self):
        dc = wx.MemoryDC()
        dc.SelectObject(self.m_backingStore)

        # OPTIMIZATION:
        # since wxAnimationCtrl can only play animations forward, without skipping
        # frames, we can be sure that m_backingStore contains the m_currentFrame-1
        # frame and thus we just need to dispose the m_currentFrame-1 frame and
        # render the m_currentFrame-th one.

        if self.m_currentFrame == 0:
            # before drawing the first frame always dispose to bg colour
            self.DisposeToBackground(dc)
        else:
            dispose_method = self.m_animation.GetDisposalMethod(self.m_currentFrame - 1)

            if dispose_method == wxANIM_TOBACKGROUND:
                self.DisposeToBackground(
                    dc,
                    self.m_animation.GetFramePosition(self.m_currentFrame - 1),
                    self.m_animation.GetFrameSize(self.m_currentFrame - 1)
                )
            elif dispose_method == wxANIM_TOPREVIOUS:
                # this disposal should never be used too often.
                # E.g. GIF specification explicitly say to keep the usage of this
                #      disposal limited to the minimum.
                # In fact it may require a lot of time to restore
                if self.m_currentFrame == 1:
                    # if 0-th frame disposal is to restore to previous frame,
                    # the best we can do is to restore to background
                    self.DisposeToBackground(dc)
                else:
                    if not self.RebuildBackingStoreUpToFrame(self.m_currentFrame - 2):
                        self.Stop()

        # now just draw the current frame on the top of the backing store
        self.DrawFrame(dc, self.m_currentFrame)
        dc.SelectObject(wx.NullBitmap)

    def UpdateStaticImage(self):

        if not self.m_bmpStaticReal.IsOk() or not self.m_bmpStatic.IsOk():
            return

        # if given bitmap is not of the right size, recreate m_bmpStaticReal accordingly
        sz = self.GetClientSize()
        if (
            sz.GetWidth() != self.m_bmpStaticReal.GetWidth() or
            sz.GetHeight() != self.m_bmpStaticReal.GetHeight()
        ):
            if (
                not self.m_bmpStaticReal.IsOk() or
                self.m_bmpStaticReal.GetWidth() != sz.GetWidth() or
                self.m_bmpStaticReal.GetHeight() != sz.GetHeight()
            ):
                # need to (re)create m_bmpStaticReal
                if not self.m_bmpStaticReal.Create(sz.GetWidth(), sz.GetHeight(), self.m_bmpStatic.GetDepth()):
                    self.m_bmpStatic = wx.NullBitmap
                    return

            if (
                self.m_bmpStatic.GetWidth() <= sz.GetWidth() and
                self.m_bmpStatic.GetHeight() <= sz.GetHeight()
            ):
                # clear the background of m_bmpStaticReal
                brush = wx.Brush(self.GetBackgroundColour())
                dc = wx.MemoryDC()
                dc.SelectObject(self.m_bmpStaticReal)
                dc.SetBackground(brush)
                dc.Clear()

                # center the user-provided bitmap in m_bmpStaticReal
                dc.DrawBitmap(
                    self.m_bmpStatic,
                    (sz.GetWidth() - self.m_bmpStatic.GetWidth()) / 2,
                    (sz.GetHeight() - self.m_bmpStatic.GetHeight()) / 2,
                    True  # use mask */
                )
            else:
                # the user-provided bitmap is bigger than our control, strech it
                temp = self.m_bmpStatic.ConvertToImage()
                temp.Rescale(sz.GetWidth(), sz.GetHeight(), wx.IMAGE_QUALITY_HIGH)
                self.m_bmpStaticReal = wx.Bitmap(temp)

    def RebuildBackingStoreUpToFrame(self, frame):
        # if we've not created the backing store yet or it's too
        # small, then recreate it
        sz = self.m_animation.GetSize()
        winsz = self.GetClientSize()
        w = min(sz.GetWidth(), winsz.GetWidth())
        h = min(sz.GetHeight(), winsz.GetHeight())

        if (
            not self.m_backingStore.IsOk() or
            self.m_backingStore.GetWidth() < w or
            self.m_backingStore.GetHeight() < h
        ):

            if not self.m_backingStore.Create(w, h):
                return False

        dc = wx.MemoryDC()
        dc.SelectObject(self.m_backingStore)

        # Draw the background
        self.DisposeToBackground(dc)

        # Draw all intermediate frames that haven't been removed from the animation
        for i in range(frame):
            if (
                self.m_animation.GetDisposalMethod(i) == wxANIM_DONOTREMOVE or
                self.m_animation.GetDisposalMethod(i) == wxANIM_UNSPECIFIED
            ):
                self.DrawFrame(dc, i)

            elif self.m_animation.GetDisposalMethod(i) == wxANIM_TOBACKGROUND:
                self.DisposeToBackground(
                    dc,
                    self.m_animation.GetFramePosition(i),
                    self.m_animation.GetFrameSize(i)
                )

        # finally draw this frame
        self.DrawFrame(dc, frame)
        dc.SelectObject(wx.NullBitmap)
        dc.Destroy()
        del dc

        return True

    def DrawFrame(self, dc, frame):
        # PERFORMANCE NOTE:
        # this draw stuff is not as fast as possible: the wxAnimationDecoder
        # needs first to convert from its internal format to wxImage RGB24;
        # the wxImage is then converted as a wxBitmap and finally blitted.
        # If wxAnimationDecoder had a function to convert directly from its
        # internal format to a port-specific wxBitmap, it would be somewhat faster.
        bmp = wx.Bitmap(self.m_animation.GetFrame(frame))
        dc.DrawBitmap(
            bmp,
            self.m_animation.GetFramePosition(frame),
            True  # use mask
        )

    def DisplayStaticImage(self):
        assert not self.IsPlaying()

        # m_bmpStaticReal will be updated only if necessary...
        self.UpdateStaticImage()

        if self.m_bmpStaticReal.IsOk():

            # copy the inactive bitmap in the backing store
            # eventually using the mask if the static bitmap has one
            if self.m_bmpStaticReal.GetMask():
                temp = wx.MemoryDC()
                temp.SelectObject(self.m_backingStore)
                self.DisposeToBackground(temp)
                temp.DrawBitmap(self.m_bmpStaticReal, 0, 0, True)  # use mask

            else:
                self.m_backingStore = self.m_bmpStaticReal
        else:
            # put in the backing store the first frame of the animation
            if (
                not self.m_animation.IsOk() or
                not self.RebuildBackingStoreUpToFrame(0)
            ):
                self.m_animation = wx.adv.NullAnimation
                self.DisposeToBackground()

        self.Refresh()

    def DoGetBestSize(self):
        if self.m_animation.GetType() != wxANIMATION_TYPE_PNG:
            return super(wxAnimationCtrl, self).DoGetBestSize()

        if self.m_animation.IsOk() and not self.HasFlag(wxAC_NO_AUTORESIZE):
            return self.m_animation.GetSize()

        return wx.Size(100, 100)








