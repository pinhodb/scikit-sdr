import logging

import sksdr

_log = logging.getLogger(__name__)

def test_psk_trans():
    msgs = ['Hello World {:03d}'.format(i) for i in range(100)]

    # BPSK
    rx_msg_idx = 0
    trans = sksdr.PSKTrans(frame_size=200, modulation=sksdr.BPSK, mod_symbols=[0, 1], chan_snr=15, chan_delay_step=0.05,
                           chan_max_delay=8, chan_freq_offset=5e3, chan_phase_offset=47)
    for i, m in enumerate(msgs):
        tx_ret = trans.transmit(m)
        chan_frame = trans.channel(tx_ret['frame'], i)
        rx_ret = trans.receive(chan_frame, msgs[rx_msg_idx])
        if rx_ret['valid']:
            rx_msg_idx += 1
    assert rx_msg_idx == 99

    # QPSK
    rx_msg_idx = 0
    trans = sksdr.PSKTrans(chan_snr=15, chan_delay_step=0.05, chan_max_delay=8, chan_freq_offset=5e3,
                           chan_phase_offset=47)
    for i, m in enumerate(msgs):
        tx_ret = trans.transmit(m)
        chan_frame = trans.channel(tx_ret['frame'], i)
        rx_ret = trans.receive(chan_frame, msgs[rx_msg_idx])
        if rx_ret['valid']:
            rx_msg_idx += 1
    assert rx_msg_idx == 99
