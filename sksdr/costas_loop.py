import logging
from typing import Optional, Tuple

import numpy as np

from .control_loop import PLL

_log = logging.getLogger(__name__)

class CostasLoop(PLL):
    def __init__(self, loop_bandwidth: float):
        super().__init__(loop_bandwidth, 1.0, -1.0)
        #_log.debug('SSYNC init: theta=%f, d=%f, p_gain=%f, i_gain=%f', theta, d, self.p_gain, self.i_gain)

    def __call__(self, inp: np.ndarray, out: np.ndarray, error: np.ndarray, filter_out: np.ndarray) -> int:

        for i, _ in enumerate(out):
            nco_out = np.exp(-1j * self.phase)
            out[i] = inp[i] * nco_out
            error[i] = out[i].real * out[i].imag
            filter_out[i] = self.advance_loop(error[i])
            self.phase_wrap()
            self.frequency_limit()
        return 0

    def __repr__(self):
        # args = 'mod={}, sps={}, damp_factor={}, norm_loop_gain={}, K={} A={}' \
        #        .format(self.mod, self.sps, self.damp_factor, self.norm_loop_bw, self.K, self.A)
        # return '{}({})'.format(self.__class__.__name__, args)
        return ''
