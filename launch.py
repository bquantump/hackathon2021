from multiprocessing import Pool, TimeoutError
from eventhubcore import run_server

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: bquantump
# GNU Radio version: 3.9.1.0

from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import dspcore
import eventhubs
import numpy as np
import os

def run(config):
    consumer_group, zc, channel = config
    print("got config is %s" % config)
    main(top_block_cls=testgrc, options=None, consumer_group=consumer_group, zc=zc, channel=channel)

class testgrc(gr.top_block):

    def __init__(self, consumer_group, zc, channel):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 30.72e6
        self.chan_num = chan_num = channel
        self.variable_low_pass_filter_taps_0 = variable_low_pass_filter_taps_0 = firdes.low_pass(1.0, samp_rate, 1.9e6/2,250e3, window.WIN_HAMMING, 6.76)
        self.freq_offset = freq_offset = (dspcore.FFT_SAMP_RATE) * (-7.5 + chan_num)
        self.ZC_ROOT = ZC_ROOT = zc

        ##################################################
        # Blocks
        ##################################################
        self.freq_xlating_fft_filter_ccc_0 = filter.freq_xlating_fft_filter_ccc(16, variable_low_pass_filter_taps_0, freq_offset, samp_rate)
        self.freq_xlating_fft_filter_ccc_0.set_nthreads(1)
        self.freq_xlating_fft_filter_ccc_0.declare_sample_delay(0)
        self.fft_filter_xxx_0 = filter.fft_filter_ccc(1, np.conjugate(dspcore.gen_ZC(ZC_ROOT))[::-1], 1)
        self.fft_filter_xxx_0.declare_sample_delay(0)
        self.eventhubs_zc_detector_0 = eventhubs.zc_detector(ZC_ROOT,chan_num,0.35)
        self.eventhub_source_0 = eventhubs.eventhub_source(os.environ['EVENTHUB_CONNECTION_STRING'], os.environ['EVENTHUB_HOSTNAME'], os.environ['SCHEMA_REGISTRY_GROUP'], os.environ['EVENTHUB_CONSUMER_TOPIC_NAME'], consumer_group, "@latest")
        self.eventhub_source_0.set_processor_affinity([1])
        self.blocks_message_debug_0 = blocks.message_debug(True)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.eventhubs_zc_detector_0, 'detections'), (self.blocks_message_debug_0, 'print'))
        self.connect((self.eventhub_source_0, 0), (self.freq_xlating_fft_filter_ccc_0, 0))
        self.connect((self.fft_filter_xxx_0, 0), (self.eventhubs_zc_detector_0, 0))
        self.connect((self.freq_xlating_fft_filter_ccc_0, 0), (self.fft_filter_xxx_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_variable_low_pass_filter_taps_0(firdes.low_pass(1.0, self.samp_rate, 1.9e6/2, 250e3, window.WIN_HAMMING, 6.76))

    def get_chan_num(self):
        return self.chan_num

    def set_chan_num(self, chan_num):
        self.chan_num = chan_num
        self.set_freq_offset((dspcore.FFT_SAMP_RATE) * (-7.5 + self.chan_num))

    def get_variable_low_pass_filter_taps_0(self):
        return self.variable_low_pass_filter_taps_0

    def set_variable_low_pass_filter_taps_0(self, variable_low_pass_filter_taps_0):
        self.variable_low_pass_filter_taps_0 = variable_low_pass_filter_taps_0
        self.freq_xlating_fft_filter_ccc_0.set_taps(self.variable_low_pass_filter_taps_0)

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.freq_xlating_fft_filter_ccc_0.set_center_freq(self.freq_offset)

    def get_ZC_ROOT(self):
        return self.ZC_ROOT

    def set_ZC_ROOT(self, ZC_ROOT):
        self.ZC_ROOT = ZC_ROOT




def main(top_block_cls=testgrc, options=None, consumer_group="$Default", zc=0, channel=0):
    tb = top_block_cls(consumer_group ,zc ,channel)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    while True:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    with Pool(processes=4) as pool:
        inputs = [('$Default', 0, 0), ('$Default', 1, 1),('test1', 2, 2)]
        pool.map(run, inputs)