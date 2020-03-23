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

from __future__ import print_function
try:
    __import__('wx')
except:
    print('wxPython 4.x is required to use wxAnimation')
    raise

from .animation_ctrl import (
    wxAnimationCtrl,
    wxANIMATION_TYPE_INVALID,
    wxANIMATION_TYPE_ANI,
    wxANIMATION_TYPE_GIF,
    wxANIMATION_TYPE_PNG,
    wxANIMATION_TYPE_ANY,
    wxAC_NO_AUTORESIZE,
    wxAC_DEFAULT_STYLE,
    wxAnimation,
    wxANIM_DONOTREMOVE,
    wxANIM_TOBACKGROUND,
    wxANIM_UNSPECIFIED,
    wxANIM_TOPREVIOUS
)

AnimationCtrl = wxAnimationCtrl
ANIMATION_TYPE_INVALID = wxANIMATION_TYPE_INVALID
ANIMATION_TYPE_ANI = wxANIMATION_TYPE_ANI
ANIMATION_TYPE_GIF = wxANIMATION_TYPE_GIF
ANIMATION_TYPE_PNG = wxANIMATION_TYPE_PNG
ANIMATION_TYPE_ANY = wxANIMATION_TYPE_ANY
AC_NO_AUTORESIZE = wxAC_NO_AUTORESIZE
AC_DEFAULT_STYLE = wxAC_DEFAULT_STYLE
Animation = wxAnimation
ANIM_DONOTREMOVE = wxANIM_DONOTREMOVE
ANIM_TOBACKGROUND = wxANIM_TOBACKGROUND
ANIM_UNSPECIFIED = wxANIM_UNSPECIFIED
ANIM_TOPREVIOUS = wxANIM_TOPREVIOUS


