"""
Digital modulation schemes.
"""
import logging

import numpy as np

_log = logging.getLogger(__name__)

class Modulation:
    """
    Represents a digital modulation, such as BPSK or QPSK.
    """
    def __init__(self, name: str, order: int):
        """
        :param name: Modulation name
        :param order: Modulation order
        """
        self._name = name
        self._order = order
        self.bits_per_symbol = int(np.log2(self.order))


    @property
    def name(self) -> int:
        """
        Modulation name.
        """
        return self._name

    @property
    def order(self) -> int:
        """
        Modulation order.
        """
        return self._order

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties
        """
        args = 'name={}, order={}, bits_per_symbol={}'.format(self.name, self.order, self.bits_per_symbol)
        return '{}({})'.format(self.__class__.__name__, args)

BPSK = Modulation('BPSK', 2)
"""
BPSK modulation.
"""

QPSK = Modulation('QPSK', 4)
"""
QPSK modulation.
"""

modulations = (
    BPSK,
    QPSK
)
"""
A tuple of the existing modulations.
"""

class PSKModulator:
    r"""
    Base class of PSK modulators that turn a stream of bits into complex symbols and vice-versa.

    Supports BPSK and QPSK modulation schemes. :attr:`labels` specifies the label of each constellation point. :attr:`amplitude` specifies the absolute value of the symbols (i.e., its L2-norm). :attr:`phase_offset` is the offset of the first symbol in the complex plane. Only ‘hard’ demodulation is supported at the moment (i.e., the module chooses the constellation point closest to the symbol). Symbols are thus generated using:

    .. math::
        Ae^{j(2\pi \frac{n}{N} + \phi)}, \textrm{for} m=[0, ..., N-1]

    where :math:`N` is the modulation order (the number of different symbols that can be transmitted with it), which can be obtained using :attr:`Modulation.order`.

    Example:

    >>> import sksdr
    >>> import numpy as np
    >>> qpsk = sksdr.PSKModulator(sksdr.QPSK, [0, 1, 2, 3], phase_offset=np.pi/4)
    >>> qpsk.constellation
    array([ 0.70710678+0.70710678j, -0.70710678+0.70710678j,
       -0.70710678-0.70710678j,  0.70710678-0.70710678j])
    """
    def __init__(self, mod: Modulation, labels: list, amplitude: float = 1.0, phase_offset: float = 0.0):
        """
        :param mod: Modulation (:data:`BPSK` or :data:`QPSK`)
        :param labels: Bits to symbols mapping, typically using Gray encoding
        :param amplitude: L2-norm of the constellation symbols
        :param phase_offset: Initial phase offset (rad)
        """
        self._mod = mod
        self._labels = labels
        self._constellation = amplitude * np.exp(1j * (2 * np.pi * np.arange(self.mod.order) / self.mod.order + phase_offset))
        self._map = dict(zip((x for x in labels), self.constellation))
        self._inv_map = dict(zip(self._map.values(), self._map.keys()))

    @property
    def mod(self) -> Modulation:
        """
        Modulation (:data:`BPSK` or :data:`QPSK`).
        """
        return self._mod

    @property
    def labels(self) -> list:
        """
        Bits to symbols mapping, typically using Gray encoding.
        """
        return self._labels

    @property
    def constellation(self) -> list:
        """
        Constellation of symbols.
        """
        return self._constellation

    @staticmethod
    def from_modulation(mod: Modulation, labels: list, amplitude: float = 1.0, phase_offset: float = 0.0):
        """
        Factory method to create the appropriate modulator for the given :class:Modulation as specified by `mod`.
        """
        if mod.name == 'BPSK':
            return BPSKModulator(labels, amplitude, phase_offset)
        elif mod.name == 'QPSK':
            return QPSKModulator(labels, amplitude, phase_offset)

    def demodulate(self, symbols: np.ndarray, bits: np.ndarray) -> int:
        """
        Demodulates a stream of symbols into bits.

        :param bits: Input symbols
        :param symbols: Output bits
        :return: 0 if OK, error code otherwise
        """
        for i, s in enumerate(symbols):
            s_idx = np.argmin(np.abs(s - self.constellation))
            s_hat = self.constellation[s_idx]
            bits[i] = self._inv_map[s_hat]
        return 0

    def __repr__(self):
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties
        """
        args = 'mod={}, labels={}, constellation={}'.format(self.mod, self.labels, self.constellation)
        return '{}({})'.format(self.__class__.__name__, args)

class BPSKModulator(PSKModulator):
    """
    Modulates a stream of packed bits into complex symbols and vice-versa, using BPSK.
    """

    def __init__(self, labels: list, amplitude: float = 1.0, phase_offset: float = 0.0):
        """
        :param labels: Bits to symbols mapping
        :param amplitude: L2-norm of the constellation symbols
        :param phase_offset: Initial phase offset (rad)
        """
        super().__init__(BPSK, labels, amplitude, phase_offset)

    def modulate(self, bits: np.ndarray, symbols: np.ndarray) -> int:
        """
        Modulates a stream of bits into symbols.

        :param bits: Input bits
        :param bits: Output symbols
        :return: 0 if OK, error code otherwise
        """
        syms = np.empty(8, dtype=np.uint8)
        for i, j in zip(range(len(bits)), range(0, len(symbols), 8)):
            syms[0] = (bits[i] >> 7) & 0x1
            syms[1] = (bits[i] >> 6) & 0x1
            syms[2] = (bits[i] >> 5) & 0x1
            syms[3] = (bits[i] >> 4) & 0x1
            syms[4] = (bits[i] >> 3) & 0x1
            syms[5] = (bits[i] >> 2) & 0x1
            syms[6] = (bits[i] >> 1) & 0x1
            syms[7] = bits[i] & 0x3
            symbols[j : j + 8] = [self._map[sym] for sym in syms]
        return 0

class QPSKModulator(PSKModulator):
    """
    Modulates a stream of packed bits into complex symbols and vice-versa, using QPSK.
    """

    def __init__(self, labels: list, amplitude: float = 1.0, phase_offset: float = 0.0):
        """
        :param labels: Bits to symbols mapping, typically using Gray encoding
        :param amplitude: L2-norm of the constellation symbols
        :param phase_offset: Initial phase offset (rad)
        """
        super().__init__(QPSK, labels, amplitude, phase_offset)

    def modulate(self, bits: np.ndarray, symbols: np.ndarray) -> int:
        """
        Modulates a stream of bits into symbols.

        :param bits: Input bits
        :param bits: Output symbols
        :return: 0 if OK, error code otherwise
        """
        syms = np.empty(4, dtype=np.uint8)
        for i, j in zip(range(len(bits)), range(0, len(symbols), 4)):
            syms[0] = (bits[i] >> 6) & 0x3
            syms[1] = (bits[i] >> 4) & 0x3
            syms[2] = (bits[i] >> 2) & 0x3
            syms[3] = bits[i] & 0x3
            symbols[j : j + 4] = [self._map[sym] for sym in syms]
        return 0
