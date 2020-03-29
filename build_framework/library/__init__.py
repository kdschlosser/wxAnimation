# -*- coding: utf-8 -*-

import sys
import distutils.log

# this next bit of code is for convience, If you do not have a complex build arrangement and your library is not
# OS dependent meaning no special flags need to be set based on the OS or macros that have to be set based on the OS
# you can import the library module and pass any parameters needed directly to the constructor library.Library()
# and the rest is taken care of internally.

distutils.log.info('Getting Library for platform {0}'.format(sys.platform))

if sys.platform.startswith('win'):
    from .windows import Library
elif sys.platform.startswith("cygwin"):
    from .cygwin import Library
elif sys.platform.startswith("darwin"):
    from .darwin import Library
elif sys.platform.startswith('freebsd'):
    from .freebsd import Library
elif sys.platform.startswith('sunos'):
    from .sunos import Library
elif sys.platform.startswith('linux'):
    from .linux import Library
else:
    raise RuntimeError(
        "No Library available for platform {0}".format(sys.platform)
    )