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

    def __call__(self, inp: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        The main work function.

        :param inp: Input samples
        :return: Upsampled samples, filtered samples
        """
        upsampled = upsample(inp, self.factor)
        filtered, self._filter_state = signal.lfilter(self.coeffs, 1, upsampled, zi=self._filter_state)
        return upsampled, filtered

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

    def __call__(self, inp: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        The main work function.

        :param inp: Input samples
        :return: Upsampled samples, filtered samples
        """
        filtered, self._filter_state = signal.lfilter(self.coeffs, 1, inp, zi=self._filter_state)
        downsampled = downsample(filtered, self.factor)
        return filtered, downsampled

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and it's properties.
        """
        args = 'factor={}, coeffs={}'.format(self.factor, self.coeffs)
        return '{}({})'.format(self.__class__.__name__, args)

def upsample(inp, factor: int):
    out = np.empty(len(inp) * factor, dtype=complex)
    out[::factor] = inp
    zero_array = np.zeros(len(inp), dtype=complex)
    for i in range(1, factor):
        out[i::factor] = zero_array
    return out

def downsample(inp, factor: int):
    return inp[::factor]
