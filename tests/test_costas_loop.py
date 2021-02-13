import logging

import numpy as np
import sksdr

_log = logging.getLogger(__name__)

def test_costas_loop():
    loop_bw = 2 * np.pi / 100
    costas = sksdr.CostasLoop(loop_bw)

     # Create a delay offset object
    vfd = sksdr.VariableFractionalDelay(max_delay=5)

    # Generate random data symbols and apply BPSK modulation
    ints = np.random.randint(0, 2, 1000)
    bits = sksdr.x2binlist(ints, 1)
    psk = sksdr.PSKModulator(sksdr.BPSK, [0, 1], 1.0, np.pi/4)
    mod_sig = psk.modulate(bits)

    # Interpolate by 4 and filter with RRC tx filter
    #interp = sksdr.FirInterpolator(4, sksdr.rrc(4, 0.5, 10))
    #_, tx_sig = interp(mod_sig)

    n = np.arange(0, 1000)
    Fs = 8e3
    F0 = 2e3

    #tx_sig = 1500 * np.exp(1j * (2 * np.pi * F0 / Fs * n + np.pi / 3))
    tx_sig = np.repeat(1500 * np.exp(1j * np.pi / 3), 1000)

    # Apply a delay offset
    #out_frame = vfd(tx_sig, 2)
    out_frame = np.zeros_like(tx_sig)
    expected_frame = np.empty_like(tx_sig)
    costas(tx_sig, out_frame)

    import matplotlib.pyplot as plt

    plt.plot(tx_sig.real)
    plt.plot(out_frame.real)
    plt.grid()
    plt.show()

    assert np.allclose(out_frame, expected_frame)
