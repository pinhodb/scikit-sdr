import logging
from typing import Tuple

import numpy as np

_log = logging.getLogger(__name__)

class Hamming:
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
        self.ntotal = ntotal
        self.ndata = ndata

    def encode(self, inp: np.ndarray) -> np.ndarray: # TODO hardcoded for 7,4 rate
        out = np.empty(int(len(inp) * 7 / 4), dtype=int)
        for i, j in zip(range(0, len(inp), 4), range(0, len(out), 7)):
            out[j : j + 7] = inp[i : i + 4] @ self.G % 2
        return out

    def decode(self, inp: np.ndarray) -> Tuple[np.ndarray, np.ndarray]: # TODO hardcoded for 7,4 rate
        out = np.empty(int(len(inp) * 4 / 7), dtype=int)
        flipped = np.zeros(int(len(inp) * 4 / 7), dtype=int)
        for i, j in zip(range(0, len(inp), 7), range(0, len(out), 4)):
            out[j : j + 4] = inp[i + 3 : i + 7]
            syndrome = self.H @ inp[i : i + 7] % 2
            if not np.all(syndrome == 0):
                for k in range(7):
                    if np.all(syndrome == self.H[:, k]):
                        flipped[i + k] = 1
                        if k >= 3:
                            out[j + k - 3] ^= 1
                        break
        return out, flipped
