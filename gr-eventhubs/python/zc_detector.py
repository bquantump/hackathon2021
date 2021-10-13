#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2021 gr-eventhubs author.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
import pmt

class zc_detector(gr.sync_block):
    """
    docstring for block zc_detector
    """
    def __init__(self,zc_root,chan_idx,threshold):
        gr.sync_block.__init__(self,
            name="zc_detector",
            in_sig=[np.complex64],
            out_sig=None)
        self.message_port_register_out(pmt.intern("detections"))
        self.zc_root = zc_root
        self.chan_idx = chan_idx
        self.threshold = threshold

    def work(self, input_items, output_items):
        in0 = input_items[0]
        max_idx = np.argmax(np.abs(in0))
        if np.abs(in0[max_idx]) > self.threshold:
            a = pmt.make_dict()
            a = pmt.dict_add(a, pmt.string_to_symbol("zc_root"), pmt.from_long(self.zc_root))
            a = pmt.dict_add(a, pmt.string_to_symbol("chan_idx"), pmt.from_long(self.chan_idx))
            
            self.message_port_pub(pmt.intern("detections"), a)

                # got a detection
        return len(input_items[0])

