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
            in_sig=[np.float32,np.complex64],
            out_sig=[np.complex64])
        self.message_port_register_in(pmt.intern("detections"))
        self.set_msg_handler(pmt.intern('detections'), self.handle_det)
        self.message_port_register_out(pmt.intern("freq"))
        self.chan_idx = -1
        self.zc_root = 1
        self.min_samps = 5 * (dspcore.FFT_SIZE + dspcore.CP_LEN)
        self.threshold = threshold
        self.set_output_multiple(self.min_samps)
        
    def handle_det(self,msg):
        pmsg = pmt.to_python(msg)
        if self.zc_root != pmsg['zc_root']:
            self.zc_root = pmsg['zc_root']
            b = pmt.make_dict()
            b = pmt.dict_add(b, pmt.string_to_symbol("taps"), pmt.to_pmt(list(np.conjugate(dspcore.gen_ZC(self.zc_root))[::-1])))
            self.message_port_pub(pmt.intern("freq"), b)
        if self.chan_idx != pmsg['chan_idx']:
            self.chan_idx = pmsg['chan_idx']
            freq = dspcore.FFT_SAMP_RATE * (self.chan_idx-7.5)
            b = pmt.make_dict()
            b = pmt.dict_add(b, pmt.string_to_symbol("freq"), pmt.from_double(freq))
            self.message_port_pub(pmt.intern("freq"), b)



    def general_work(self, input_items, output_items):
        cor = input_items[0]
        data = input_items[1]
        out = output_items[0]
        
        if len(cor) < self.min_samps:
            print("NOT ENOUGH SAMPS\n")
            return 0
        max_idx = np.argmax(cor)
        max_cor = cor[max_idx]

        if max_cor < self.threshold:
            print("NO DECT\n")
            self.consume(0, len(cor))
            self.consume(1, len(cor))
            return 0
        else:
            if max_idx < (dspcore.FFT_SIZE + dspcore.CP_LEN):
                print("ZC TO CLOSE TO LEFT EDGE \n")
                # ZC too close to left edge
                self.consume(0, len(cor))
                self.consume(1, len(cor))
                return 0
            elif (len(cor) - max_idx) < 3*(dspcore.FFT_SIZE + dspcore.CP_LEN):
                print("ZC TO CLOSE TO RIGHT EDGE\n")
                print(max_idx)
                print(len(cor))
                # ZC too close to right edge
                self.consume(0, int(0.5*(dspcore.FFT_SIZE + dspcore.CP_LEN)))
                self.consume(1, int(0.5*(dspcore.FFT_SIZE + dspcore.CP_LEN)))
                return 0
            else:
                print("SHOULD BE GOOD\n")
                zc_idx = max_idx
                self.consume(0, len(cor))
                self.consume(1, len(cor))
                idx = zc_idx - (dspcore.FFT_SIZE + dspcore.CP_LEN)

                sym1 = data[idx:idx+dspcore.FFT_SIZE]
                idx += (dspcore.FFT_SIZE + dspcore.CP_LEN)
                zc = data[idx:idx+dspcore.FFT_SIZE]
                idx += (dspcore.FFT_SIZE + dspcore.CP_LEN)
                sym2 = data[idx:idx+dspcore.FFT_SIZE]
                
                chan_response = np.fft.fft(zc)/np.fft.fft(dspcore.gen_ZC(self.zc_root))
                zc_fft = np.fft.fft(zc)
                sym1_fft = np.fft.fft(sym1)
                sym2_fft = np.fft.fft(sym2)

                chan_response = np.fft.fftshift(chan_response)
                zc_fft = np.fft.fftshift(zc_fft)
                sym1_fft = np.fft.fftshift(sym1_fft)
                sym2_fft = np.fft.fftshift(sym2_fft)

                chan_response[dspcore.L_GAURD:dspcore.L_GAURD_ZC] = [chan_response[dspcore.L_GAURD_ZC + 1]] * 5
                chan_response[dspcore.L_GAURD_ZC + dspcore.OCCUPIED_SUBCARS_ZC:dspcore.L_GAURD_ZC + dspcore.OCCUPIED_SUBCARS_ZC + 5] = [chan_response[dspcore.L_GAURD_ZC + dspcore.OCCUPIED_SUBCARS_ZC - 1]] * 5
                #print("chan repson")
                #print(max_idx)
                #print(len(cor))
                sym1_fft = sym1_fft / chan_response
                sym2_fft = sym2_fft / chan_response
                zc_fft = zc_fft / chan_response
                '''
                sym1_fft = np.fft.fft(sym1)
                zc_fft = np.fft.fft(zc)
                sym2_fft = np.fft.fft(sym2)
                '''

                sym1_final = sym1_fft[dspcore.L_GAURD:-dspcore.R_GAURD]
                zc_final = zc_fft[dspcore.L_GAURD_ZC:-dspcore.R_GAURD_ZC]
                sym2_final = sym2_fft[dspcore.L_GAURD:-dspcore.R_GAURD]
                #print(np.shape(np.concatenate((sym1_final,zc_final,sym2_final)).tolist()))
                res = np.concatenate((sym1_final,sym2_final))

                outlen = len(res)
                out[:outlen] = res
        
                return len(res)

