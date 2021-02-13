"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""
import logging

import numpy as np
import sksdr
from gnuradio import gr

_log = logging.getLogger(__name__)
#_log.setLevel(logging.DEBUG)


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, message_size=1, payload_size_bits=1):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        self.message_size = message_size
        self.payload_size_bits = payload_size_bits
        gr.sync_block.__init__(
            self,
            name='decode_frame',   # will show up in GRC
            in_sig=[np.uint8],
            out_sig=[np.uint8]
        )
        self.set_output_multiple(self.payload_size_bits)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        for i in range(0, len(in0), self.payload_size_bits):
            rxbits = in0[i : i + self.message_size * 8]
            rx_msg = sksdr.binlist2x(rxbits, 8)
            rx_msg_ascii = [chr(x) for x in rx_msg]
            print(rx_msg_ascii)

        return len(in0)
