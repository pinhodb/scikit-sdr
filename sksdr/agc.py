"""
AGC algorithms.
"""
import logging

import numpy as np
import scipy.signal as signal

_log = logging.getLogger(__name__)

class AGC:

    r"""
    AGC based on a logarithmic scheme.

    The algorithm doesn't use a linear loop scheme since that has a significant drawback: The time constant of the loop is input signal level dependent, and is different depending on whether the input signal is increasing or decreasing. These properties drastically reduce the control over the system's time constant. To solve this problem, a logarithmic loop is adopted. This allows complete control of the AGC's time constant, increases its dynamic range and generally provides good performance for a variety of signal types. For the logarithmic AGC scheme, the feedback loop's time constant is dependent solely on the detector gain and so independent of the input signal level.

    The detector block is composed of a LPF to eliminate rapid gain changes. That filter can be a simple moving average filter, a CIC filter, or a more traditional LPF having a sinc-shaped impulse response. In the current implementation, a moving average filter is implemented, which computes the average power of the last :attr:`avg_len` samples. This power is then multiplied by the loop gain :math:`g(n)` and compared with the reference power :math:`A` (specified by :attr:`ref_power`) in natural log units, to produce the error signal :math:`e(n)`. This error signal is scaled by the detector gain :math:`K` (specified by :attr:`det_gain`) and passed to an integrator  which updates the loop gain :math:`g(n)`. Mathematically, the algorithm is summarized as:

    TODO equation

    where:

    * :math:`x(n)` is the input signal
    * :math:`y(n)` is the output signal
    * :math:`g(n)` is the loop gain, in Neper
    * :math:`D()` is the detector function
    * :math:`z(n)` is the detector output
    * :math:`e(n)` is the error signal
    * :math:`A` is the reference value, given by :attr:`ref_power`
    * :math:`K` is the detector gain, given by :attr:`det_gain`

    The detector function :math:`D(\ldots)` is implemented as a moving average filter:

    TODO equation

    where :math:`N` is the number of samples to average, given by :attr:`avg_len`.
    """

    def __init__(self, ref_power: float, max_gain: float, det_gain: float, avg_len: int):
        """
        :param ref_power: Desired output power
        :param max_gain: Upper limit on the loop gain (dB)
        :param det_gain: Detector gain
        :param avg_len: Length of moving average filter (samples)
        """
        self.ref_power = ref_power
        self.max_gain = max_gain
        self.det_gain = det_gain
        # Moving average filter
        self._avg_len = avg_len
        self._filter_coeffs = np.ones(self.avg_len) / self.avg_len
        self._filter_state = np.zeros(self.avg_len - 1)
        self._gain = 0.0 # Np (neper)

    @property
    def ref_power(self) -> float:
        """
        Desired output power.
        """
        return self._ref_power

    @ref_power.setter
    def ref_power(self, value: int):
        self._ref_power = value
        self._ref_power_ln = np.log(self.ref_power)

    @property
    def max_gain(self) -> float:
        """
        Upper limit on the loop gain (dB).
        """
        return self._max_gain

    @max_gain.setter
    def max_gain(self, value: float):
        self._max_gain = value
        self._max_gain_ln = np.log(10**(self.max_gain / 20)) # Np (neper)

    @property
    def det_gain(self) -> float:
        """
        Detector gain.
        """
        return self._det_gain

    @det_gain.setter
    def det_gain(self, value: float):
        self._det_gain = value

    @property
    def avg_len(self) -> int:
        """
        Length of moving average filter (samples).
        """
        return self._avg_len

    def __call__(self, inp: np.ndarray, out: np.ndarray, err: np.ndarray = None) -> int:
        """
        The main work function.

        :param inp: Input signal
        :param out: Output signal
        :param err: Error signal
        :return: 0 if OK, error code otherwise
        """
        inp_pow, self._filter_state = signal.lfilter(self._filter_coeffs, 1, abs(inp)**2, zi=self._filter_state)
        inp_pow_ln = np.log(inp_pow)

        for i, v in enumerate(inp):
            out[i] = v * np.exp(self._gain)
            # z is the detector output. Derivation:
            # z = inp_pow[i] * exp(gain)^2
            # z_ln = ln(z) = inp_pow_ln[i] + ln(exp(gain)^2) = inp_pow_ln[i] + 2*gain
            z_ln = inp_pow_ln[i] + 2 * self._gain
            error = self._ref_power_ln - z_ln
            if err is not None:
                err[i] = error
            self._gain = min(self._gain + self.det_gain * error, self._max_gain_ln)
            # _log.debug('AGC loop: err=%f, gain=%f, out=%s', err, self._gain, out[i].__format__('.6f'))
        return 0

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.

        :return: A string representing the object and its properties
        """
        args = 'ref_power={}, max_gain={}, det_gain={}, avg_len={}'.format(self.ref_power, self.max_gain, self.det_gain, self.avg_len)
        return '{}({})'.format(self.__class__.__name__, args)
