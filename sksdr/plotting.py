import logging

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
from numpy.fft import fft, fftfreq, fftshift

_log = logging.getLogger(__name__)

def time_plot(data, data_label, ts, title, xlabel='Time (s)', ylabel='Amplitude', fig=None, gs=None):
    fig = fig if fig else plt.figure()
    ax = fig.add_subplot(gs) if gs else fig.add_subplot()
    ax.xaxis.tick_top()
    #ax.xaxis.set_label_position('top')
    for i, d in enumerate(data):
        ax.plot(np.arange(len(data[i])) * ts[i], d, label=data_label[i], marker='.')
        # TODO: Add more than 1 secondary axis
        secax = ax.secondary_xaxis('bottom', functions=(lambda x: x/ts[i], lambda x: x/ts[i]))
        secax.set_xlabel('Sample')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if any(x for x in data_label):
        ax.legend()
    ax.grid()
    ax.set_title(title)
    return fig

def scatter_plot(data, title, xlabel='Re', ylabel='Im', xlim=[-1.5, 1.5], ylim=[-1.5, 1.5], fig=None, gs=None):
    fig = fig if fig else plt.figure()
    ax = fig.add_subplot(gs) if gs else fig.add_subplot()
    ax.scatter(data.real, data.imag)
    ax.axis('square')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid()
    return fig

def psd_plot(data, fs, title, xlabel='Frequency (Hz)', ylabel='Magnitude (dB)', fig=None, gs=None):
    fig = fig if fig else plt.figure()
    ax = fig.add_subplot(gs) if gs else fig.add_subplot()
    fourier = fft(data)
    freqs = fftfreq(len(data)) * fs
    plt.plot(fftshift(freqs), fftshift(20 * np.log10(np.abs(fourier))))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid()
    return fig

def freqz_plot(b, a, fs, plot_type, title, xlabel='Frequency (Hz)', ylabel=None, fig=None, gs=None):
    w, h = signal.freqz(b, a, fs=fs)
    fig = fig if fig else plt.figure()
    ax = fig.add_subplot(gs) if gs else fig.add_subplot()
    if plot_type == 'mag':
        ax.plot(w, np.abs(h))
        ax.set_ylabel(ylabel if ylabel else 'Magnitude')
    elif plot_type == 'mag_db':
        ax.plot(w, 20 * np.log10(np.abs(h)))
        ax.set_ylabel(ylabel if ylabel else 'Magnitude (dB)')
    else:
        ax.plot(w, np.angle(h, True))
        ax.set_ylabel(ylabel if ylabel else 'Phase (degrees)')
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid()
    return fig
