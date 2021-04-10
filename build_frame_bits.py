import numpy as np

import sksdr

msgs = ['Hello World {:03d}'.format(i) for i in range(100)]
rx_msg_idx = 0
ret = dict()
frame_size_bits = 250
preamble = np.repeat(sksdr.UNIPOLAR_BARKER_SEQ[13], 2)
scrambler_poly = [1, 1, 1, 0, 1]
scrambler_init_state = [0, 1, 1, 0]
scrambler = sksdr.Scrambler(scrambler_poly, scrambler_init_state)
fid = open('test.dat', 'wb')

for i, msg in enumerate(msgs):
    ret['payload'] = sksdr.unpack(msg, 8)
    ret['fill'] = np.random.randint(0, 1, frame_size_bits - len(preamble) - len(ret['payload']))
    ret['bits'] = np.hstack((ret['payload'], ret['fill']))
    ret['sbits'] = scrambler(ret['bits'])
    bits = np.hstack((preamble, ret['sbits']))
    nbits = len(bits)
    if nbits % 8 > 0:
        bits = np.hstack((bits, [0] * (8 - nbits % 8)))
    chars = [int(''.join(map(str, bits[i : i + 8])), 2) for i in range(0, len(bits), 8)]
    fid.write(bytes(chars))
