import logging

import numpy as np

_log = logging.getLogger(__name__)

class PhaseOffsetEst:
    def __init__(self, preamble: np.ndarray):
        self._preamble = preamble

    def __call__(self, inp: np.ndarray, out: np.ndarray) -> int:
        cprb = np.conj(self._preamble)
        sprb = inp[:len(self._preamble)]

        phase_vector_est = np.mean(sprb * cprb)
        phase_est = np.angle(phase_vector_est)
        phase_est_discrete = np.round(phase_est * 2 / np.pi) * np.pi / 2

        out[:] = inp * np.exp(1j * -phase_est_discrete)
        return 0

    def __repr__(self):
        args = 'preamble={}'.format(self._preamble)
        return '{}({})'.format(self.__class__.__name__, args)
