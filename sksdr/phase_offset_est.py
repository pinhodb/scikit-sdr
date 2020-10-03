import logging

import numpy as np

_log = logging.getLogger(__name__)

class PhaseOffsetEst:
    def __init__(self, preamble: np.ndarray):
        self.preamble = preamble

    def __call__(self, inp: np.ndarray) -> np.ndarray:
        cprb = np.conj(self.preamble)
        sprb = inp[:len(self.preamble)]

        phase_vector_est = np.mean(sprb * cprb)
        phase_est = np.angle(phase_vector_est)
        phase_est_discrete = np.round(phase_est * 2 / np.pi) * np.pi / 2

        out = inp * np.exp(1j * -phase_est_discrete)
        return out

    def __repr__(self):
        args = 'preamble={}'.format(self.preamble)
        return '{}({})'.format(self.__class__.__name__, args)
