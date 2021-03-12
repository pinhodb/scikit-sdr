"""
Digital modulation schemes.
"""
import logging

import numpy as np

from .utils import x2binlist

_log = logging.getLogger(__name__)

class Modulation:
    """
    Represents a modulation type, such as BPSK or QPSK.
    """
    def __init__(self, name: str, order: int):
        """
        :param name: The modulation name
        :param order: The order of the modulation. This determines the bits per symbol.
        """
        self.name = name
        self.order = order

    @property
    def order(self) -> int:
        """
        Returns the order of the modulation.
        """
        return self._order

    @order.setter
    def order(self, value: int):
        self._order = value
        self.bits_per_symbol = int(np.log2(self.order))

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties.
        """
        args = 'name={}, order={}, bits_per_symbol={}'.format(self.name, self.order, self.bits_per_symbol)
        return '{}({})'.format(self.__class__.__name__, args)

BPSK = Modulation('BPSK', 2)
"""
BPSK modulation
"""

QPSK = Modulation('QPSK', 4)
"""
QPSK modulation
"""

modulations = (
    BPSK,
    QPSK
)
"""
A tuple of the existing modulations.
"""

class PSKModulator:
    """
    Modulates a stream of bits into complex symbols and vice-versa.

    Supports BPSK and QPSK modulation schemes. :attr:`labels` specifies the mapping between bits and symbols (the class uses :math:`m` LSB bits from each of the list elements, where :math:`m` is the modulation order). :attr:`amplitude` specifies the absolute value of the symbols (i.e., its L2-norm). :attr:`phase_offset` is the offset of the first symbol in the complex plane. Only ‘hard’ demodulation is supported at the moment (i.e., the module chooses the constellation point closest to the symbol).
    """
    def __init__(self, mod: Modulation, labels: list, amplitude: float = 1.0, phase_offset: float = 0.0):
        """
        :param mod: The desired modulation (:data:`BPSK` or :data:`QPSK`)
        :param labels: Bits to symbols mapping. Typically Gray encoding is used.
        :param amplitude: The L2-norm of the constellation symbols
        :param phase_offset: The initial phase offset (rad)
        """
        self.mod = mod
        self.labels = labels
        self.constellation = amplitude * np.exp(1j * (2 * np.pi * np.arange(self.mod.order) / self.mod.order + phase_offset))
        self._map = dict(zip([tuple(x2binlist(x, self.mod.bits_per_symbol)) for x in labels], self.constellation))
        self._inv_map = dict(zip(self._map.values(), self._map.keys()))

    def modulate(self, bits: np.ndarray, symbols: np.ndarray) -> int:
        """
        Modulates a stream of bits into symbols.

        :param bits: Input bits
        :param bits: Output symbols
        :return: 0 if OK, error code otherwise
        """
        m = self.mod.bits_per_symbol
        n_symbols = len(symbols)
        assert len(bits) == len(symbols) * m
        for i, bit_sequence in enumerate(np.reshape(bits, newshape=(n_symbols, m))):
            symbols[i] = self._map[tuple(bit_sequence)]
        return 0

    def demodulate(self, symbols: np.ndarray, bits: np.ndarray) -> int:
        """
        Demodulates a stream of symbols into bits.

        :param bits: Input symbols
        :param symbols: Output bits
        :return: 0 if OK, error code otherwise
        """
        bps = self.mod.bits_per_symbol
        for i, s in enumerate(symbols):
            s_idx = np.argmin(np.abs(s - self.constellation))
            s_hat = self.constellation[s_idx]
            bits[i * bps : (i + 1) * bps] = self._inv_map[s_hat]
        return 0

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties.
        """
        args = 'mod={}, labels={}, constellation={}'.format(self.mod, self.labels, self.constellation)
        return '{}({})'.format(self.__class__.__name__, args)
