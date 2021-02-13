#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: PSK Transmitter
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
import pmt
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import epy_block_0
import grsksdr
import numpy as np
import osmosdr
import time
import sksdr

from gnuradio import qtgui

class psk_tx_mine(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "PSK Transmitter")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("PSK Transmitter")
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

        self.settings = Qt.QSettings("GNU Radio", "psk_tx_mine")

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
        self.txt_size = txt_size = 11
        self.msg_size = msg_size = txt_size + 4
        self.modulation = modulation = sksdr.QPSK
        self.frame_size_bits = frame_size_bits = 250
        self.fec_ntotal = fec_ntotal = 4
        self.fec_ndata = fec_ndata = 4
        self.upsampling = upsampling = 4
        self.payload_size_bits = payload_size_bits = 224
        self.msg_size_bits = msg_size_bits = msg_size * 8
        self.frame_size_symbols = frame_size_symbols = int(frame_size_bits / modulation.bits_per_symbol)
        self.fec_rate = fec_rate = fec_ntotal / fec_ndata
        self.samp_rate = samp_rate = 1.024e6
        self.rrc_coeffs = rrc_coeffs = sksdr.rrc(upsampling, 0.5, 10)
        self.rf_gain = rf_gain = 40
        self.preamble = preamble = np.repeat(sksdr.UNIPOLAR_BARKER_SEQ[13], 2)
        self.payload_fec_size_bits = payload_fec_size_bits = int(payload_size_bits * fec_rate)
        self.mod_phase_offset = mod_phase_offset = np.pi / 4
        self.mod_labels = mod_labels = [0, 1, 3, 2]
        self.mod_amplitude = mod_amplitude = 1
        self.freq_correction = freq_correction = 0
        self.freq = freq = 220e6
        self.frame_size_samples = frame_size_samples = frame_size_symbols * upsampling
        self.frac_resampling = frac_resampling = 1/5
        self.fill_size_bits = fill_size_bits = payload_size_bits - msg_size_bits

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_time_sink_x_1 = qtgui.time_sink_c(
            1024, #size
            samp_rate, #samp_rate
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
        markers = [0, 0, -1, -1, -1,
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
            samp_rate, #bw
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
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + "driver=rtlsdr"
        )
        self.osmosdr_sink_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(10, 0)
        self.osmosdr_sink_0.set_if_gain(20, 0)
        self.osmosdr_sink_0.set_bb_gain(20, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.mmse_resampler_xx_0 = filter.mmse_resampler_cc(0, frac_resampling)
        self.grsksdr_scrambler_0 = grsksdr.scrambler([1, 1, 1,  0, 1], [0, 1, 1, 0])
        self.grsksdr_psk_mod_0 = grsksdr.psk_mod('sksdr.QPSK', mod_labels, mod_amplitude, mod_phase_offset)
        self.grsksdr_fir_interpolator_0 = grsksdr.fir_interpolator(upsampling, rrc_coeffs)
        self.epy_block_0 = epy_block_0.blk(txt_size=txt_size, payload_size=payload_size_bits)
        self.blocks_vector_source_x_0 = blocks.vector_source_b(preamble, True, 1, [])
        self.blocks_stream_mux_0 = blocks.stream_mux(gr.sizeof_char*1, [len(preamble), payload_fec_size_bits])
        self.blocks_file_source_0_0 = blocks.file_source(gr.sizeof_char*1, 'msg.txt', True, 0, 0)
        self.blocks_file_source_0_0.set_begin_tag(pmt.PMT_NIL)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0_0, 0), (self.epy_block_0, 0))
        self.connect((self.blocks_stream_mux_0, 0), (self.grsksdr_psk_mod_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_stream_mux_0, 0))
        self.connect((self.epy_block_0, 0), (self.grsksdr_scrambler_0, 0))
        self.connect((self.grsksdr_fir_interpolator_0, 0), (self.mmse_resampler_xx_0, 0))
        self.connect((self.grsksdr_fir_interpolator_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.grsksdr_fir_interpolator_0, 0), (self.qtgui_time_sink_x_1, 0))
        self.connect((self.grsksdr_psk_mod_0, 0), (self.grsksdr_fir_interpolator_0, 0))
        self.connect((self.grsksdr_scrambler_0, 0), (self.blocks_stream_mux_0, 1))
        self.connect((self.mmse_resampler_xx_0, 0), (self.osmosdr_sink_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "psk_tx_mine")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_txt_size(self):
        return self.txt_size

    def set_txt_size(self, txt_size):
        self.txt_size = txt_size
        self.set_msg_size(self.txt_size + 4)
        self.epy_block_0.txt_size = self.txt_size

    def get_msg_size(self):
        return self.msg_size

    def set_msg_size(self, msg_size):
        self.msg_size = msg_size
        self.set_msg_size_bits(self.msg_size * 8)

    def get_modulation(self):
        return self.modulation

    def set_modulation(self, modulation):
        self.modulation = modulation

    def get_frame_size_bits(self):
        return self.frame_size_bits

    def set_frame_size_bits(self, frame_size_bits):
        self.frame_size_bits = frame_size_bits
        self.set_frame_size_symbols(int(self.frame_size_bits / modulation.bits_per_symbol))

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

    def get_upsampling(self):
        return self.upsampling

    def set_upsampling(self, upsampling):
        self.upsampling = upsampling
        self.set_frame_size_samples(self.frame_size_symbols * self.upsampling)
        self.set_rrc_coeffs(sksdr.rrc(self.upsampling, 0.5, 10))

    def get_payload_size_bits(self):
        return self.payload_size_bits

    def set_payload_size_bits(self, payload_size_bits):
        self.payload_size_bits = payload_size_bits
        self.set_fill_size_bits(self.payload_size_bits - self.msg_size_bits)
        self.set_payload_fec_size_bits(int(self.payload_size_bits * self.fec_rate))
        self.epy_block_0.payload_size = self.payload_size_bits

    def get_msg_size_bits(self):
        return self.msg_size_bits

    def set_msg_size_bits(self, msg_size_bits):
        self.msg_size_bits = msg_size_bits
        self.set_fill_size_bits(self.payload_size_bits - self.msg_size_bits)

    def get_frame_size_symbols(self):
        return self.frame_size_symbols

    def set_frame_size_symbols(self, frame_size_symbols):
        self.frame_size_symbols = frame_size_symbols
        self.set_frame_size_samples(self.frame_size_symbols * self.upsampling)

    def get_fec_rate(self):
        return self.fec_rate

    def set_fec_rate(self, fec_rate):
        self.fec_rate = fec_rate
        self.set_payload_fec_size_bits(int(self.payload_size_bits * self.fec_rate))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_1.set_samp_rate(self.samp_rate)

    def get_rrc_coeffs(self):
        return self.rrc_coeffs

    def set_rrc_coeffs(self, rrc_coeffs):
        self.rrc_coeffs = rrc_coeffs

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain

    def get_preamble(self):
        return self.preamble

    def set_preamble(self, preamble):
        self.preamble = preamble
        self.blocks_vector_source_x_0.set_data(self.preamble, [])

    def get_payload_fec_size_bits(self):
        return self.payload_fec_size_bits

    def set_payload_fec_size_bits(self, payload_fec_size_bits):
        self.payload_fec_size_bits = payload_fec_size_bits

    def get_mod_phase_offset(self):
        return self.mod_phase_offset

    def set_mod_phase_offset(self, mod_phase_offset):
        self.mod_phase_offset = mod_phase_offset

    def get_mod_labels(self):
        return self.mod_labels

    def set_mod_labels(self, mod_labels):
        self.mod_labels = mod_labels

    def get_mod_amplitude(self):
        return self.mod_amplitude

    def set_mod_amplitude(self, mod_amplitude):
        self.mod_amplitude = mod_amplitude

    def get_freq_correction(self):
        return self.freq_correction

    def set_freq_correction(self, freq_correction):
        self.freq_correction = freq_correction

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_sink_0.set_center_freq(self.freq, 0)

    def get_frame_size_samples(self):
        return self.frame_size_samples

    def set_frame_size_samples(self, frame_size_samples):
        self.frame_size_samples = frame_size_samples

    def get_frac_resampling(self):
        return self.frac_resampling

    def set_frac_resampling(self, frac_resampling):
        self.frac_resampling = frac_resampling
        self.mmse_resampler_xx_0.set_resamp_ratio(self.frac_resampling)

    def get_fill_size_bits(self):
        return self.fill_size_bits

    def set_fill_size_bits(self, fill_size_bits):
        self.fill_size_bits = fill_size_bits

def snipfcn_snippet_0(self):
    import logging
    logging.getLogger('grsksdr.hamming_encoder').setLevel(logging.DEBUG)


def snippets_main_after_init(tb):
    snipfcn_snippet_0(tb)




def main(top_block_cls=psk_tx_mine, options=None):

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
