import logging

import numpy as np
import sksdr
from sksdr.utils import Endian, Pack, Unpack

_log = logging.getLogger(__name__)

def test_hamming_7_4():
    in_stream = np.array([
        np.uint8(0b11011001),
        np.uint8(0b00110101),
        np.uint8(0b00111010),
        np.uint8(0b10110010),
        np.uint8(0b00011110),
        np.uint8(0b01011010),
        np.uint8(0b00000100),
        np.uint8(0b00001101),
        np.uint8(0b11011010),
        np.uint8(0b10100010),
        np.uint8(0b10010010),
        np.uint8(0b10101100)])

    expected_stream = np.array([
        np.uint8(0b00011101),
        np.uint8(0b01001001),
        np.uint8(0b00010011),
        np.uint8(0b00100101),
        np.uint8(0b00010011),
        np.uint8(0b01011010),
        np.uint8(0b00101011),
        np.uint8(0b01100010),
        np.uint8(0b01110001),
        np.uint8(0b00001110),
        np.uint8(0b00100101),
        np.uint8(0b01011010),
        np.uint8(0b00000000),
        np.uint8(0b01010100),
        np.uint8(0b00000000),
        np.uint8(0b00011101),
        np.uint8(0b00011101),
        np.uint8(0b01011010),
        np.uint8(0b01011010),
        np.uint8(0b01100010),
        np.uint8(0b01001001),
        np.uint8(0b01100010),
        np.uint8(0b01011010),
        np.uint8(0b01101100)])

    out_stream = np.empty_like(expected_stream)
    ham = sksdr.Hamming74()
    ham.encode(in_stream, out_stream)
    assert np.all(out_stream == expected_stream)

def test_desc_hamming_7_4():
    in_stream = np.array([
        np.uint8(0b00011101),
        np.uint8(0b01001001),
        np.uint8(0b00010011),
        np.uint8(0b00100101),
        np.uint8(0b00010011),
        np.uint8(0b01011010),
        np.uint8(0b00101011),
        np.uint8(0b01100010),
        np.uint8(0b01110001),
        np.uint8(0b00001110),
        np.uint8(0b00100101),
        np.uint8(0b01011010),
        np.uint8(0b00000000),
        np.uint8(0b01010100),
        np.uint8(0b00000000),
        np.uint8(0b00011101),
        np.uint8(0b00011101),
        np.uint8(0b01011010),
        np.uint8(0b01011010),
        np.uint8(0b01100010),
        np.uint8(0b01001001),
        np.uint8(0b01100010),
        np.uint8(0b01011010),
        np.uint8(0b01101100)])

    expected_stream = np.array([
        np.uint8(0b00001101),
        np.uint8(0b00001001),
        np.uint8(0b00000011),
        np.uint8(0b00000101),
        np.uint8(0b00000011),
        np.uint8(0b00001010),
        np.uint8(0b00001011),
        np.uint8(0b00000010),
        np.uint8(0b00000001),
        np.uint8(0b00001110),
        np.uint8(0b00000101),
        np.uint8(0b00001010),
        np.uint8(0b00000000),
        np.uint8(0b00000100),
        np.uint8(0b00000000),
        np.uint8(0b00001101),
        np.uint8(0b00001101),
        np.uint8(0b00001010),
        np.uint8(0b00001010),
        np.uint8(0b00000010),
        np.uint8(0b00001001),
        np.uint8(0b00000010),
        np.uint8(0b00001010),
        np.uint8(0b00001100)])

    # flip some bits
    in_stream[3] ^= 1
    in_stream[10] ^= 1
    fec = sksdr.Hamming74()
    out_stream = np.empty_like(expected_stream, dtype=np.uint8)
    flipped_stream = np.empty_like(expected_stream, dtype=np.int8) * -1
    fec.decode(in_stream, out_stream, flipped_stream)
    assert np.all(out_stream == expected_stream) and np.all(flipped_stream[[3, 10]] == 0)
