"""
Phase/Frequency synchronization algorithms.
"""
import logging
from typing import Tuple

import numpy as np

from .modulation import BPSK, QPSK, Modulation

_log = logging.getLogger(__name__)

class PSKSync:
    """
    Compensates for carrier frequency and phase offsets in signals in BPSK and QPSK.

    The algorithm is a closed loop synchronizer that uses the discrete phase-locked loop (PLL) based algorithm described in :cite:`rice08`.
    The maximum likelihood (ML) phase error detector (PED) is chosen, which consists of minimizing the energy in :math:`\theta_e` . It also has the advantage of avoiding arctangent operations required by other phase detectors based on a purely geometric The ML phase detector first de-rotates the input signal by the estimated phase from the DDS output (CCW rotation block). This leaves only the phase of the received data symbol :math:`\theta_r = \theta-\hat\theta`. It then subtracts the phase of the transmitted data symbol to obtain the phase error, :math:`\theta_e=\theta_r-\theta_d` . This is usually used in a data-aided system, in which there is a training sequence where the transmission symbols are well known. If the symbols are unknown then it is called a decision-directed system and the transmitted symbols must be estimated.

    Kp is the slope of phase detector S-Curve in the linear range
    BPSK: Kp = K * A^2
    QPSK: Kp = 2 * K * A^2
    K = Amplitude of received signal (unit gain from AGC)
    A = Norm of constellation point
    K1 (loop filter proportional gain)
    K2 (loop filter integral gain)
    # Loop bandwidth normalized by sample rate
    phase_recovery_loop_bw = self.norm_loop_bw * self.sps
    """
    def __init__(self, mod: Modulation, sps: int, damp_factor: float, norm_loop_bw: float):
        self.sps = sps
        self.mod = mod

        # ζ (damping factor)
        self.damp_factor = damp_factor

        # Loop bandwidth normalized by sample rate
        self.norm_loop_bw = norm_loop_bw # Hz
        self.dds_gain = -1.0

        self._prev_sample = 0j
        self._dds_prev_input = 0.0
        self._integratorfilt_state = 0.0
        self._loopfilt_state = 0.0
        self._phase = 0.0

        # Kp is the slope of phase detector S-Curve in the linear range
        # BPSK: Kp = K * A^2
        # QPSK: Kp = 2 * K * A^2
        # K = Amplitude of received signal (unit gain from AGC)
        # A = Norm of constellation point
        # K0 (phase detector gain)
        if self.mod == BPSK:
            self.ped = 1
            self.ped_gain = 1 # Kp
        elif self.mod == QPSK:
            self.ped = 2
            self.ped_gain = 2 # Kp
        else:
            raise NotImplementedError('Only BPSK and QPSK are implemented')

        # Loop bandwidth normalized by sample rate
        phase_recovery_loop_bw = self.norm_loop_bw * self.sps

        # K0 (phase detector gain)
        phase_recovery_gain = self.sps
        theta = phase_recovery_loop_bw / ((self.damp_factor + 0.25 / self.damp_factor) * self.sps)
        d = 1 + 2 * self.damp_factor * theta + theta * theta

        # K1 (loop filter proportional gain)
        self.p_gain = (4 * self.damp_factor * theta/d) / (self.ped_gain * phase_recovery_gain)
        # K2 (loop filter integral gain)
        self.i_gain = (4 / self.sps * theta * theta/d) / (self.ped_gain * phase_recovery_gain)

        _log.debug('FSYNC init: phase_recovery_loop_bw=%f, phase_recovery_gain=%f, theta=%f, d=%f, p_gain=%f, i_gain=%f',
                   phase_recovery_loop_bw, phase_recovery_gain, theta, d, self.p_gain, self.i_gain)

    def __call__(self, inp: np.ndarray, out: np.ndarray, phase_estimate: np.ndarray = None) -> int:

        def common_logic():
            # Phase accumulate and correct
            out[idx] = val * np.exp(1j * self._phase)

            # Loop filter
            loopfilt_out = ph_err * self.i_gain + self._loopfilt_state
            self._loopfilt_state = loopfilt_out

            # DDS implemented as an integrator
            dds_out = self._dds_prev_input + self._integratorfilt_state
            self._integratorfilt_state = dds_out
            self._dds_prev_input = ph_err * self.p_gain + loopfilt_out

            self._phase = self.dds_gain * dds_out
            if phase_estimate is not None:
                phase_estimate[idx] = -self._phase
            self._prev_sample = out[idx]

        if self.ped == 1: # BPSK
            for idx, val in enumerate(inp):
                # Compute phase error
                ph_err = np.sign(self._prev_sample.real) * self._prev_sample.imag
                common_logic()

        elif self.ped == 2: # QPSK
            for idx, val in enumerate(inp):
                # Compute phase error
                ph_err = np.sign(self._prev_sample.real) * self._prev_sample.imag \
                         - np.sign(self._prev_sample.imag) * self._prev_sample.real
                common_logic()
        return 0

    def __repr__(self):
        args = 'sps={}, mod={}, damp_factor={}, norm_loop_gain={}' \
               .format(self.sps, repr(self.mod), self.damp_factor, self.norm_loop_bw)
        return '{}({})'.format(self.__class__.__name__, args)
