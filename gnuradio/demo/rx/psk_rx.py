#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: PSK Receiver
# Author: david
# GNU Radio version: 3.8.2.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from stream_demux import stream_demux_swig
import epy_block_0
import grsksdr
import numpy as np
import osmosdr
import time
import sksdr

from gnuradio import qtgui

class psk_rx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "PSK Receiver")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("PSK Receiver")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "psk_rx")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.modulation = modulation = sksdr.QPSK
        self.frame_size_bits = frame_size_bits = 250
        self.upsampling = upsampling = 4
        self.msg_size = msg_size = 15
        self.frame_size_symbols = frame_size_symbols = int(frame_size_bits / modulation.bits_per_symbol)
        self.fec_ntotal = fec_ntotal = 4
        self.fec_ndata = fec_ndata = 4
        self.payload_size_bits = payload_size_bits = 224
        self.msg_size_bits = msg_size_bits = msg_size * 8
        self.mod_phase_offset = mod_phase_offset = np.pi / 4
        self.mod_labels = mod_labels = [0, 1, 3, 2]
        self.mod_amplitude = mod_amplitude = 1
        self.frame_size_samples = frame_size_samples = frame_size_symbols * upsampling
        self.fec_rate = fec_rate = fec_ntotal / fec_ndata
        self.downsampling = downsampling = 2
        self.samp_rate = samp_rate = 1.024e6
        self.rx_frame_size_samples = rx_frame_size_samples = int(frame_size_samples / downsampling)
        self.rx_filter_sps = rx_filter_sps = int(upsampling / downsampling)
        self.rrc_coeffs = rrc_coeffs = sksdr.rrc(upsampling, 0.5, 10)
        self.preamble = preamble = np.repeat(sksdr.UNIPOLAR_BARKER_SEQ[13], 2)
        self.payload_fec_size_bits = payload_fec_size_bits = int(payload_size_bits * fec_rate)
        self.mod_preamble = mod_preamble = sksdr.PSKModulator(modulation, mod_labels, mod_amplitude, mod_phase_offset).modulate(np.repeat(sksdr.UNIPOLAR_BARKER_SEQ[13], 2))
        self.freq_correction = freq_correction = 40
        self.freq = freq = 220e6
        self.frac_resampling = frac_resampling = 5
        self.fill_size_bits = fill_size_bits = payload_size_bits - msg_size_bits

        ##################################################
        # Blocks
        ##################################################
        self.stream_demux_stream_demux_0 = stream_demux_swig.stream_demux(gr.sizeof_char*1, [len(preamble), payload_fec_size_bits])
        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(freq, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(10, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna('', 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
        self.qtgui_time_sink_x_1 = qtgui.time_sink_c(
            1024, #size
            samp_rate/frac_resampling, #samp_rate
            "", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_1.set_update_time(0.10)
        self.qtgui_time_sink_x_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_1.enable_tags(True)
        self.qtgui_time_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1.enable_autoscale(False)
        self.qtgui_time_sink_x_1.enable_grid(False)
        self.qtgui_time_sink_x_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_1.enable_control_panel(False)
        self.qtgui_time_sink_x_1.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_1.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_1.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_win = sip.wrapinstance(self.qtgui_time_sink_x_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_1_win)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate/frac_resampling, #bw
            "", #name
            1
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.mmse_resampler_xx_0 = filter.mmse_resampler_cc(0, frac_resampling)
        self.grsksdr_symbol_sync_0 = grsksdr.symbol_sync('sksdr.QPSK', rx_filter_sps, 1, 0.01, 1, 1/np.sqrt(2))
        self.grsksdr_psk_demod_0 = grsksdr.psk_demod('sksdr.QPSK', mod_labels, mod_amplitude, mod_phase_offset)
        self.grsksdr_phase_offset_est_0 = grsksdr.phase_offset_est(mod_preamble, frame_size_symbols)
        self.grsksdr_freq_sync_0 = grsksdr.freq_sync('sksdr.QPSK', rx_filter_sps, 1, 0.01)
        self.grsksdr_frame_sync_0 = grsksdr.frame_sync(mod_preamble, 8.0, frame_size_symbols)
        self.grsksdr_fir_decimator_0 = grsksdr.fir_decimator(downsampling, rrc_coeffs)
        self.grsksdr_descrambler_0 = grsksdr.descrambler([1, 1, 1, 0, 1], [0, 1, 1, 0])
        self.grsksdr_coarse_freq_comp_0 = grsksdr.coarse_freq_comp(modulation.order, samp_rate/frac_resampling, 1, rx_frame_size_samples)
        self.grsksdr_agc_1 = grsksdr.agc(0.25, 60, 0.01, frame_size_samples)
        self.epy_block_0 = epy_block_0.blk(message_size=msg_size, payload_size_bits=payload_size_bits)
        self.blocks_null_sink_0_0_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_null_sink_0_0 = blocks.null_sink(gr.sizeof_char*1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_char*1)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.epy_block_0, 0), (self.blocks_null_sink_0_0, 0))
        self.connect((self.grsksdr_agc_1, 0), (self.grsksdr_fir_decimator_0, 0))
        self.connect((self.grsksdr_coarse_freq_comp_0, 0), (self.grsksdr_freq_sync_0, 0))
        self.connect((self.grsksdr_coarse_freq_comp_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.grsksdr_coarse_freq_comp_0, 0), (self.qtgui_time_sink_x_1, 0))
        self.connect((self.grsksdr_descrambler_0, 0), (self.epy_block_0, 0))
        self.connect((self.grsksdr_fir_decimator_0, 0), (self.grsksdr_coarse_freq_comp_0, 0))
        self.connect((self.grsksdr_frame_sync_0, 0), (self.blocks_null_sink_0_0_0, 0))
        self.connect((self.grsksdr_frame_sync_0, 0), (self.grsksdr_phase_offset_est_0, 0))
        self.connect((self.grsksdr_freq_sync_0, 0), (self.grsksdr_symbol_sync_0, 0))
        self.connect((self.grsksdr_phase_offset_est_0, 0), (self.grsksdr_psk_demod_0, 0))
        self.connect((self.grsksdr_psk_demod_0, 0), (self.stream_demux_stream_demux_0, 0))
        self.connect((self.grsksdr_symbol_sync_0, 0), (self.grsksdr_frame_sync_0, 0))
        self.connect((self.mmse_resampler_xx_0, 0), (self.grsksdr_agc_1, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.mmse_resampler_xx_0, 0))
        self.connect((self.stream_demux_stream_demux_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.stream_demux_stream_demux_0, 1), (self.grsksdr_descrambler_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "psk_rx")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_modulation(self):
        return self.modulation

    def set_modulation(self, modulation):
        self.modulation = modulation
        self.set_mod_preamble(sksdr.PSKModulator(self.modulation, self.mod_labels, self.mod_amplitude, self.mod_phase_offset).modulate(np.repeat(sksdr.UNIPOLAR_BARKER_SEQ[13], 2)))

    def get_frame_size_bits(self):
        return self.frame_size_bits

    def set_frame_size_bits(self, frame_size_bits):
        self.frame_size_bits = frame_size_bits
        self.set_frame_size_symbols(int(self.frame_size_bits / modulation.bits_per_symbol))

    def get_upsampling(self):
        return self.upsampling

    def set_upsampling(self, upsampling):
        self.upsampling = upsampling
        self.set_frame_size_samples(self.frame_size_symbols * self.upsampling)
        self.set_rrc_coeffs(sksdr.rrc(self.upsampling, 0.5, 10))
        self.set_rx_filter_sps(int(self.upsampling / self.downsampling))

    def get_msg_size(self):
        return self.msg_size

    def set_msg_size(self, msg_size):
        self.msg_size = msg_size
        self.set_msg_size_bits(self.msg_size * 8)
        self.epy_block_0.message_size = self.msg_size

    def get_frame_size_symbols(self):
        return self.frame_size_symbols

    def set_frame_size_symbols(self, frame_size_symbols):
        self.frame_size_symbols = frame_size_symbols
        self.set_frame_size_samples(self.frame_size_symbols * self.upsampling)

    def get_fec_ntotal(self):
        return self.fec_ntotal

    def set_fec_ntotal(self, fec_ntotal):
        self.fec_ntotal = fec_ntotal
        self.set_fec_rate(self.fec_ntotal / self.fec_ndata)

    def get_fec_ndata(self):
        return self.fec_ndata

    def set_fec_ndata(self, fec_ndata):
        self.fec_ndata = fec_ndata
        self.set_fec_rate(self.fec_ntotal / self.fec_ndata)

    def get_payload_size_bits(self):
        return self.payload_size_bits

    def set_payload_size_bits(self, payload_size_bits):
        self.payload_size_bits = payload_size_bits
        self.set_fill_size_bits(self.payload_size_bits - self.msg_size_bits)
        self.set_payload_fec_size_bits(int(self.payload_size_bits * self.fec_rate))
        self.epy_block_0.payload_size_bits = self.payload_size_bits

    def get_msg_size_bits(self):
        return self.msg_size_bits

    def set_msg_size_bits(self, msg_size_bits):
        self.msg_size_bits = msg_size_bits
        self.set_fill_size_bits(self.payload_size_bits - self.msg_size_bits)

    def get_mod_phase_offset(self):
        return self.mod_phase_offset

    def set_mod_phase_offset(self, mod_phase_offset):
        self.mod_phase_offset = mod_phase_offset
        self.set_mod_preamble(sksdr.PSKModulator(self.modulation, self.mod_labels, self.mod_amplitude, self.mod_phase_offset).modulate(np.repeat(sksdr.UNIPOLAR_BARKER_SEQ[13], 2)))

    def get_mod_labels(self):
        return self.mod_labels

    def set_mod_labels(self, mod_labels):
        self.mod_labels = mod_labels
        self.set_mod_preamble(sksdr.PSKModulator(self.modulation, self.mod_labels, self.mod_amplitude, self.mod_phase_offset).modulate(np.repeat(sksdr.UNIPOLAR_BARKER_SEQ[13], 2)))

    def get_mod_amplitude(self):
        return self.mod_amplitude

    def set_mod_amplitude(self, mod_amplitude):
        self.mod_amplitude = mod_amplitude
        self.set_mod_preamble(sksdr.PSKModulator(self.modulation, self.mod_labels, self.mod_amplitude, self.mod_phase_offset).modulate(np.repeat(sksdr.UNIPOLAR_BARKER_SEQ[13], 2)))

    def get_frame_size_samples(self):
        return self.frame_size_samples

    def set_frame_size_samples(self, frame_size_samples):
        self.frame_size_samples = frame_size_samples
        self.set_rx_frame_size_samples(int(self.frame_size_samples / self.downsampling))

    def get_fec_rate(self):
        return self.fec_rate

    def set_fec_rate(self, fec_rate):
        self.fec_rate = fec_rate
        self.set_payload_fec_size_bits(int(self.payload_size_bits * self.fec_rate))

    def get_downsampling(self):
        return self.downsampling

    def set_downsampling(self, downsampling):
        self.downsampling = downsampling
        self.set_rx_filter_sps(int(self.upsampling / self.downsampling))
        self.set_rx_frame_size_samples(int(self.frame_size_samples / self.downsampling))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate/self.frac_resampling)
        self.qtgui_time_sink_x_1.set_samp_rate(self.samp_rate/self.frac_resampling)
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)

    def get_rx_frame_size_samples(self):
        return self.rx_frame_size_samples

    def set_rx_frame_size_samples(self, rx_frame_size_samples):
        self.rx_frame_size_samples = rx_frame_size_samples

    def get_rx_filter_sps(self):
        return self.rx_filter_sps

    def set_rx_filter_sps(self, rx_filter_sps):
        self.rx_filter_sps = rx_filter_sps

    def get_rrc_coeffs(self):
        return self.rrc_coeffs

    def set_rrc_coeffs(self, rrc_coeffs):
        self.rrc_coeffs = rrc_coeffs

    def get_preamble(self):
        return self.preamble

    def set_preamble(self, preamble):
        self.preamble = preamble

    def get_payload_fec_size_bits(self):
        return self.payload_fec_size_bits

    def set_payload_fec_size_bits(self, payload_fec_size_bits):
        self.payload_fec_size_bits = payload_fec_size_bits

    def get_mod_preamble(self):
        return self.mod_preamble

    def set_mod_preamble(self, mod_preamble):
        self.mod_preamble = mod_preamble

    def get_freq_correction(self):
        return self.freq_correction

    def set_freq_correction(self, freq_correction):
        self.freq_correction = freq_correction

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.rtlsdr_source_0.set_center_freq(self.freq, 0)

    def get_frac_resampling(self):
        return self.frac_resampling

    def set_frac_resampling(self, frac_resampling):
        self.frac_resampling = frac_resampling
        self.mmse_resampler_xx_0.set_resamp_ratio(self.frac_resampling)
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate/self.frac_resampling)
        self.qtgui_time_sink_x_1.set_samp_rate(self.samp_rate/self.frac_resampling)

    def get_fill_size_bits(self):
        return self.fill_size_bits

    def set_fill_size_bits(self, fill_size_bits):
        self.fill_size_bits = fill_size_bits

def snipfcn_snippet_0(self):
    import logging
    logging.getLogger('grsksdr.frame_sync').setLevel(logging.DEBUG-1)
    logging.getLogger('grsksdr.phase_offset_est').setLevel(logging.DEBUG)
    logging.getLogger('grsksdr.descramber').setLevel(logging.DEBUG)
    logging.getLogger('grsksdr.hamming_decoder').setLevel(logging.DEBUG)


def snippets_main_after_init(tb):
    snipfcn_snippet_0(tb)




def main(top_block_cls=psk_rx, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    snippets_main_after_init(tb)
    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
