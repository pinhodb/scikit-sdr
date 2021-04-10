"""
Pulses.
"""
import logging

import numpy as np

_log = logging.getLogger(__name__)

def rrc(sps: int, rolloff: float, span: int) -> np.ndarray:
    """
    Returns the root raised cosine filter coefficients.

    :param sps: Samples per symbol
    :param rolloff: Rolloff factor
    :param span: Span (symbols)
    :return: Coefficients of the filter
    """
    # Design the filter
    n = np.arange(-span * sps / 2, span * sps / 2 + 1)
    b = np.zeros(len(n))
    sps *= 1.0
    a = rolloff
    for i, v in enumerate(n):
        if abs(1 - 16 * a**2 * (v / sps)**2) <= np.finfo(np.float).eps / 2:
            b[i] = 1 / 2.0 * ((1 + a) * np.sin((1 + a) * np.pi / (4.0 * a)) - (1 - a) * np.cos((1 - a) * np.pi / (4.0 * a)) + (4 * a) / np.pi * np.sin((1 - a) * np.pi / (4.0 * a)))
        else:
            b[i] = 4 * a / (np.pi * (1 - 16 * a**2 * (v / sps)**2))
            b[i] = b[i] * (np.cos((1 + a) * np.pi * v / sps) + np.sinc((1 - a) * v / sps) * (1 - a) * np.pi / (4.0 * a))

    # Make it a unit energy pulse
    energy = np.sum(b**2)
    return b / np.sqrt(energy)

class RRCPulse:
    """
    A class to encapsulate :func:`rrc`.
    """

    def __init__(self, sps: int, rolloff: float, span:int):
        """
        :param sps: Samples per symbol
        :param rolloff: Rolloff factor
        :param span: Span (symbols)
        """
        self.sps = sps
        self.rolloff = rolloff
        self.span = span

    def __call__(self) -> np.ndarray:
        """
        The main work function.

        :return: Coefficients of the filter
        """
        return rrc(self.sps, self. rolloff, self.span)

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties
        """
        args = 'sps={}, rolloff={}, span={}'.format(self.sps, self.rolloff, self.span)
        return '{}({})'.format(self.__class__.__name__, args)
