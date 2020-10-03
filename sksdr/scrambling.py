import logging
from collections import deque

import numpy as np

_log = logging.getLogger(__name__)

class Scrambler:
    def __init__(self, poly: list, init_state: list):
        self.poly = poly
        self.init_state = init_state
        self._state = deque(self.init_state, maxlen=4)

    def __call__(self, data: np.ndarray) -> np.ndarray:
        y = np.empty_like(data)
        for i, b in enumerate(data):
            for j in range(1, len(self.poly)):
                if self.poly[j]:
                    b ^= self._state[j-1]
                    # to work with modulo-N, use this instead of XOR
                    #b = (b + data) % N
            y[i] = b
            self._state.appendleft(b)
        return y

    def __repr__(self):
        args = 'poly={}, init_state={}'.format(self.poly, self.init_state)
        return '{}({})'.format(self.__class__.__name__, args)


class Descrambler:
    def __init__(self, poly: list, init_state: list):
        self.poly = poly
        self.init_state = init_state
        self._state = deque(self.init_state, maxlen=4)

    def __call__(self, data: np.ndarray) -> np.ndarray:
        y = np.empty_like(data)
        for i, b in enumerate(data):
            for j in range(1, len(self.poly)):
                if self.poly[j]:
                    b ^= self._state[j-1]
                    # to work with modulo-N, use this instead of XOR
                    #b = (b + data) % N
            y[i] = b
            self._state.appendleft(data[i])
        return y

    def __repr__(self):
        args = 'poly={}, init_state={}'.format(self.poly, self.init_state)
        return '{}({})'.format(self.__class__.__name__, args)
