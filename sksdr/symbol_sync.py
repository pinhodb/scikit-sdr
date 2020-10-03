import logging
from typing import Optional, Tuple

import numpy as np

from .modulation import BPSK, QPSK, Modulation

_log = logging.getLogger(__name__)

class SymbolSync:
    def __init__(self, mod: Modulation, sps: int, damp_factor: float, norm_loop_bw: float, K: float, A: float):
        self.mod = mod
        self.sps = sps

        # Interpolator config
        self.mu = 0.
        self.alpha = 0.5
        self._coeffs = np.array([
            [ 0,                     0,              1,            0],
            [-self.alpha, 1+self.alpha, -(1-self.alpha), -self.alpha],
            [ self.alpha,  -self.alpha,    -self.alpha,   self.alpha]])
        self._interp_states = np.zeros((3, 1))

        # ζ (damping factor)
        self.damp_factor = damp_factor

        # Loop bandwidth normalized by sample rate
        self.norm_loop_bw = norm_loop_bw

        # Derive proportional gain (K1) and integrator gain (K2) in the loop
        # filter. Kp for Timing Recovery PLL, determined by 2KA^2*2.7 (for
        # binary PAM), QPSK could be treated as two individual binary PAM, 2.7
        # is for raised cosine filter with roll-off factor 0.5
        self.K = K
        self.A = A
        if self.mod == BPSK:
            det_gain = 2.7 * 2 * self.K * self.A**2
        elif self.mod == QPSK:
            det_gain = 2.7 * 2 * self.K * self.A**2 + 2.7 * 2 * self.K * self.A**2
        else:
            raise NotImplementedError('Only BPSK and QPSK are implemented')

        zeta = self.damp_factor
        BnTs = self.norm_loop_bw
        Kp = det_gain
        K0 = -1.0
        theta = BnTs / sps / (zeta + 0.25 / zeta)
        d = (1 + 2 * zeta * theta + theta**2) * K0 * Kp
        self.p_gain = (4 * zeta * theta) / d
        self.i_gain = (4 * theta * theta) / d

        self._loopfilt_state = 0.0
        self._loopfilt_prev_in = 0.0

        # TED config
        self._ted_buf = np.zeros(sps, dtype=complex)

        # Counter config
        self._strobe = False
        self._strobe_count = 0
        self._strobe_hist = np.zeros(sps)
        self._nco_count = 0

        _log.debug('SSYNC init: theta=%f, d=%f, p_gain=%f, i_gain=%f', theta, d, self.p_gain, self.i_gain)

    def __call__(self, inp: np.ndarray, nout: Optional[int] = None) -> Tuple[np.ndarray, int, np.ndarray]:
        _symbols = np.empty(int(len(inp) / self.sps * 1.1), dtype=complex)
        _timing_err = np.empty_like(inp)
        self._strobe_count = 0

        idx = 0
        for idx, i in enumerate(inp):
            # Interpolator
            _timing_err[idx] = self.mu

            xseq = np.vstack((i, self._interp_states))
            int_v = self._coeffs.dot(xseq)
            int_out = np.sum(int_v * np.array([[1, self.mu, self.mu**2]]).T)
            self._interp_states = xseq[:3]

            if self._strobe:
                _symbols[self._strobe_count] = int_out
                self._strobe_count += 1

            # ZCTED
            # Calculate the midsample point for odd or even samples per symbol
            if self._strobe and not np.any(self._strobe_hist[1:]):
                l = len(self._ted_buf) / 2
                t1 = self._ted_buf[int(np.floor(l))]
                t2 = self._ted_buf[int(np.ceil(l))]
                mid_sample = (t1 + t2) / 2
                e = mid_sample.real * (np.sign(self._ted_buf[0].real) - np.sign(int_out.real)) \
                    + mid_sample.imag * (np.sign(self._ted_buf[0].imag) - np.sign(int_out.imag))
            else:
                e = 0

            # Stuffing and skipping
            s = np.sum(np.hstack((self._strobe_hist[1:], self._strobe))) # Strobe is a bool that gets converted to 1
            if s == 0:
                pass
            elif s == 1:
                self._ted_buf = np.hstack((self._ted_buf[1:], int_out))
            else:
                self._ted_buf = np.hstack((self._ted_buf[2:], 0, int_out))

            # Loop filter
            loopfilt_out = self._loopfilt_prev_in + self._loopfilt_state
            v = e * self.p_gain + loopfilt_out
            self._loopfilt_state = loopfilt_out
            self._loopfilt_prev_in = e * self.i_gain

            # Interpolator control
            W = v + 1. / self.sps # W should be small when locked
            self._strobe_hist = np.hstack((self._strobe_hist[1:], self._strobe))
            self._strobe = (self._nco_count < W)
            if self._strobe: # update mu if a strobe
                self.mu = self._nco_count / W

            self._nco_count = (self._nco_count - W) % 1 # update counter

            if self._strobe_count == nout:
                break
        return _symbols[:self._strobe_count], idx + 1, _timing_err

    def __repr__(self):
        args = 'mod={}, sps={}, damp_factor={}, norm_loop_gain={}, K={} A={}' \
               .format(self.mod, self.sps, self.damp_factor, self.norm_loop_bw, self.K, self.A)
        return '{}({})'.format(self.__class__.__name__, args)
