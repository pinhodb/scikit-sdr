"""
Frame synchronization algorithms.
"""
import logging
from typing import Tuple

import numpy as np
import scipy.signal as signal

_log = logging.getLogger(__name__)

class PreambleSync:
    """
    Frame synchronization by correlation with a preamble.

    Performs a correlation with a known preamble to detect the beginning of a frame.
    """
    def __init__(self, preamble: np.ndarray, threshold: float, frame_size: int):
        self.preamble = np.flipud(np.conj(preamble))
        self.threshold = threshold
        self.frame_size = frame_size
        self._filter_state = np.zeros(len(self.preamble) - 1)
        self._buf = np.empty(0)
        self._xcorr = np.empty(0)

    def __call__(self, inp: np.ndarray, out: np.ndarray) -> int:
        """
        The main work function.

        :param inp: Input signal
        :param out: Output signal
        :return: 0 if OK, error code otherwise
        """
        # Correlate with preamble
        xcorr, self._filter_state = signal.lfilter(self.preamble, 1, inp, zi=self._filter_state)
        if np.any(np.iscomplex(inp)) or np.any(np.iscomplex(self.preamble)):
            xcorr = np.abs(xcorr)

        self._buf = np.hstack((self._buf, inp))
        self._xcorr = np.hstack((self._xcorr, xcorr))

        # Find indexes that exceed the threshold
        idxs = np.where(self._xcorr >= self.threshold)[0]

        if len(idxs) == 0:
            return False

        # Find the best index
        best_idx = idxs[0]
        for idx in idxs[1:]:
            if idx - idxs[0] < (self.frame_size / 2) and self._xcorr[idx] > self._xcorr[best_idx]:
                best_idx = idx

        frame_start = best_idx - len(self.preamble) + 1
        frame_end = frame_start + self.frame_size

        if frame_start < 0:
            self._buf = self._buf[best_idx + 1:]
            self._xcorr = self._xcorr[best_idx + 1:]
            return False
        elif frame_end > len(self._buf):
            self._buf = self._buf[frame_start:]
            self._xcorr = self._xcorr[frame_start:]
            return False
        else:
            out[:] = self._buf[frame_start:frame_end]
            self._buf = self._buf[frame_end:]
            self._xcorr = self._xcorr[frame_end:]
            return True

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties.
        """
        args = 'preamble={}, threshold={}, frame_size={}'.format(self.preamble, self.threshold, self.frame_size)
        return '{}({})'.format(self.__class__.__name__, args)
