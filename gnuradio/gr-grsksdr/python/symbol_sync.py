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
from logging import DEBUG

import numpy as np
from gnuradio import gr

import sksdr

_log = logging.getLogger(__name__)
#_log.setLevel(logging.DEBUG)

class symbol_sync(gr.basic_block):
    """
    docstring for block symbol_sync
    """
    def __init__(self, modulation, sps, damp_factor, norm_loop_bw, K, A):
        self.sps = sps
        gr.basic_block.__init__(self,
                                name='symbol_sync',
                                in_sig=[np.complex64],
                                out_sig=[np.complex64])
        self.ssync = sksdr.SymbolSync(eval(modulation), sps, damp_factor, norm_loop_bw, K, A)

    def forecast(self, noutput_items, ninput_items_required):
        # setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = int(np.ceil(noutput_items * self.sps))

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        nout = len(out)
        ret, ninp, _ = self.ssync(in0, nout)
        nret = len(ret)
        _log.debug('len in0/out0/inp/ret: %d/%d/%d/%d', len(in0), nout, ninp, nret)
        _log.log(DEBUG-1, ret)
        out[:nret] = ret
        self.consume(0, ninp)
        return nret
