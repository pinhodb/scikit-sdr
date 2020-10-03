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

class frame_sync(gr.basic_block):
    """
    docstring for block frame_sync
    """
    def __init__(self, preamble, det_thr, frame_size):
        self.frame_size = frame_size
        gr.basic_block.__init__(self,
                                name='frame_sync',
                                in_sig=[np.csingle],
                                out_sig=[np.csingle])
        self.frame_sync = sksdr.FrameSync(preamble, det_thr, frame_size)
        # self.psk = sksdr.PSKModulator(sksdr.QPSK, [0, 1, 3, 2], 1.0, np.pi/4)
        # self.preamble = np.repeat(sksdr.UNIPOLAR_BARKER_SEQ[13], 2)
        # self.mod_preamble = self.psk.modulate(self.preamble)
        # self.phase_off_est = sksdr.PhaseOffsetEst(self.mod_preamble)
        # self.descrambler = sksdr.Descrambler([1, 1, 1, 0, 1], [0, 1, 1, 0])
        # self.fec = sksdr.Hamming(7, 4)
        self.set_output_multiple(self.frame_size)

    def forecast(self, noutput_items, ninput_items_required):
        # setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]
        nin0 = len(in0)
        nout0 = len(out0)
        _log.debug('len in0/out0: %d/%d', nin0, nout0)
        nret = 0
        nin = int(nin0 / self.frame_size) * self.frame_size
        for i in range(0, nin, self.frame_size):
            ret, _, valid = self.frame_sync(in0[i : i + self.frame_size])
            if valid:
                # data = dict()

                # # Phase ambiguity correction
                # data['phase_amb_frame'] = self.phase_off_est(ret)
                # #_log.log(DEBUG-1, ret['phase_amb_frame'])

                # # Demodulate symbols
                # data['rx_sbits'] = self.psk.demodulate(data['phase_amb_frame'])
                # #_log.log(DEBUG-1, ret['rx_sbits'][26:146])

                # # Descramble bits after the preamble
                # data['payload'] = self.descrambler(data['rx_sbits'][len(self.preamble):])
                # #_log.log(DEBUG-1, data['payload'])

                # #  Compute BER
                # # txbits = grsksdr.x2binlist(tx_msg, 8)
                # # rxbits = ret['payload'][:len(tx_msg) * 8]
                # # ret['BER'] = [np.count_nonzero(rxbits != txbits), len(rxbits)]
                # # data['payload'], _ = self.fec.decode(data['payload_fec'])

                # # Convert the payload to ASCII
                # data['rx_msg'] = grsksdr.binlist2x(data['payload'][:15 * 8], 8)
                # data['rx_msg_ascii'] = [chr(x) for x in data['rx_msg']]
                # _log.debug(data['rx_msg_ascii'])

                out0[nret : nret + len(ret)] = ret
                nret += len(ret)
                if nret == nout0:
                    break

        self.consume(0, i + self.frame_size)
        return nret
