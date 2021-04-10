"""
Scrambling/Descrambling algorithms.

Scrambling is necessary to ensure a signal doesn't contain long sequences of 0's or 1's, which can reduce the performance of various blocks, such as symbol synchronizers.
"""
import logging
from collections import deque

import numpy as np

_log = logging.getLogger(__name__)

class Scrambler:
    """
    Scrambler using LFSR.

    At each time step, the input causes the contents of the registers to shift sequentially. Notice that the output for a particular sample depends only on the :math:`M` previous samples (except for the first :math:`M` samples which depend on the initial conditions), where :math:`M` is the size of the LFSR.
    """

    def __init__(self, poly: list, init_state: list, N: int = 256):
        """
        :param poly: Polynomial that defines the connections to the LFSR
        :param init_state: Initial state of the LFSR
        :param N: Number base for computation. Input elements must be integers from 0 to :math:`N-1`. Default is :math:`2^8`, since the input samples are typically octets.
        """
        self._poly = poly
        self._init_state = init_state
        self._N = N
        self._state = deque(self.init_state, maxlen=len(self.init_state))

    @property
    def poly(self) -> list:
        """
        Polynomial that defines the connections to the LFSR.
        """
        return self._poly

    @property
    def init_state(self) -> list:
        """
        Initial state of the LFSR.
        """
        return self._init_state

    @property
    def N(self) -> int:
        """
        Number base for computation. Input elements must be integers from 0 to :math:`N-1`. Default is :math:`2^8`, since the input samples are typically octets.
        """
        return self._N

    def __call__(self, inp: np.ndarray, out: np.ndarray) -> int:
        """
        The main work function.

        :param inp: Input samples
        :param out: Scrambled output samples
        :return: 0 if OK, error code otherwise
        """
        for i, b in enumerate(inp):
            for j in range(1, len(self.poly)):
                if self.poly[j] != 0:
                    # to work with modulo-N, use this instead of XOR
                    b = (b + self._state[j-1]) % self.N
            out[i] = b
            self._state.appendleft(b)
        return 0

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties
        """
        args = 'poly={}, init_state={}, N={}'.format(self.poly, self.init_state, self.N)
        return '{}({})'.format(self.__class__.__name__, args)


class Descrambler:
    """
    Descrambler using LFSR.
    """

    def __init__(self, poly: list, init_state: list, N: int = 256):
        """
        :param poly: Polynomial that defines the connections to the LFSR
        :param init_state: Initial state of the LFSR
        :param N: Number base for computation. Input samples must be integers from 0 to :math:`N-1`. Default is :math:`2^8`, since the input samples are typically octets.
        """
        self._poly = poly
        self._init_state = init_state
        self._N = N
        self._state = deque(self.init_state, maxlen=len(self.init_state))

    @property
    def poly(self) -> list:
        """
        Polynomial that defines the connections to the LFSR.
        """
        return self._poly

    @property
    def init_state(self) -> list:
        """
        Initial state of the LFSR.
        """
        return self._init_state

    @property
    def N(self) -> int:
        """
        Number base for computation. Input samples must be integers from 0 to :math:`N-1`. Default is :math:`2^8`, since the input samples are typically octets.
        """
        return self._N

    def __call__(self, data: np.ndarray, data_out: np.ndarray) -> int:
        """
        The main work function.

        :param inp: Input samples
        :param out: Descrambled output samples
        :return: 0 if OK, error code otherwise
        """
        for i, b in enumerate(data):
            for j in range(1, len(self.poly)):
                if self.poly[j] != 0:
                    # to work with modulo-N, use this instead of XOR
                    b = (b - self._state[j-1]) % self.N
            data_out[i] = b
            self._state.appendleft(data[i])
        return 0

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties
        """
        args = 'poly={}, init_state={}, N={}'.format(self.poly, self.init_state, self.N)
        return '{}({})'.format(self.__class__.__name__, args)
