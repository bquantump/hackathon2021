
import numpy as np
import matplotlib.pyplot as plt
import commpy
from scipy import signal
from signal_constants import *


def fshift_and_decimate(samples,chan_idx):
    desired_chan = 7.5
    chan_diff = chan_idx - desired_chan
    fshift = chan_diff * FFT_SAMP_RATE # since this sample rate also equals channel width
    phase_per_samp = (1.0 / TARGET_SAMP_RATE) * 2.0 * np.pi * fshift
    phase_array = np.array([i*phase_per_samp for i in range(len(samples))])
    return samples * np.exp(2.0j*phase_array)


def detect_zc(samples, cyc_shift):
    zc = commpy.sequences.zcsequence(29,63,cyc_shift)
    signal.correlate(samples,zc)