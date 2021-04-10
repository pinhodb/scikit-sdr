"""
Interpolation and decimation algorithms.
"""
import logging
from typing import Tuple

import numpy as np
import scipy.signal as signal

_log = logging.getLogger(__name__)

class FirInterpolator:
    """
    Upsamples and filters the input signal.
    """

    def __init__(self, factor: int, coeffs: list):
        """
        :param factor: Interpolation factor
        :param coeffs: Filter coefficients
        """
        self._factor = factor
        self._coeffs = coeffs
        self._filter_state = np.zeros(len(self.coeffs) - 1)

    @property
    def factor(self) -> int:
        """
        Interpolation factor.
        """
        return self._factor

    @property
    def coeffs(self) -> list:
        """
        Filter coefficients.
        """
        return self._coeffs

    def __call__(self, inp: np.ndarray, filtered: np.ndarray, upsampled: np.ndarray = None) -> int:
        """
        The main work function.

        :param inp: Input signal
        :param filtered: Filtered signal
        :param upsampled: Upsampled signal
        :return: 0 if OK, error code otherwise
        """
        if upsampled is None:
            upsampled = np.empty(len(inp) * self.factor, dtype=complex)
        upsample(inp, self.factor, upsampled)
        filtered[:], self._filter_state = signal.lfilter(self.coeffs, 1, upsampled, zi=self._filter_state)
        return 0

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties
        """
        args = 'factor={}, coeffs={}'.format(self.factor, self.coeffs)
        return '{}({})'.format(self.__class__.__name__, args)

class FirDecimator:
    """
    Filters and downsamples the input signal.
    """

    def __init__(self, factor: int, coeffs: list):
        """
        :param factor: Decimation factor
        :param coeffs: Filter coefficients
        """
        self._factor = factor
        self._coeffs = coeffs
        self._filter_state = np.zeros(len(self.coeffs) - 1)

    @property
    def factor(self) -> int:
        """
        decimation factor.
        """
        return self._factor

    @property
    def coeffs(self) -> list:
        """
        Filter coefficients.
        """
        return self._coeffs

    def __call__(self, inp: np.ndarray, downsampled: np.ndarray, filtered: np.ndarray = None) -> int:
        """
        The main work function.

        :param inp: Input signal
        :param downsampled: Upsampled signal
        :param filtered: Filtered signal
        :return: 0 if OK, error code otherwise
        """
        if filtered is None:
            filtered = np.empty(len(inp), dtype=complex)
        filtered[:], self._filter_state = signal.lfilter(self.coeffs, 1, inp, zi=self._filter_state)
        downsample(filtered, self.factor, downsampled)
        return 0

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties
        """
        args = 'factor={}, coeffs={}'.format(self.factor, self.coeffs)
        return '{}({})'.format(self.__class__.__name__, args)

def upsample(inp: np.ndarray, factor: int, out: np.ndarray):
    """
    Upsamples an input signal.

    :param inp: Input signal
    :param factor: Upsampling factor
    :param out: Upsampled output signal
    """
    out[::factor] = inp
    zero_array = np.zeros(len(inp), dtype=complex)
    for i in range(1, factor):
        out[i::factor] = zero_array

def downsample(inp: np.ndarray, factor: int, out: np.ndarray):
    """
    Downsamples an input signal.

    :param inp: Input signal
    :param factor: Downsampling factor
    :param out: Downsampled output signal
    """
    out[:] = inp[::factor]
