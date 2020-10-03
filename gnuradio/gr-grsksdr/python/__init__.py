#
# Copyright 2008,2009 Free Software Foundation, Inc.
#
# This application is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This application is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# The presence of this file turns this directory into a Python package

"""
This is the GNU Radio GRSKSDR module. Place your Python package
description here (python/__init__.py).
"""
from __future__ import unicode_literals

import logging

from .agc import agc
from .coarse_freq_comp import coarse_freq_comp
from .descrambler import descrambler
from .fir_decimator import fir_decimator
from .fir_interpolator import fir_interpolator
from .frame_sync import frame_sync
from .freq_sync import freq_sync
from .hamming_decoder import hamming_decoder
from .hamming_encoder import hamming_encoder
from .phase_offset_est import phase_offset_est
from .psk_demod import psk_demod
from .psk_mod import psk_mod
from .scrambler import scrambler
from .symbol_sync import symbol_sync

# import swig generated symbols into the grsksdr namespace
try:
    # this might fail if the module is python-only
    from .grsksdr_swig import *
except ImportError:
    pass

_log = logging.getLogger(__name__)

def _setupLog():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    _log.addHandler(handler)
    _log.setLevel(logging.INFO)

_setupLog()
