import logging
import unittest

import numpy as np
import sksdr

_log = logging.getLogger(__name__)

class TestPSKModulator(unittest.TestCase):
    def setUp(self):
        self.psk = sksdr.QPSKModulator([0, 1, 3, 2], phase_offset=np.pi/4)

    def test_modulation(self):
        bits = np.array([0b00011110, 0b00011110], dtype=np.uint8)
        expected_symbols = 1 / np.sqrt(2) * np.array([1.0 + 1.0j, -1.0 + 1.0j, -1.0 - 1.0j, 1.0 - 1.0j, 1.0 + 1.0j, -1.0 + 1.0j, -1.0 - 1.0j, 1.0 - 1.0j])
        n_symbols = len(bits) * 8 // self.psk._mod.bits_per_symbol
        symbols = np.empty(n_symbols, dtype=complex)
        self.psk.modulate(bits, symbols)
        err_msg = f'expected_symbols = {expected_symbols}\n'
        err_msg += f'symbols = {symbols}\n'
        self.assertTrue(np.allclose(symbols, expected_symbols), err_msg)

    def test_demodulation(self):
        symbols = 1 / np.sqrt(2) * np.array([1.0 + 1.0j, -1.0 + 1.0j, -1.0 - 1.0j, 1.0 - 1.0j, 1.0 + 1.0j, -1.0 + 1.0j, -1.0 - 1.0j, 1.0 - 1.0j])
        expected_bits = np.array([0, 1, 3, 2, 0, 1, 3, 2], dtype=np.uint8)
        bits = np.empty(len(symbols), dtype=np.uint8)
        self.psk.demodulate(symbols, bits)
        err_msg = f'expected_bits = {expected_bits}\n'
        err_msg += f'bits = {bits}\n'
        self.assertTrue(np.alltrue(bits == expected_bits), err_msg)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
