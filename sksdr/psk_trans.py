import logging
from logging import DEBUG

import numpy as np

from .agc import AGC
from .channels import AWGNChannel
from .coarse_freq_comp import CoarseFrequencyComp
from .frame_sync import PreambleSync
from .freq_sync import PSKSync
from .impairments import PhaseFrequencyOffset, VariableFractionalDelay
from .interp_decim import FirDecimator, FirInterpolator
from .modulation import QPSK, PSKModulator
from .phase_offset_est import PhaseOffsetEst
from .pulses import rrc
from .scrambling import Descrambler, Scrambler
from .sequences import UNIPOLAR_BARKER_SEQ
from .symbol_sync import SymbolSync

_log = logging.getLogger(__name__)

class PSKTrans:
    def __init__(self, sample_rate=200.0e3, upsampling=4, downsampling=2, frame_size=100,
                 # Modulation
                 modulation=QPSK, mod_symbols=[0, 1, 3, 2], mod_amplitude=1.0, mod_phase_offset=np.pi/4,
                 # Scrambling
                 scrambler_poly=[1, 1, 1, 0, 1], scrambler_init_state=[0, 1, 1, 0],
                 # RRC filtering
                 rrc_rolloff=0.5, rrc_span=10,
                 # AGC
                 agc_ref_power=1/4, agc_max_gain=60.0, agc_det_gain=0.01, agc_avg_len=100, # agc_ref_power = 1/upsampling
                 # Coarse frequency compensation
                 coarse_freq_comp_res=25.0,
                 # Frequency synchronization
                 fsync_damp_factor=1.0, fsync_norm_loop_bw=0.01,
                 # Symbol timing synchronization
                 ssync_K=1.0, ssync_A=1/np.sqrt(2), ssync_damp_factor=1.0, ssync_norm_loop_bw=0.01,
                 # Frame synchronization
                 prb_det_thr=8.0,
                 # Channel settings
                 chan_snr=np.inf, chan_signal_power=None,
                 chan_delay_type='triangle', chan_delay_step=0.0, chan_max_delay=0.0,
                 chan_freq_offset=0.0, chan_phase_offset=0.0):

        # General settings
        self.sample_rate = sample_rate
        self.modulation = modulation
        self.mod_symbols = mod_symbols
        self.mod_amplitude = mod_amplitude
        self.mod_phase_offset = mod_phase_offset
        self.upsampling = upsampling
        self.downsampling = downsampling
        self.frame_size_symbols = frame_size # symbols
        self._frame_size_bits = self.frame_size_symbols * self.modulation.bits_per_symbol # bits
        self._frame_size_samples = self.frame_size_symbols * self.upsampling # samples
        self._rx_frame_size_samples = int(self._frame_size_samples / self.downsampling)
        self._rx_filter_sps = int(self.upsampling / self.downsampling)

        # Modulator
        self._psk = PSKModulator(self.modulation, self.mod_symbols, self.mod_amplitude, self.mod_phase_offset)

        # Scrambler
        self.scrambler_poly = scrambler_poly
        self.scrambler_init_state = scrambler_init_state
        self._scrambler = Scrambler(self.scrambler_poly, self.scrambler_init_state)

        # Descrambler
        self._descrambler = Descrambler(self.scrambler_poly, self.scrambler_init_state)

        # FIR interpolator with RRC coefficients
        self.rrc_rolloff = rrc_rolloff
        self.rrc_span = rrc_span # symbols
        self._rrc = rrc(self.upsampling, self.rrc_rolloff, self.rrc_span)
        self._interp = FirInterpolator(self.upsampling, self._rrc)

        # AGC
        self.agc_ref_power = agc_ref_power
        self.agc_max_gain = agc_max_gain # dB
        self.agc_det_gain = agc_det_gain
        self.agc_avg_len = agc_avg_len
        self._agc = AGC(self.agc_ref_power, self.agc_max_gain, self.agc_det_gain, self.agc_avg_len)

        # FIR decimator with RRC coefficients
        self._decim = FirDecimator(self.downsampling, self._rrc)

        # Coarse frequency compensator
        self.coarse_freq_comp_res = coarse_freq_comp_res
        self._cfc = CoarseFrequencyComp(self.modulation.order, self.sample_rate,
                                        self.coarse_freq_comp_res)

        # Frequency synchronizer
        self.fsync_damp_factor = fsync_damp_factor
        self.fsync_norm_loop_bw = fsync_norm_loop_bw
        self._fsync = PSKSync(self.modulation, self._rx_filter_sps, self.fsync_damp_factor, self.fsync_norm_loop_bw)

        # Symbol timing synchronizer
        self.ssync_damp_factor = ssync_damp_factor
        self.ssync_norm_loop_bw = ssync_norm_loop_bw
        self.ssync_K = ssync_K
        self.ssync_A = ssync_A
        self._ssync = SymbolSync(self.modulation, self._rx_filter_sps,
                                 self.ssync_damp_factor, self.ssync_norm_loop_bw, self.ssync_K, self.ssync_A)

        # Frame synchronizer
        self.prb_det_thr = prb_det_thr
        self._preamble = np.repeat(UNIPOLAR_BARKER_SEQ[13], 2)
        self._mod_preamble = self._psk.modulate(self._preamble)
        self._frame_sync = PreambleSync(self._mod_preamble, self.prb_det_thr, self.frame_size_symbols)

        # Phase offset estimator
        self._phase_off_est = PhaseOffsetEst(self._mod_preamble)

        # Channel settings
        self.chan_snr = chan_snr # dB
        self.chan_signal_power = chan_signal_power
        self._chan = AWGNChannel(self.chan_snr, self.chan_signal_power)

        # Variable fractional delay impairment
        self.chan_max_delay = chan_max_delay
        self.chan_delay_type = chan_delay_type
        self.chan_delay_step = chan_delay_step
        self.chan_delay_num_steps = 0 if self.chan_delay_step == 0.0 else self.chan_max_delay / self.chan_delay_step
        self._vfd = VariableFractionalDelay(self._frame_size_samples)

        # Phase/Frequency offset impairment
        self.chan_phase_offset = chan_phase_offset
        self.chan_freq_offset = chan_freq_offset
        self._pfo = PhaseFrequencyOffset(self.sample_rate, self.chan_freq_offset, self.chan_phase_offset)

    def transmit(self, msg):
        ret = dict()

        # Build frame bits
        ret['payload'] = unpack(msg, 8)
        ret['fill'] = np.random.randint(0, 1, self._frame_size_bits - len(self._preamble) - len(ret['payload']))
        ret['bits'] = np.hstack((ret['payload'], ret['fill'])) # TODO: Avoid array copy

        # Scramble bits
        ret['sbits'] = self._scrambler(ret['bits'])
        ret['final_bits'] = np.hstack((self._preamble, ret['sbits']))

        # Modulate symbols
        ret['symbols'] = self._psk.modulate(ret['final_bits'])

        # Upsample and pulse shaping filter
        ret['usymbols'], ret['frame'] = self._interp(ret['symbols'])
        return ret

    def channel(self, frame, count):
        # Variable fractional delay
        index = 0 if self.chan_delay_num_steps == 0 else count % (2 * self.chan_delay_num_steps)
        if index <= self.chan_delay_num_steps:
            delay = index * self.chan_delay_step
        else:
            delay = 2 * self.chan_max_delay - index * self.chan_delay_step
        vfd_frame = self._vfd(frame, delay)
        # Phase/frequency offset
        pfo_frame, _ = self._pfo(vfd_frame)
        return self._chan(pfo_frame)

    def receive(self, frame, tx_msg=None):
        ret = dict()

        # AGC
        ret['agc_frame'], ret['agc_error'] = self._agc(frame)
        _log.log(DEBUG-1, ret['agc_frame'])

        # Matched filter and downsample
        _, ret['rx_filter_down_frame'] = self._decim(ret['agc_frame'])
        _log.log(DEBUG-1, ret['rx_filter_down_frame'])

        # Frequency compensation
        ret['cfc_frame'], ret['cfc_spectrum'], ret['cfc_offset'] = self._cfc(ret['rx_filter_down_frame'])
        _log.log(DEBUG-1, ret['cfc_frame'])

        # Carrier synchronizer
        ret['fsync_frame'], ret['fsync_estimate'] = self._fsync(ret['cfc_frame'])
        _log.log(DEBUG-1, ret['fsync_frame'])

        # Symbol synchronizer
        ret['ssync_frame'], _, _ = self._ssync(ret['fsync_frame'])
        _log.log(DEBUG-1, ret['ssync_frame'])

        # Frame synchronizer
        ret['frame_sync_frame'], ret['prb_end_idxs'], ret['valid'] = self._frame_sync(ret['ssync_frame'])
        _log.log(DEBUG-1, ret['frame_sync_frame'])

        if ret['valid']:
            # Phase ambiguity correction
            ret['phase_amb_frame'] = self._phase_off_est(ret['frame_sync_frame'])
            _log.log(DEBUG-1, ret['phase_amb_frame'])

            # Demodulate symbols
            ret['rx_sbits'] = self._psk.demodulate(ret['phase_amb_frame'])
            _log.log(DEBUG-1, ret['rx_sbits'])

            # Descramble bits after the preamble
            ret['payload'] = self._descrambler(ret['rx_sbits'][len(self._preamble):])
            _log.log(DEBUG-1, ret['payload'])

            # Compute BER
            if tx_msg is None:
                rxbits = ret['payload']
            else:
                txbits = unpack(tx_msg, 8)
                rxbits = ret['payload'][:len(tx_msg) * 8]
                ret['BER'] = [np.count_nonzero(rxbits != txbits), len(rxbits)]

            # Convert the payload to ASCII
            ret['rx_msg'] = binlist2x(rxbits, 8)
            ret['rx_msg_ascii'] = [chr(x) for x in ret['rx_msg']]
            _log.debug(ret['rx_msg_ascii'])

        else:
            ret['phase_amb_frame'], ret['rx_sbits'], ret['payload'], ret['rx_msg'] = [np.zeros(1)] * 4
        return ret
