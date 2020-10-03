import logging

# import matplotlib.pyplot as plt
import numpy as np

import sksdr

_log = logging.getLogger(__name__)

def test_psk_rx_iq():
    valid_frames = 0
    frame_size_samples = 500
    frame_size_symbols = 125
    trans = sksdr.PSKTrans(sample_rate=1.024e6, frame_size=frame_size_symbols, agc_avg_len=frame_size_samples)
    # file obtained from GNU Radio which uses complex64 (float32 +j*float32)
    num_frames = 100
    samples = np.fromfile('tests/test.iq', dtype=np.complex64)[:num_frames * frame_size_samples]
    for i in range(0, len(samples), frame_size_samples):
        rx_ret = trans.receive(samples[i: i + frame_size_samples], 'Hello World 000')
        if rx_ret['valid']:
            valid_frames += 1
    pass
