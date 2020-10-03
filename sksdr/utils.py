import logging
from functools import singledispatch
from typing import Tuple

import numpy as np

_log = logging.getLogger(__name__)

@singledispatch
def x2binlist(x, width, endian='msb'):
    raise TypeError(str(type(x)) + ' not supported.')

@x2binlist.register(int)
@x2binlist.register(np.uint8)
@x2binlist.register(np.uint32)
@x2binlist.register(np.uint64)
@x2binlist.register(np.int64)
def _(x, width, endian='msb'):
    if endian == 'lsb':
        y = [(x >> i) & 1 for i in range(width)]
    else:
        y = [(x >> i) & 1 for i in range(width - 1, -1, -1)]
    return np.array(y)

@x2binlist.register(list)
@x2binlist.register(np.ndarray)
def _(x, width, endian='msb'):
    ret = np.empty(len(x) * width, dtype=int)
    for idx, val in enumerate(x):
        ret[idx * width : (idx + 1) * width] = x2binlist(val, width, endian)
    return ret

@x2binlist.register(str)
def _(x, width, endian='msb'):
    ret = np.empty(len(x) * width, dtype=int)
    for idx, val in enumerate(x):
        ret[idx * width : (idx + 1) * width] = x2binlist(ord(val), width, endian)
    return ret

@singledispatch
def binlist2x(x, width, endian='msb'):
    raise TypeError(str(type(x)) + ' not supported.')

@binlist2x.register(list)
@binlist2x.register(np.ndarray)
def _(x, width, endian='msb'):
    ret = np.empty(int(np.floor(len(x) / width)), dtype=int)
    for j in range(0, len(x) - len(x) % width, width):
        x2 = x[j : j + width]
        if endian == 'lsb':
            ret[int(j / width)] = sum(x2[i] << i for i in range(width))
        else:
            ret[int(j / width)] = sum(x2[i] << width - 1 - i for i in range(width))
    return ret

def power(x: np.ndarray, n=1) -> float:
    start = int((1-n) * len(x))
    samples = x[start:]**2
    return np.sum(samples) / len(samples)

def ber(tx: np.ndarray, rx: np.ndarray) -> Tuple[int, int]:
    err, total = len(np.where(rx != tx)[0]), len(tx)
    return err, total
