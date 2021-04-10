"""
FEC algorithms.
"""
import logging

import numpy as np

from sksdr.utils import Endian, Pack, Unpack

_log = logging.getLogger(__name__)

class Hamming74:
    """
    Hamming(7,4) encoder/decoder.

    Hamming's (7,4) algorithm can correct any single-bit error, or detect all single-bit and two-bit errors.

    E.g., encode the data value 1010 using the Hamming code defined by the matrix :attr:`G`:

    TODO redo in Latex
    |1 0 1 0| |0 1 1 1 0 0 0|
              |1 0 1 0 1 0 0| = |1 0 1 1 0 1 0|
              |1 1 0 0 0 1 0|    | | | | | | |
              |1 1 1 0 0 0 1|    | | | | | | +-->(1 × 0) + (0 × 0) + (1 × 0) + (0 × 1)
                                 | | | | | +---->(1 × 0) + (0 × 0) + (1 × 1) + (0 × 0)
                                 | | | | +------>(1 × 0) + (0 × 1) + (1 × 0) + (0 × 0)
                                 | | | +-------->(1 × 1) + (0 × 0) + (1 × 0) + (0 × 0)
                                 | | +---------->(1 × 1) + (0 × 1) + (1 × 0) + (0 × 1)
                                 | +------------>(1 × 1) + (0 × 0) + (1 × 1) + (0 × 1)
                                 +-------------->(1 × 0) + (0 × 1) + (1 × 1) + (0 × 1)
    """

    def __init__(self):
        self._unpack = Unpack(8, 1, Endian.MSB)
        self._pack = Pack(1, 7, Endian.MSB)

#                  p  p  p  d  d  d  d
#                  1, 2, 3, 1, 2, 3, 4
    _G = np.array([[0, 1, 1, 1, 0, 0, 0],
                  [1, 0, 1, 0, 1, 0, 0],
                  [1, 1, 0, 0, 0, 1, 0],
                  [1, 1, 1, 0, 0, 0, 1]])
    """
    Generator matrix.
    """

    _H = np.array([[1, 0, 0, 0, 1, 1, 1],
                  [0, 1, 0, 1, 0, 1, 1],
                  [0, 0, 1, 1, 1, 0, 1]])
    """
    Parity-check matrix.
    """

    def encode(self, inp: np.ndarray, out: np.ndarray) -> int:
        """
        Encodes a sequence of octets.

        Each octet in ``inp`` will be split in two 4-bit values and encoded into two 7-lsb octets in ``out`` (4-msb first).

        :param inp: Input samples. This should be an array of octets.
        :param out: Output samples. This should be an array of octets with twice the size of ``inp``.
        :return: 0 if OK, error code otherwise
        """
        tmp = np.empty(8, dtype=np.uint8)
        for i, j in zip(range(len(inp)), range(0, len(out), 2)):
            self._unpack(inp[i], tmp)
            out[j] = self._pack(tmp[:4] @ self._G % 2)

            out[j + 1] = self._pack(tmp[4:] @ self._G % 2)

    def decode(self, inp: np.ndarray, out:np.ndarray, corrected:np.ndarray) -> int:
        """
        Decodes a sequence of octets.

        Each 7-lsb octet in ``inp`` will be decoded into a 4-lsb octet in ``out``.

        :param inp: Input samples
        :param out: Output samples
        :param corrected: Index of the corrected bit, if any
        :return: 0 if OK, error code otherwise
        """
        tmp = np.zeros(8, dtype=np.uint8)
        for i in range(len(out)):
            out[i] = inp[i] & 0xf
            self._unpack(inp[i], tmp)
            syndrome = (self._H @ tmp[1:]) % 2
            if not np.all(syndrome == 0):
                for k in range(7):
                    if np.all(syndrome == self._H[:, k]):
                        corrected[i] = 7 - k - 1
                        if k >= 3:
                            out[i] ^= (1 << (7 - k - 1))
                        break
        return 0
