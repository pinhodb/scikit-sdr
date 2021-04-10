"""
Channel models.
"""
import logging

import numpy as np

_log = logging.getLogger(__name__)

class AWGNChannel:
    """
    AWGN channel model.
    """

    def __init__(self, snr: float = np.inf, signal_power: float = None):
        """
        :param snr: Desired SNR (dB)
        :param signal_power: Desired signal power (linear units), or :obj:`None` if the signal is to be measured on each :meth:`__call__()`
        """
        self.snr = snr
        self.signal_power = signal_power

    @property
    def snr(self) -> float:
        """
        Desired SNR (dB).
        """
        return self._snr

    @snr.setter
    def snr(self, value: float):
        self._snr = value
        self._snr_linear = 10**(self.snr / 10)

    @property
    def signal_power(self) -> float:
        """
        Desired signal power (linear units), or :obj:`None` if the signal is to be measured on each :meth:`__call__()`.
        """
        return self._signal_power

    @signal_power.setter
    def signal_power(self, value: float):
        self._signal_power = value

    def capacity(self) -> float:
        r"""
        Returns the capacity of the channel.

        The capacity is computed using the Shannon–Hartley formula: :math:`C = B\log_{2}\left(1+\frac{P}{N_0 B}\right)`.

        :return: Capacity of the channel
        """
        return 0.5 * np.log1p(self.snr) / np.log(2.0)

    def __call__(self, inp: np.ndarray, out: np.ndarray) -> int:
        """
        The main work function.

        :param inp: Input signal
        :param out: Output signal
        :return: 0 if OK, error code otherwise
        """
        size = len(inp)
        if self.signal_power is None:
            # Measured
            signal_power = np.linalg.norm(inp)**2 / size
        else:
            signal_power = self.signal_power

        noise_power = signal_power / self._snr_linear

        if inp.dtype == np.complex:
            # for some reason random.default_rng().normal() is much faster than random.normal()
            out[:] = inp + np.sqrt(noise_power / 2) * (np.random.default_rng().normal(size=size) + 1j * np.random.default_rng().normal(size=size))
        else:
            out[:] = inp + np.sqrt(noise_power) * np.random.default_rng().normal(size=size)
        return 0

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties
        """
        args = 'snr={}, signal_power={}'.format(self.snr, self.signal_power)
        return '{}({})'.format(self.__class__.__name__, args)
