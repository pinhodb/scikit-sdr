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
    def __init__(self, txt_size=11, payload_size=28):
        self.payload_size = payload_size
        self.txt_size = txt_size
        self.fill_size = self.payload_size - self.txt_size - 4
        self.counter = 0
        gr.basic_block.__init__(self,
                               name='build_frame',
                               in_sig=[(np.uint8)],
                               out_sig=[(np.uint8)])
        self.set_output_multiple(self.payload_size)

    def forecast(self, noutput_items, ninput_items_required):
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        for xstart, ystart in zip(range(0, len(in0), self.txt_size), range(0, len(out), self.payload_size)):
            xend = xstart + self.txt_size
            yend = ystart + self.payload_size
            out[ystart:yend] = np.concatenate((in0[xstart:xend], np.frombuffer(' {:03d}'.format(self.counter % 100).encode(), dtype=np.uint8), np.random.randint(0, 256, self.fill_size)))
            self.counter += 1
        self.consume(0, xend)
        return yend

