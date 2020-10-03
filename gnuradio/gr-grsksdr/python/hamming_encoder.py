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
from gnuradio import gr

import sksdr

_log = logging.getLogger(__name__)
#_log.setLevel(logging.DEBUG)

class hamming_encoder(gr.basic_block):
    """
    docstring for block hamming_encoder
    """
    def __init__(self, ntotal, ndata):
        self.ntotal = ntotal
        self.ndata = ndata
        gr.basic_block.__init__(self,
                                name='hamming_encoder',
                                in_sig=[np.uint8],
                                out_sig=[np.uint8])
        self.set_output_multiple(self.ntotal)
        self.fec = sksdr.Hamming(self.ntotal, self.ndata)

    def forecast(self, noutput_items, ninput_items_required):
        # setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        nout = len(out)
        _log.debug('len(in0), nout: %d/%d', len(in0), nout)
        for i, j in zip(range(0, len(in0), self.ndata), range(0, nout, self.ntotal)):
            iend = i + self.ndata
            jend = j + self.ntotal
            out[j : jend] = self.fec.encode(in0[i : iend])

        _log.debug('iend, jend: %d, %d', iend, jend)
        self.consume(0, iend)
        return jend
