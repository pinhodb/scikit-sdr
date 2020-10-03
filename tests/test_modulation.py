import logging
import unittest

import numpy as np

import sksdr

_log = logging.getLogger(__name__)

class TestPSKModulator(unittest.TestCase):
    def setUp(self):
        self.mod = sksdr.QPSK
        self.psk = sksdr.PSKModulator(self.mod, [0, 1, 3, 2], phase_offset=np.pi/4)

    def test_modulation(self):
        bits = np.array([0, 0, 0, 1, 1, 1, 1, 0])
        expected_symbols = 1 / np.sqrt(2) * np.array([1.0 + 1.0j, -1.0 + 1.0j, -1.0 - 1.0j, 1.0 - 1.0j])
        symbols = self.psk.modulate(bits)
        err_msg = f'expected_symbols = {expected_symbols}\n'
        err_msg += f'symbols = {symbols}\n'
        self.assertTrue(np.allclose(symbols, expected_symbols), err_msg)

    def test_demodulation(self):
        symbols = 1 / np.sqrt(2) * np.array([1.0 + 1.0j, -1.0 + 1.0j, -1.0 - 1.0j, 1.0 - 1.0j])
        expected_bits = np.array([0, 0, 0, 1, 1, 1, 1, 0])
        bits = self.psk.demodulate(symbols)
        err_msg = f'expected_bits = {expected_bits}\n'
        err_msg += f'bits = {bits}\n'
        self.assertTrue(np.alltrue(bits == expected_bits), err_msg)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
