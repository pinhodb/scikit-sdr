#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 gr-grsksdr author.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#
import logging

import numpy as np
import sksdr
from gnuradio import gr

_log = logging.getLogger(__name__)
#_log.setLevel(logging.DEBUG)

class fir_interpolator(gr.interp_block):
    """
    docstring for block fir_interpolator
    """
    def __init__(self, upsampling, coeffs):
        gr.interp_block.__init__(self,
                                 name='fir_interpolator',
                                 in_sig=[np.complex64],
                                 out_sig=[np.complex64], interp=upsampling)
        self.interp = sksdr.FirInterpolator(upsampling, coeffs)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        self.interp(in0, out)
        return len(out)
