
import numpy as np
import matplotlib.pyplot as plt
import commpy
from scipy import signal
from signal_constants import *

# Implemenet a simplistic OFDM signal with the following
# layout SYM-ZC-SYM

def generate_tx_samples():
    
    #data I-Q generation
    data_pointsI = np.random.randint(2,size=OCCUPIED_SUBCARS*N_DATA_SYMBOLS)
    data_pointsQ = np.random.randint(2,size=OCCUPIED_SUBCARS*N_DATA_SYMBOLS)
    constellation_points = (1.0 - 2*data_pointsI) + 1.0j * (1.0 - 2*data_pointsQ)

    #ZC generation
    cyc_shift = np.random.randint(62) + 1
    zc = commpy.sequences.zcsequence(29,63,cyc_shift)

    # packing
    f_domain_symbs = []
    f_domain_symbs.append(np.concatenate((np.zeros(L_GAURD),constellation_points[0:OCCUPIED_SUBCARS], np.zeros(R_GAURD))))
    f_domain_symbs.append(np.concatenate((np.zeros(L_GAURD_ZC),zc,np.zeros(R_GAURD_ZC))))
    f_domain_symbs.append(np.concatenate((np.zeros(L_GAURD) , constellation_points[OCCUPIED_SUBCARS:] , np.zeros(R_GAURD))))

    #IFFT
    t_domain_symbs = []
    for s in f_domain_symbs:
        shifted = np.fft.ifftshift(s)
        t_domain_symbs.append(np.fft.ifft(shifted))

    #CP insertion
    for i in range(3):
        tds = np.concatenate((t_domain_symbs[i],t_domain_symbs[i][0:CP_LEN]))
        t_domain_symbs[i] = tds
    
    #flatten and extend to meet duty cycle
    flattened = np.concatenate(t_domain_symbs)
    extension_factor = int(1/DUTY_CYCLE) - 1
    extended = np.concatenate((flattened,np.zeros(extension_factor*len(flattened))))

    # upsample & rotate to channel
    extended_full_rate = signal.resample(extended,16*len(extended))
    initial_chan = 7.5
    chan_idx = np.random.randint(NUM_CHANS)
    chan_diff = initial_chan - chan_idx
    fshift = chan_diff * FFT_SAMP_RATE # since this sample rate also equals channel width
    phase_per_samp = (1.0 / TARGET_SAMP_RATE) * 2.0 * np.pi * fshift
    phase_array = np.array([i*phase_per_samp for i in range(len(extended_full_rate))])
    extended_full_rate = extended_full_rate * np.exp(2.0j*phase_array)
    print("channel randomly chosen as {}".format(chan_idx))
    print("ZC cyc shift: {}".format(cyc_shift))
    #plt.plot(np.abs(extended_full_rate))
    #plt.show()
    #plt.plot(np.abs(np.fft.fft(extended_full_rate)))
    #plt.show()
if __name__ == '__main__':
    generate_tx_samples()