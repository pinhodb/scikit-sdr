"""
Forward error correction (FEC) algorithms.
"""
import logging
from typing import Tuple

import numpy as np

_log = logging.getLogger(__name__)

class Hamming:
    """
    Hamming(7,4) encoder/decoder.
    """
#                  p  p  p  d  d  d  d
#                  1, 2, 3, 1, 2, 3, 4
    G = np.array([[0, 1, 1, 1, 0, 0, 0],
                  [1, 0, 1, 0, 1, 0, 0],
                  [1, 1, 0, 0, 0, 1, 0],
                  [1, 1, 1, 0, 0, 0, 1]])

    H = np.array([[1, 0, 0, 0, 1, 1, 1],
                  [0, 1, 0, 1, 0, 1, 1],
                  [0, 0, 1, 1, 1, 0, 1]])

# Encode the data value 1010 using the Hamming code defined by the matrix G (above)
# |1 0 1 0| |0 1 1 1 0 0 0|
#           |1 0 1 0 1 0 0| = |1 0 1 1 0 1 0|
#           |1 1 0 0 0 1 0|    | | | | | | |
#           |1 1 1 0 0 0 1|    | | | | | | +-->(1 × 0) + (0 × 0) + (1 × 0) + (0 × 1)
#                              | | | | | +---->(1 × 0) + (0 × 0) + (1 × 1) + (0 × 0)
#                              | | | | +------>(1 × 0) + (0 × 1) + (1 × 0) + (0 × 0)
#                              | | | +-------->(1 × 1) + (0 × 0) + (1 × 0) + (0 × 0)
#                              | | +---------->(1 × 1) + (0 × 1) + (1 × 0) + (0 × 1)
#                              | +------------>(1 × 1) + (0 × 0) + (1 × 1) + (0 × 1)
#                              +-------------->(1 × 0) + (0 × 1) + (1 × 1) + (0 × 1)

    def __init__(self, ntotal: int, ndata: int):
        """
        :param ntotal: Total number of bits
        :param ndata: Number of data bits
        """
        self.ntotal = ntotal
        self.ndata = ndata

    def encode(self, inp: np.ndarray, out: np.ndarray) -> int:
        """
        Encodes a sequence of data bits.
        TODO hardcoded for 7,4 rate

        :param inp: Input samples
        :param out: Output samples
        :return: 0 if OK, or error code otherwise
        """
        for i, j in zip(range(0, len(inp), 4), range(0, len(out), 7)):
            out[j : j + 7] = inp[i : i + 4] @ self.G % 2
        return out

    def decode(self, inp: np.ndarray, out:np.ndarray, corrected:np.ndarray) -> int:
        """
        Decodes a sequence of data bits.
        TODO hardcoded for 7,4 rate

        :param inp: Input samples
        :param out: Output samples
        :param corrected: Corrected samples
        :return: 0 if OK, or error code otherwise
        """

        for i, j in zip(range(0, len(inp), 7), range(0, len(out), 4)):
            out[j : j + 4] = inp[i + 3 : i + 7]
            syndrome = self.H @ inp[i : i + 7] % 2
            if not np.all(syndrome == 0):
                for k in range(7):
                    if np.all(syndrome == self.H[:, k]):
                        corrected[i + k] = 1
                        if k >= 3:
                            out[j + k - 3] ^= 1
                        break
        return 0
