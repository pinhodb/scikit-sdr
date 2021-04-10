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

from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from stream_demux import stream_demux_swig
import epy_block_0
import grsksdr
import numpy as np
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
        self.preamble_and_padding = preamble_and_padding = np.array([255, 195, 204, 192], dtype=np.uint8)
        self.payload_size = payload_size = 28
        self.frame_size = frame_size = len(preamble_and_padding) + payload_size
        self.modulation = modulation = sksdr.QPSK
        self.frame_size_bits = frame_size_bits = frame_size * 8
        self.upsampling = upsampling = 4
        self.frame_size_symbols = frame_size_symbols = frame_size_bits // modulation.bits_per_symbol
        self.frame_size_samples_before_downsampling = frame_size_samples_before_downsampling = frame_size_symbols * upsampling
        self.downsampling = downsampling = 2
        self.samp_rate = samp_rate = 1.024e6
        self.rx_filter_sps = rx_filter_sps = int(upsampling / downsampling)
        self.rrc_coeffs = rrc_coeffs = sksdr.rrc(upsampling, 0.5, 10)
        self.msg_size = msg_size = 11 + 4
        self.mod_preamble = mod_preamble = np.array([-0.7071067811865477-0.7071067811865475j, -0.7071067811865477-0.7071067811865475j, -0.7071067811865477-0.7071067811865475j, -0.7071067811865477-0.7071067811865475j, -0.7071067811865477-0.7071067811865475j, 0.7071067811865476+0.7071067811865475j, 0.7071067811865476+0.7071067811865475j, -0.7071067811865477-0.7071067811865475j, -0.7071067811865477-0.7071067811865475j, 0.7071067811865476+0.7071067811865475j, -0.7071067811865477-0.7071067811865475j, 0.7071067811865476+0.7071067811865475j, -0.7071067811865477-0.7071067811865475j, 0.7071067811865476+0.7071067811865475j, 0.7071067811865476+0.7071067811865475j, 0.7071067811865476+0.7071067811865475j])
        self.mod_phase_offset = mod_phase_offset = np.pi / 4
        self.mod_labels = mod_labels = [0, 1, 3, 2]
        self.mod_amplitude = mod_amplitude = 1
        self.freq_correction = freq_correction = 40
        self.freq = freq = 220e6
        self.frame_size_samples_after_downsampling = frame_size_samples_after_downsampling = frame_size_samples_before_downsampling // downsampling
        self.frac_resampling = frac_resampling = 5

        ##################################################
        # Blocks
        ##################################################
        self.stream_demux_stream_demux_0 = stream_demux_swig.stream_demux(gr.sizeof_char*1, [len(preamble_and_padding), payload_size])
        self.grsksdr_symbol_sync_0 = grsksdr.symbol_sync('sksdr.QPSK', rx_filter_sps, 1, 0.01, 1, 1/np.sqrt(2))
        self.grsksdr_psk_demod_0 = grsksdr.psk_demod('sksdr.QPSK', mod_labels, mod_amplitude, mod_phase_offset)
        self.grsksdr_phase_offset_est_0 = grsksdr.phase_offset_est(mod_preamble, frame_size_symbols)
        self.grsksdr_freq_sync_0 = grsksdr.freq_sync('sksdr.QPSK', rx_filter_sps, 1, 0.01)
        self.grsksdr_frame_sync_0 = grsksdr.frame_sync(mod_preamble, 8.0, frame_size_symbols)
        self.grsksdr_fir_decimator_0 = grsksdr.fir_decimator(downsampling, rrc_coeffs)
        self.grsksdr_descrambler_0 = grsksdr.descrambler([1, 0, 1, 1, 0, 1, 0 ,1], [0, 3, 2, 2, 5, 1, 7])
        self.grsksdr_coarse_freq_comp_0 = grsksdr.coarse_freq_comp(modulation.order, samp_rate/2, 1, frame_size_samples_after_downsampling)
        self.grsksdr_agc_1 = grsksdr.agc(0.25, 60, 0.01, frame_size_samples_before_downsampling)
        self.epy_block_0 = epy_block_0.blk(message_size=msg_size, payload_size=payload_size)
        self.blocks_unpacked_to_packed_xx_0 = blocks.unpacked_to_packed_bb(modulation.bits_per_symbol, gr.GR_MSB_FIRST)
        self.blocks_throttle_1 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_null_sink_0_0_1 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_null_sink_0_0_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_null_sink_0_0 = blocks.null_sink(gr.sizeof_char*1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_char*1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, 'test.iq', True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.blocks_throttle_1, 0))
        self.connect((self.blocks_throttle_1, 0), (self.grsksdr_agc_1, 0))
        self.connect((self.blocks_unpacked_to_packed_xx_0, 0), (self.stream_demux_stream_demux_0, 0))
        self.connect((self.epy_block_0, 0), (self.blocks_null_sink_0_0, 0))
        self.connect((self.grsksdr_agc_1, 0), (self.grsksdr_fir_decimator_0, 0))
        self.connect((self.grsksdr_coarse_freq_comp_0, 0), (self.grsksdr_freq_sync_0, 0))
        self.connect((self.grsksdr_descrambler_0, 0), (self.epy_block_0, 0))
        self.connect((self.grsksdr_fir_decimator_0, 0), (self.grsksdr_coarse_freq_comp_0, 0))
        self.connect((self.grsksdr_frame_sync_0, 0), (self.blocks_null_sink_0_0_0, 0))
        self.connect((self.grsksdr_frame_sync_0, 0), (self.grsksdr_phase_offset_est_0, 0))
        self.connect((self.grsksdr_freq_sync_0, 0), (self.grsksdr_symbol_sync_0, 0))
        self.connect((self.grsksdr_phase_offset_est_0, 0), (self.grsksdr_psk_demod_0, 0))
        self.connect((self.grsksdr_psk_demod_0, 0), (self.blocks_unpacked_to_packed_xx_0, 0))
        self.connect((self.grsksdr_symbol_sync_0, 0), (self.blocks_null_sink_0_0_1, 0))
        self.connect((self.grsksdr_symbol_sync_0, 0), (self.grsksdr_frame_sync_0, 0))
        self.connect((self.stream_demux_stream_demux_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.stream_demux_stream_demux_0, 1), (self.grsksdr_descrambler_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "psk_rx")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_preamble_and_padding(self):
        return self.preamble_and_padding

    def set_preamble_and_padding(self, preamble_and_padding):
        self.preamble_and_padding = preamble_and_padding
        self.set_frame_size(len(self.preamble_and_padding) + self.payload_size)

    def get_payload_size(self):
        return self.payload_size

    def set_payload_size(self, payload_size):
        self.payload_size = payload_size
        self.set_frame_size(len(self.preamble_and_padding) + self.payload_size)
        self.epy_block_0.payload_size = self.payload_size

    def get_frame_size(self):
        return self.frame_size

    def set_frame_size(self, frame_size):
        self.frame_size = frame_size
        self.set_frame_size_bits(self.frame_size * 8)

    def get_modulation(self):
        return self.modulation

    def set_modulation(self, modulation):
        self.modulation = modulation

    def get_frame_size_bits(self):
        return self.frame_size_bits

    def set_frame_size_bits(self, frame_size_bits):
        self.frame_size_bits = frame_size_bits
        self.set_frame_size_symbols(self.frame_size_bits // modulation.bits_per_symbol)

    def get_upsampling(self):
        return self.upsampling

    def set_upsampling(self, upsampling):
        self.upsampling = upsampling
        self.set_frame_size_samples_before_downsampling(self.frame_size_symbols * self.upsampling)
        self.set_rrc_coeffs(sksdr.rrc(self.upsampling, 0.5, 10))
        self.set_rx_filter_sps(int(self.upsampling / self.downsampling))

    def get_frame_size_symbols(self):
        return self.frame_size_symbols

    def set_frame_size_symbols(self, frame_size_symbols):
        self.frame_size_symbols = frame_size_symbols
        self.set_frame_size_samples_before_downsampling(self.frame_size_symbols * self.upsampling)

    def get_frame_size_samples_before_downsampling(self):
        return self.frame_size_samples_before_downsampling

    def set_frame_size_samples_before_downsampling(self, frame_size_samples_before_downsampling):
        self.frame_size_samples_before_downsampling = frame_size_samples_before_downsampling
        self.set_frame_size_samples_after_downsampling(self.frame_size_samples_before_downsampling // self.downsampling)

    def get_downsampling(self):
        return self.downsampling

    def set_downsampling(self, downsampling):
        self.downsampling = downsampling
        self.set_frame_size_samples_after_downsampling(self.frame_size_samples_before_downsampling // self.downsampling)
        self.set_rx_filter_sps(int(self.upsampling / self.downsampling))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_1.set_sample_rate(self.samp_rate)

    def get_rx_filter_sps(self):
        return self.rx_filter_sps

    def set_rx_filter_sps(self, rx_filter_sps):
        self.rx_filter_sps = rx_filter_sps

    def get_rrc_coeffs(self):
        return self.rrc_coeffs

    def set_rrc_coeffs(self, rrc_coeffs):
        self.rrc_coeffs = rrc_coeffs

    def get_msg_size(self):
        return self.msg_size

    def set_msg_size(self, msg_size):
        self.msg_size = msg_size
        self.epy_block_0.message_size = self.msg_size

    def get_mod_preamble(self):
        return self.mod_preamble

    def set_mod_preamble(self, mod_preamble):
        self.mod_preamble = mod_preamble

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

    def get_frame_size_samples_after_downsampling(self):
        return self.frame_size_samples_after_downsampling

    def set_frame_size_samples_after_downsampling(self, frame_size_samples_after_downsampling):
        self.frame_size_samples_after_downsampling = frame_size_samples_after_downsampling

    def get_frac_resampling(self):
        return self.frac_resampling

    def set_frac_resampling(self, frac_resampling):
        self.frac_resampling = frac_resampling

def snipfcn_snippet_0(self):
    import logging
    logging.getLogger('grsksdr.frame_sync').setLevel(logging.DEBUG-1)
    logging.getLogger('grsksdr.phase_offset_est').setLevel(logging.DEBUG)
    logging.getLogger('grsksdr.descramber').setLevel(logging.DEBUG)
    logging.getLogger('grsksdr.hamming_decoder').setLevel(logging.DEBUG)

    #self.psk = sksdr.PSKModulator.from_modulation(self.modulation, self.mod_labels, self.mod_amplitude, self.mod_phase_offset)
    #self.psk.modulate(self.preamble_and_padding, self.mod_preamble)
    #print(self.mod_preamble)


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
