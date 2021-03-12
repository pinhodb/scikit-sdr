"""
Control loop algorithms.
"""
import logging
from typing import Optional, Tuple

import numpy as np

_log = logging.getLogger(__name__)

class PLL:
    """
    Generic Phase-locked Loop structure.

    Implements a 2nd-order generic PLL algorithm as described in :cite:`rice08`. The PLL consists of three basic components: the phase detector, the loop filter and the numerically-controlled oscillator (NCO). This class implements a  proportional-plus-integrator loop filter and a NCO implemented as an integrator. The phase detector is implementation-specific and so the typical usage pattern is to create an application-specific class (e.g., :ref:`CostasLoop`) that uses/extends this class and implements it's own phase-detector.

    Two parameters are usually used to characterize a 2nd-order loop. The *damping factor* denoted by :math:`\zeta` and *natural frequency* denoted by :math:`\omega_n`. These parameters are given by:

    .. math::
        \zeta & =\frac{k_1}{2}\sqrt{\frac{k_0 k_p}{k_2}}
        \omega_n & = \sqrt{k_0 k_p k_2}

    where :math:`k0` is the NCO gain, :math:`kp is the phase detector gain, k1 is the loop filter proportional gain and k2 is the loop filter integrator gain`.
    """
    def __init__(self, loop_bandwidth: float, max_freq: float, min_freq: float):
        """
        """
        self._phase = 0
        self._frequency = 0

        self.max_freq = max_freq
        self.min_freq = min_freq

        # Set the damping factor for a critically damped system
        self._loop_bandwidth = 0
        self.damping = np.sqrt(2.0) / 2.0

        # Set the bandwidth, which will then call update_gains()
        self.loop_bandwidth = loop_bandwidth

    @property
    def min_freq(self):
        return self._min_freq

    @min_freq.setter
    def min_freq(self, value: float):
        self._min_freq = value

    @property
    def max_freq(self):
        return self._max_freq

    @max_freq.setter
    def max_freq(self, value: float):
        self._max_freq = value

    @property
    def loop_bandwidth(self):
        return self._loop_bandwidth

    @loop_bandwidth.setter
    def loop_bandwidth(self, value: float):
        if value < 0:
            raise ValueError(f'Invalid bandwidth {value}. Must be >= 0.')
        self._loop_bandwidth = value
        self.update_gains()

    @property
    def damping(self):
        return self._damping

    @damping.setter
    def damping(self, value: float):
        if value < 0:
            raise ValueError(f'Invalid damping factor {value}. Must be >= 0.')
        self._damping = value
        self.update_gains()

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value: float):
        if value < 0 or value > 1.0:
            raise ValueError(f'Invalid alpha {value}. Must be [0,1].')
        self._alpha = value

    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, value: float):
        if value < 0 or value > 1.0:
            raise ValueError(f'Invalid beta {value}. Must be in [0,1].')
        self._beta = value

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value: float):
        if value > self.max_freq:
            self._frequency = self.max_freq
        elif value < self.min_freq:
            self._frequency = self.min_freq
        else:
            self._frequency = value

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, value: float):
        self._phase = value
        while self._phase > 2 * np.pi:
            self._phase -= 2 * np.pi
        while self._phase < -2 * np.pi:
            self._phase += 2 * np.pi

    def __call__(self, inp: np.ndarray, nout: Optional[int] = None) -> Tuple[np.ndarray, int, np.ndarray]:
        pass

    def __repr__(self):
        # args = 'mod={}, sps={}, damp_factor={}, norm_loop_gain={}, K={} A={}' \
        #        .format(self.mod, self.sps, self.damp_factor, self.norm_loop_bw, self.K, self.A)
        # return '{}({})'.format(self.__class__.__name__, args)
        return ''

    def update_gains(self):
        denom = 1.0 + 2.0 * self.damping * self.loop_bandwidth + self.loop_bandwidth**2
        self.alpha = (4 * self.damping * self.loop_bandwidth) / denom
        self.beta = (4 * self.loop_bandwidth**2) / denom

    def phase_wrap(self):
        while self.phase > 2 * np.pi:
            self.phase -= 2 * np.pi
        while self.phase < -2 * np.pi:
            self.phase += 2 * np.pi

    def frequency_limit(self):
        if self.frequency > self.max_freq:
            self.frequency = self.max_freq
        elif self.frequency < self.min_freq:
            self.frequency = self.min_freq

    def advance_loop(self, error: float):
        self.frequency = self.frequency + self.beta * error
        self.phase = self.phase + self.frequency + self.alpha * error
        return self.frequency + self.alpha * error

    _tanh_lut_table = [
        -0.96402758, -0.96290241, -0.96174273, -0.96054753, -0.95931576, -0.95804636,
        -0.95673822, -0.95539023, -0.95400122, -0.95257001, -0.95109539, -0.9495761,
        -0.94801087, -0.94639839, -0.94473732, -0.94302627, -0.94126385, -0.93944862,
        -0.93757908, -0.93565374, -0.93367104, -0.93162941, -0.92952723, -0.92736284,
        -0.92513456, -0.92284066, -0.92047938, -0.91804891, -0.91554743, -0.91297305,
        -0.91032388, -0.90759795, -0.9047933,  -0.90190789, -0.89893968, -0.89588656,
        -0.89274642, -0.88951709, -0.88619637, -0.88278203, -0.87927182, -0.87566342,
        -0.87195453, -0.86814278, -0.86422579, -0.86020115, -0.85606642, -0.85181914,
        -0.84745683, -0.84297699, -0.83837709, -0.83365461, -0.82880699, -0.82383167,
        -0.81872609, -0.81348767, -0.80811385, -0.80260204, -0.7969497,  -0.79115425,
        -0.78521317, -0.77912392, -0.772884,   -0.76649093, -0.75994227, -0.75323562,
        -0.74636859, -0.73933889, -0.73214422, -0.7247824,  -0.71725127, -0.70954876,
        -0.70167287, -0.6936217,  -0.68539341, -0.67698629, -0.66839871, -0.65962916,
        -0.65067625, -0.64153871, -0.6322154,  -0.62270534, -0.61300768, -0.60312171,
        -0.59304692, -0.58278295, -0.57232959, -0.56168685, -0.55085493, -0.53983419,
        -0.52862523, -0.51722883, -0.50564601, -0.49387799, -0.48192623, -0.46979241,
        -0.45747844, -0.44498647, -0.4323189,  -0.41947836, -0.40646773, -0.39329014,
        -0.37994896, -0.36644782, -0.35279057, -0.33898135, -0.32502449, -0.31092459,
        -0.2966865,  -0.28231527, -0.26781621, -0.25319481, -0.23845682, -0.22360817,
        -0.208655,   -0.19360362, -0.17846056, -0.16323249, -0.14792623, -0.13254879,
        -0.11710727, -0.10160892, -0.08606109, -0.07047123, -0.05484686, -0.0391956,
        -0.02352507, -0.00784298, 0.00784298,  0.02352507,  0.0391956,   0.05484686,
        0.07047123,  0.08606109,  0.10160892,  0.11710727,  0.13254879,  0.14792623,
        0.16323249,  0.17846056,  0.19360362,  0.208655,    0.22360817,  0.23845682,
        0.25319481,  0.26781621,  0.28231527,  0.2966865,   0.31092459,  0.32502449,
        0.33898135,  0.35279057,  0.36644782,  0.37994896,  0.39329014,  0.40646773,
        0.41947836,  0.4323189,   0.44498647,  0.45747844,  0.46979241,  0.48192623,
        0.49387799,  0.50564601,  0.51722883,  0.52862523,  0.53983419,  0.55085493,
        0.56168685,  0.57232959,  0.58278295,  0.59304692,  0.60312171,  0.61300768,
        0.62270534,  0.6322154,   0.64153871,  0.65067625,  0.65962916,  0.66839871,
        0.67698629,  0.68539341,  0.6936217,   0.70167287,  0.70954876,  0.71725127,
        0.7247824,   0.73214422,  0.73933889,  0.74636859,  0.75323562,  0.75994227,
        0.76649093,  0.772884,    0.77912392,  0.78521317,  0.79115425,  0.7969497,
        0.80260204,  0.80811385,  0.81348767,  0.81872609,  0.82383167,  0.82880699,
        0.83365461,  0.83837709,  0.84297699,  0.84745683,  0.85181914,  0.85606642,
        0.86020115,  0.86422579,  0.86814278,  0.87195453,  0.87566342,  0.87927182,
        0.88278203,  0.88619637,  0.88951709,  0.89274642,  0.89588656,  0.89893968,
        0.90190789,  0.9047933,   0.90759795,  0.91032388,  0.91297305,  0.91554743,
        0.91804891,  0.92047938,  0.92284066,  0.92513456,  0.92736284,  0.92952723,
        0.93162941,  0.93367104,  0.93565374,  0.93757908,  0.93944862,  0.94126385,
        0.94302627,  0.94473732,  0.94639839,  0.94801087,  0.9495761,   0.95109539,
        0.95257001,  0.95400122,  0.95539023,  0.95673822,  0.95804636,  0.95931576,
        0.96054753,  0.96174273,  0.96290241,  0.96402758
    ]

    def tanhf_lut(self, x: int):
        if x > 2:
            return 1
        elif x <= -2:
            return -1
        else:
            index = 128 + 64 * x
            return self._tanh_lut_table[index]
