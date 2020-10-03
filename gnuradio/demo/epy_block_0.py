"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""
import logging
from logging import DEBUG

import numpy as np

import sksdr
from gnuradio import gr

_log = logging.getLogger(__name__)
#_log.setLevel(logging.DEBUG)

class blk(gr.basic_block):
    """
    """
    def __init__(self, txt_size=11, payload_size=224):
        self.payload_size = payload_size
        self.txt_size = txt_size
        self.counter = 0
        gr.basic_block.__init__(self,
                               name='build_frame',
                               in_sig=[(np.uint8)],
                               out_sig=[(np.uint8)])
        self.set_output_multiple(self.payload_size)

    def forecast(self, noutput_items, ninput_items_required):
        # setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        # print('len(in0), len(out): {}, {}'.format(len(in0), len(out)))
        for xstart, ystart in zip(range(0, len(in0), self.txt_size), range(0, len(out), self.payload_size)):
            xend = xstart + self.txt_size
            bin_txt = sksdr.x2binlist(in0[xstart:xend], 8)
            yend = ystart + len(bin_txt)
            out[ystart:yend] = bin_txt
            bin_counter = sksdr.x2binlist(' {:03d}'.format(self.counter % 100), 8)
            y = yend
            yend = y + len(bin_counter)
            out[y:yend] = bin_counter
            fill = np.random.randint(0, 1, self.payload_size - (yend - ystart))
            y = yend
            yend = y + len(fill)
            out[y:yend] = fill
            # print('ystart, yend: {}, {}'.format(ystart, yend))
            # print('out[ystart:yend]: {}'.format(out[ystart:yend]))
            self.counter += 1
        # print('xend, yend: {}, {}'.format(xend, yend))
        self.consume(0, xend)
        return yend

