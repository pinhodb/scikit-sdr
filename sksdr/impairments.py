"""
Channel impairments.
"""
import logging
from collections import deque
from typing import Tuple

import numpy as np

_log = logging.getLogger(__name__)

class PhaseFrequencyOffset:
    """
    Applies phase and frequency offsets to an incoming signal.
    """
    def __init__(self, sample_rate: float, freq_offset: float = 0, phase_offset: float = 0):
        """
        :para sample_rate: Input signal sample rate (Hz)
        :param freq_offset: Desired frequency offset (Hz)
        :param phase_offset: Desired phase offset (degrees)
        """
        self.sample_rate = sample_rate
        self.freq_offset = freq_offset
        self.phase_offset = np.deg2rad(phase_offset)
        self._sum_phase = 0.0

    def __call__(self, inp: np.ndarray, out: np.ndarray) -> int:
        """
        The main work function.

        :param inp: Input samples
        :param out: Output samples
        :return: 0 if OK, error code otherwise
        """
        time_steps = np.arange(0, len(inp) + 1)
        phase = self.freq_offset * time_steps / self.sample_rate

        # Apply frequency and phase offset
        out[:] = inp * np.exp(1j * 2 * np.pi * (self._sum_phase + phase[:-1] + self.phase_offset))
        self._sum_phase += phase[-1]
        return out, phase

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties.
        """
        args = 'sample_rate={}, freq_offset={}, phase_offset={}'.format(self.sample_rate, self.freq_offset,
                                                                        self.phase_offset)
        return '{}({})'.format(self.__class__.__name__, args)

class VariableFractionalDelay:
    """
    Delays the input signal by a specified (and potentially fractional) number of samples.

    The algorithm interpolates the input signal to obtain new samples at non-integer sampling intervals. The only available interpolation method currently is *linear* interpolation. The delay can vary with each invocation of the module (specified by the :attr:`delay` argument in the :func:`__call__` function). This allows to create a delay profile say, for example, in a triangle or sawtooth shape. The maximum value of the delay is specified using :attr:max_delay. Delay values greater than the maximum are clipped to the maximum.

    The object contains a circular buffer of size :math:`max_delay+1` that holds the previous samples, from which it can then compute the interpolation, to obtain the output sequence.
    """
    def __init__(self, max_delay: float, init_state: int = 0):
        """
        :param max_delay: Maximum delay (samples)
        :param init_state: Initial value to fill in the circular buffer that holds the samples (default=0).
        """
        self.max_delay = max_delay
        self.init_state = init_state
        self._buf = deque([self.init_state] * (self.max_delay + 1), maxlen=self.max_delay + 1)

    def __call__(self, inp: np.ndarray, delay: float, out: np.ndarray) -> int:
        """
        The main work function.

        :param inp: Input samples
        :param delay: The delay to apply
        :param out: Output samples
        :return: 0 if OK, error code otherwise
        """
        int_part = int(np.floor(delay))
        frac_part = delay - int_part
        for i in range(len(inp)):
            self._buf.append(inp[i])
            idx = max(-int_part - 2, -len(self._buf))
            out[i] = self._buf[idx] * frac_part + self._buf[idx + 1] * (1 - frac_part)

        return out

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties.
        """
        args = 'max_delay={}, init_state={}'.format(self.max_delay, self.init_state)
        return '{}({})'.format(self.__class__.__name__, args)
