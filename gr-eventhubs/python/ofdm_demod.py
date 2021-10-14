#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2021 gr-eventhubs author.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
import dspcore
import pmt

class ofdm_demod(gr.sync_block):
    """
    docstring for block ofdm_demod
    """
    def __init__(self,threshold):
        gr.basic_block.__init__(self,
            name="ofdm_demod",
            in_sig=[np.complex64],
            out_sig=[np.complex64])
        self.message_port_register_in(pmt.intern("detections"))
        self.set_msg_handler(pmt.intern('detections'), self.handle_det)
        self.message_port_register_out(pmt.intern("freq"))
        self.chan_idx = 0
        self.zc_root = 0
        self.min_samps = 4 * (dspcore.FFT_SIZE + dspcore.CP_LEN)
        self.threshold = threshold

    def handle_det(self,msg):
        pmsg = pmt.to_python(msg)
        self.zc_root = pmsg['zc_root']
        self.chan_idx = pmsg['chan_idx']
        freq = dspcore.TARGET_SAMP_RATE * (chan_idx-7.5)
        b = pmt.make_dict()
        b = pmt.dict_add(b, pmt.string_to_symbol("freq"), pmt.from_double(freq))
        self.message_port_pub(pmt.intern("freq"), b)


    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        if len(in0) < self.min_samps:
            return 0
        zc_idx = dspcore.detect_zc(in0[dspcore.FFT_SIZE+dspcore.CP_LEN:2*(dspcore.FFT_SIZE+dspcore.CP_LEN)],self.zc_root,self.threshold) # look for zc in first 2 symbols worth
        if zc_idx is None:
            # no ZC detected
            self.consume(0, dspcore.FFT_SIZE+dspcore.CP_LEN)
            return 0
        else:
            self.consume(0, len(in0))
            idx = zc_idx - (dspcore.FFT_LEN + dspcore.CP_LEN)
            sym1 = in0[idx:idx+dspcore.FFT_LEN]
            idx += (dspcore.FFT_LEN + dspcore.CP_LEN)
            zc = in0[idx:idx+dspcore.FFT_LEN]
            idx += (dspcore.FFT_LEN + dspcore.CP_LEN)
            sym2 = in0[idx:idx+dspcore.FFT_LEN]

            chan_response = np.fft.fft(zc)/np.fft.fft(dspcore.gen_ZC(self.zc_root))

            sym1_fft = np.fft.fft(sym1) / chan_response
            zc_fft = np.fft.fft(zc) / chan_response
            sym2_fft = np.fft.fft(sym2) /  chan_response

            sym1_fft = np.fft.fftshift(sym1_fft)
            zc_fft = np.fft.fftshift(zc_fft)
            sym2_fft = np.fft.fftshift(sym2_fft)

            sym1_final = sym1_fft[dspcore.L_GAURD:-dspcore.R_GAURD]
            zc_final = zc_fft[dspcore.L_GAURD_ZC:-dspcore.R_GAURD_ZC]
            sym2_final = sym2_fft[dspcore.L_GAURD:-dspcore.R_GAURD]

            out[:] = np.concatenate((sym1_final,zc_final,sym2_final)).to_list()
        
       
            return len(output_items[0])

