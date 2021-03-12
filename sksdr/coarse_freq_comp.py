"""
Coarse frequency compensation algorithms.
"""
import logging
from typing import Tuple

import numpy as np
from numpy.fft import fft, fftshift

_log = logging.getLogger(__name__)

class CoarseFrequencyComp:
    r"""
    Open loop frequency correction on a PSK input signal.

    The algorithm estimates the frequency error :math:`\Delta\hat{f}` by using a periodogram of the :math:`m`\ :sup:`th`\  power of the received signal (the :math:`m`\ :sup:`th`\  power is used since it removes the :math:`m`\ :sup:`th`\  order PSK modulation, leaving only the carrier at a frequency :math:`m` times its original frequency):

    TODO equation

    where :math:`f_s` is the sampling frequency (specified by :attr:`sample_rate`), :math:`m` is the modulation order (specified by :attr:`mod_order`), :math:`r(n)` is the received sequence, and :math:`N` is the number of samples of the periodogram. To avoid aliasing :math:`\Delta\hat{f}` must be restricted to :math:`\left[\frac{-R_{sym}}{2}, \frac{R_{sym}}{2}\right]`, where :math:`R_{sym}=\frac{R_b}{log_2(m)}`, with :math:`R_b` representing the bit rate.

    The algorithm effectively searches for a frequency that maximizes the time average of the :math:`m`\ :sup:`th`\  power of the received signal multiplied by frequencies in the range of :math:`\left[\frac{-R_{sym}}{2}, \frac{R_{sym}}{2}\right]`. As the form of the algorithm is the definition of the DFT of :math:`r^{m}(n)`, searching for a frequency that maximizes the time average is equivalent to searching for a peak line in the spectrum of :math:`r^{m}(n)`. The number of points required by the FFT is

    TODO equation

    where :math:`f_r` is the desired frequency resolution, specified by :attr:`freq_res`. Note that :math:`log_2\left(\frac{f_s}{f_r}\right)` should be rounded up, since it might not be integer.
    """

    def __init__(self, mod_order: int, sample_rate: float, freq_res: float):
        """
        :param mod_order: Modulation order (e.g., 2 for BPSK, 4 for QPSK)
        :param sample_rate: Input signal sampling rate (Hz)
        :param freq_res: Desired frequency resolution (Hz)
        """
        self._mod_order = mod_order
        self._sample_rate = sample_rate
        self._freq_res = freq_res
        self._fft_size = int(2**np.ceil(np.log2(self._sample_rate / self._freq_res)))
        self._buf = np.zeros(self._fft_size, dtype=complex)
        self._sum_phase = 0.0

    def __call__(self, inp: np.ndarray, out: np.ndarray, shifted_fft: np.ndarray = None, freq_offset: np.ndarray = None) -> int:
        """
        The main work function.

        :param inp: Input signal
        :param out: Output signal
        :param shifted_fft: PSD of input signal
        :param freq_offset: Frequency offset of input signal
        :return: 0 if OK, error code otherwise
        """
        if len(inp) > self._fft_size:
            # TODO Implement average fft
            raise NotImplementedError('Average FFT not implemented')

        time_steps = np.arange(0, len(inp) + 1)
        raised = inp**self._mod_order
        buf = np.hstack((self._buf[len(raised):], raised))
        self._buf = buf

        abs_fft = abs(fft(buf, self._fft_size))
        shift_fft = fftshift(abs_fft)
        if shifted_fft is not None:
            shifted_fft[:] = shift_fft
        max_idx = np.argmax(shift_fft)
        offset_idx = max_idx - self._fft_size / 2
        df = self._sample_rate / self._fft_size
        freq_off  = df * (offset_idx) / self._mod_order
        # FIXME unnecessary copy
        if freq_offset is not None:
            freq_offset[:] = freq_off
        phase = freq_off * time_steps / self._sample_rate

        # Frequency correction
        out[:] = inp * np.exp(1j * 2 * np.pi * (self._sum_phase - phase[:-1]))
        self._sum_phase -= phase[-1]
        return 0

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties.
        """
        args = 'mod_order={}, sample_rate={}, freq_res={}'.format(self._mod_order, self._sample_rate, self._freq_res)
        return '{}({})'.format(self.__class__.__name__, args)
