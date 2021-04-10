"""
Utilities.
"""
import logging
from enum import Enum
from typing import Tuple

import numpy as np

_log = logging.getLogger(__name__)

def power(inp: np.ndarray) -> float:
    """
    Computes the average power of the input signal.

    :param inp: Input signal
    :return: Average power in the input signal
    """
    samples = inp * np.conj(inp)
    return np.sum(samples) / len(samples).real

def ber(inp0: np.ndarray, inp1: np.ndarray) -> Tuple[int, int]:
    """
    Computes the bit error rate (BER) by comparing two sequences of equal length.

    :param inp0: First array to compare
    :param inp1: Second array to compare
    :return: The first element is the number of different elements between the two input arrays. The second element is the length of the input arrays.
    """
    err, total = len(np.where(inp1 != inp0)[0]), len(inp0)
    return err, total

class Endian(Enum):
    """
    An enumeration to represent endianness.
    """

    MSB = 0
    """
    Most-significant bit first.
    """

    LSB = 1
    """
    Least-significant bit first.
    """

class Pack:
    """
    Takes :attr:`inp_width`-lsb from each input element and packs them into :attr:`out_width`-lsb output elements.

    :attr:`inp_width` has to be an integer multiple of :attr:`out_width`.
    """

    def __init__(self, inp_width: int, out_width: int, endian: Endian):
        """
        :param inp_width: Number of bits to take from each input sample
        :param out_width: Number of bits to pack into each output sample
        :param endian: Packing order
        """
        self._inp_width = inp_width
        self._out_width = out_width
        self._mask = (1 << self.inp_width) - 1
        self._num_chunks = out_width // inp_width
        self._endian = endian
        if self.endian == Endian.MSB:
            self._range = np.arange(self._num_chunks -1, -1, -1)
        else:
            self._range = np.arange(0, 1, self._num_chunks)

    @property
    def inp_width(self) -> int:
        """
        Number of bits to take from each input sample.
        """
        return self._inp_width

    @property
    def out_width(self) -> int:
        """
        Number of bits to pack into each output sample.
        """
        return self._out_width

    @property
    def endian(self) -> int:
        """
        Packing order.
        """
        return self._endian

    @property
    def num_chunks(self) ->  int:
        """
        Number of input elements for each output element. This is calculated as :code:`out_width // inp_width` (notice it's a floor division which truncates the decimal part).
        """
        return self._num_chunks

    def __call__(self, inp: np.ndarray) -> int:
        """
        The main work function.

        This function packs a single element. For packing a sequence of elements see :func:`call_list`. It's the caller's responsibility to ensure there are enough elements in ``inp``.

        :param inp: Unpacked input samples
        :return: Packed output sample
        """
        out = 0
        for i, j in zip(range(0, self.num_chunks), self._range):
            chunk = inp[i] & self._mask
            out |= chunk << (self.inp_width * j)
        return out

    def call__list(self, inp: np.ndarray, out: np.ndarray):
        """
        The main work function for packing a sequence of elements.
        TODO Could use an overloaded version of :func:`__call__`, but @singledispatch for class methods is only available in Python >= 3.8.

        It's the caller's responsibility to ensure there are enough elements in ``inp``.

        :param inp: Unpacked input samples
        :param out: Packed output samples
        :return: 0 if OK, error code otherwise
        """
        for i, j in zip(range(0, len(inp), self.num_chunks), range(len(out))):
            out[j] = 0
            for idx in range(self.num_chunks - 1, -1, -1):
                chunk = inp[i] & self._mask
                out[j] |= chunk << (self.inp_width * idx)
                i += 1

class Unpack:
    """
    Takes :attr:`inp_width`-lsb from each input element and unpacks them into :attr:`out_width`-lsb output elements.

    :attr:`out_width` has to be an integer multiple of :attr:`inp_width`.
    """

    def __init__(self, inp_width: int, out_width: int, endian: Endian):
        """
        :param inp_width: Number of bits to take from each input sample
        :param out_width: Number of bits to unpack into each output sample
        :param endian: Unpacking order
        """
        self._inp_width = inp_width
        self._out_width = out_width
        self._mask = (1 << self.out_width) - 1
        self._num_chunks = inp_width // out_width
        self._endian = endian
        if self.endian == Endian.MSB:
            self._range = np.arange(self._num_chunks -1, -1, -1)
        else:
            self._range = np.arange(0, 1, self._num_chunks)

    @property
    def inp_width(self) -> int:
        """
        Number of bits to take from each input sample.
        """
        return self._inp_width

    @property
    def out_width(self) -> int:
        """
        Number of bits to unpack into each output sample.
        """
        return self._out_width

    @property
    def endian(self) -> int:
        """
        Unpacking order.
        """
        return self._endian

    @property
    def num_chunks(self) ->  int:
        """
        Number of output elements for each input element. This is calculated as :code:`inp_width // out_width` (notice it's a floor division which truncates the decimal part).
        """
        return self._num_chunks

    def __call__(self, inp: int, out: np.ndarray) -> int:
        """
        The main work function.

        This function unpack a single element. For unpacking a sequence of elements see :func:`call_list`. It's the caller's responsibility to ensure there are enough elements in ``out``.

        :param inp: Packed input sample
        :param out: Unpacked output samples
        :return: 0 if OK, error code otherwise
        """
        for i, j in zip(self._range, range(self.num_chunks)):
            chunk = (inp >> (self.out_width * i)) & self._mask
            out[j] = chunk

    def call__list(self, inp: np.ndarray, out: np.ndarray):
        """
        The main work function for unpacking a sequence of elements.
        TODO Could use an overloaded version of :func:`__call__`, but :ref:`@singledispatch` for class methods is only available in Python >= 3.8.

        It's the caller's responsibility to ensure there are enough elements in ``out``.

        :param inp: Packed input samples
        :param out: Unpacked output samples
        :return: 0 if OK, error code otherwise
        """
        for i, j in zip(range(len(inp)), range(0, len(out), self.num_chunks)):
            for idx in self._range:
                chunk = (inp[i] >> (self.out_width * idx)) & self._mask
                out[j] = chunk
                j += 1
