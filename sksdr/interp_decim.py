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
        self.factor = factor
        self.coeffs = coeffs
        self._filter_state = np.zeros(len(self.coeffs) - 1)

    def __call__(self, inp: np.ndarray, filtered: np.ndarray, upsampled: np.ndarray = None) -> int:
        """
        The main work function.

        :param inp: Input samples
        :param filtered: Filtered samples
        :param upsampled: Upsampled samples
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

        :return: A string representing the object and it's properties.
        """
        args = 'factor={}, coeffs={}'.format(self.factor, self.coeffs)
        return '{}({})'.format(self.__class__.__name__, args)

class FirDecimator:
    """
    Filters and downsamples the input signal.
    """
    def __init__(self, factor: int, coeffs: list):
        """
        :param factor: Interpolation factor
        :param coeffs: Filter coefficients
        """
        self.factor = factor
        self.coeffs = coeffs
        self._filter_state = np.zeros(len(self.coeffs) - 1)

    def __call__(self, inp: np.ndarray, downsampled: np.ndarray, filtered: np.ndarray = None) -> int:
        """
        The main work function.

        :param inp: Input samples
        :param downsampled: Upsampled samples
        :param filtered: Filtered samples
        :return: 0 if OK, error code otherwise
        """
        if downsampled is None:
            downsampled = np.empty(len(inp) // self.factor, dtype=complex)
        filtered[:], self._filter_state = signal.lfilter(self.coeffs, 1, inp, zi=self._filter_state)
        downsample(filtered, self.factor, downsampled)
        return 0

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and it's properties.
        """
        args = 'factor={}, coeffs={}'.format(self.factor, self.coeffs)
        return '{}({})'.format(self.__class__.__name__, args)

def upsample(inp: np.ndarray, factor: int, out: np.ndarray):
    out[::factor] = inp
    zero_array = np.zeros(len(inp), dtype=complex)
    for i in range(1, factor):
        out[i::factor] = zero_array

def downsample(inp: np.ndarray, factor: int, out: np.ndarray):
    out[:] = inp[::factor]
