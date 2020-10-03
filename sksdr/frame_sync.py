import logging
from typing import Tuple

import numpy as np
import scipy.signal as signal

_log = logging.getLogger(__name__)

class FrameSync:
    def __init__(self, preamble: np.ndarray, threshold: float, frame_size: int):
        self.preamble = np.flipud(np.conj(preamble))
        self.threshold = threshold
        self.frame_size = frame_size
        self._filter_state = np.zeros(len(self.preamble) - 1)
        self._buf = np.empty(0)
        self._xcorr = np.empty(0)

    def __call__(self, inp: np.ndarray) -> Tuple[np.ndarray, np.ndarray, bool]:

        # Correlate with preamble
        xcorr, self._filter_state = signal.lfilter(self.preamble, 1, inp, zi=self._filter_state)
        if np.any(np.iscomplex(inp)) or np.any(np.iscomplex(self.preamble)):
            xcorr = np.abs(xcorr)

        self._buf = np.hstack((self._buf, inp))
        self._xcorr = np.hstack((self._xcorr, xcorr))

        # Find indexes that exceed the threshold
        idxs = np.where(self._xcorr >= self.threshold)[0]

        if len(idxs) == 0:
            return None, idxs, False

        best_idx = idxs[0]
        for idx in idxs[1:]:
            if idx - idxs[0] < (self.frame_size / 2) and self._xcorr[idx] > self._xcorr[best_idx]:
                best_idx = idx

        frame_start = best_idx - len(self.preamble) + 1
        frame_end = frame_start + self.frame_size

        if frame_start < 0:
            ret = None
            self._buf = self._buf[best_idx + 1:]
            self._xcorr = self._xcorr[best_idx + 1:]
            valid = False
        elif frame_end > len(self._buf):
            ret = None
            self._buf = self._buf[frame_start:]
            self._xcorr = self._xcorr[frame_start:]
            valid = False
        else:
            ret = self._buf[frame_start:frame_end]
            self._buf = self._buf[frame_end:]
            self._xcorr = self._xcorr[frame_end:]
            valid = True

        return ret, idxs, valid

    def __repr__(self):
        args = 'preamble={}, threshold={}, frame_size={}'.format(self.preamble, self.threshold, self.frame_size)
        return '{}({})'.format(self.__class__.__name__, args)
