import logging

import matplotlib.pyplot as plt
import numpy as np
import sksdr
from sksdr.utils import Endian

_log = logging.getLogger(__name__)

def test_costas_loop():

    loop_bw = 2 * np.pi / 100
    costas = sksdr.CostasLoop(loop_bw)

     # Create a delay offset object
    vfd = sksdr.VariableFractionalDelay(max_delay=5)

    # Generate random data symbols and apply BPSK modulation
    ints = np.random.randint(0, 2, 1000)
    bits = np.zeros(len(ints) * 8, dtype=np.uint8)
    unpack = sksdr.Unpack(8, 1, Endian.MSB)
    unpack(ints, bits)
    psk = sksdr.BPSKModulator([0, 1], 1.0)
    n_symbols = len(bits) // psk._mod.bits_per_symbol
    mod_sig = np.empty(n_symbols, dtype=complex)
    psk.modulate(bits, mod_sig)

    # Interpolate by 4 and filter with RRC tx filter
    interp = sksdr.FirInterpolator(4, sksdr.rrc(4, 0.5, 10))
    tx_sig = np.empty(len(mod_sig) * 4, dtype=complex)
    interp(mod_sig, tx_sig)

    n = np.arange(0, 4000)
    Fs = 8e3
    F0 = 2e3
    phase_offset = np.pi / 2
    tx_carrier = np.exp(1j * (2 * np.pi * n * F0 / Fs + phase_offset))
    rx_carrier = np.exp(-1j * 2 * np.pi * n * F0 / Fs)

    rx_sig = tx_sig * tx_carrier * rx_carrier

    # Apply a delay offset
    #out_frame = vfd(tx_sig, 2)
    out_sig = np.zeros_like(rx_sig)
    err_sig = np.zeros_like(rx_sig)
    filter_out = np.zeros_like(rx_sig)
    costas(rx_sig, out_sig, err_sig, filter_out)

    plt.plot(tx_sig.real)
    plt.plot(out_sig.real)
    plt.grid()
    plt.show()

    #assert np.allclose(out_sig, expected_frame)
