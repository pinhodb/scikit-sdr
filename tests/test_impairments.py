import logging

import numpy as np
import sksdr

_log = logging.getLogger(__name__)

def test_fractional_delay0():
    delay = 0.1
    data = np.array([1, 2, 3, 4, 5], dtype=float)
    expected_data = np.array([0.9, 1.9, 2.9, 3.9, 4.9])
    vfd = sksdr.VariableFractionalDelay(10)
    out_data = np.empty_like(data)
    vfd(data, delay, out_data)
    assert np.allclose(out_data, expected_data)

    delay = 10
    data = np.array([1, 2, 3, 4, 5], dtype=float)
    expected_data = np.array([0, 0, 0, 0, 0], dtype=float)
    vfd = sksdr.VariableFractionalDelay(10)
    out_data = np.empty_like(data)
    vfd(data, delay, out_data)
    assert np.allclose(out_data, expected_data)

def test_fractional_delay1():

    # Create a delay offset object
    vfd = sksdr.VariableFractionalDelay(5)

    # Generate random data symbols and apply QPSK modulation
    bits = np.random.randint(0, 4, 10000)
    psk = sksdr.QPSKModulator([0, 1, 3, 2], 1.0, np.pi/4)
    n_symbols = len(bits) * 8 // psk._mod.bits_per_symbol
    mod_sig = np.empty(n_symbols, dtype=complex)
    psk.modulate(bits, mod_sig)

    # Interpolate by 4 and filter with RRC tx filter
    interp = sksdr.FirInterpolator(4, sksdr.rrc(4, 0.5, 10))
    tx_sig = np.empty(len(mod_sig) * 4, dtype=complex)
    interp(mod_sig, tx_sig)

    # Apply the delay offset. Then, pass the offset signal through an AWGN channel.
    out_sig = np.empty_like(tx_sig)
    vfd(tx_sig, 2, out_sig)
    expected_sig = np.concatenate(([0, 0], tx_sig[0:-2]))
    assert np.allclose(out_sig, expected_sig)
