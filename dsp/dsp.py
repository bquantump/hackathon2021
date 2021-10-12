
import numpy as np
import matplotlib.pyplot as plt
import commpy
from scipy import signal

N_DATA_SYMBOLS = 2
DUTY_CYCLE = 0.25
SUBCAR_SPACING = 15e3 #15khz
SIG_BW = 1.4e6
FFT_SAMP_RATE = 1.92e6
TARGET_SAMP_RATE = 30.72e6
NUM_CHANS = TARGET_SAMP_RATE/FFT_SAMP_RATE
FFT_SIZE = 128
OCCUPIED_SUBCARS = 73 # with DC
GAURD_BAND_SUBCARS =  FFT_SIZE - OCCUPIED_SUBCARS
L_GAURD = int(GAURD_BAND_SUBCARS/2)
R_GAURD = GAURD_BAND_SUBCARS - L_GAURD
OCCUPIED_SUBCARS_ZC = 63 # with DC
GAURD_BAND_SUBCARS_ZC = FFT_SIZE - OCCUPIED_SUBCARS_ZC
L_GAURD_ZC = int(GAURD_BAND_SUBCARS_ZC/2)
R_GAURD_ZC = GAURD_BAND_SUBCARS_ZC - L_GAURD_ZC
CP_LEN = 9 # samples long

# Implemenet a simplistic OFDM signal with the following
# layout SYM-ZC-SYM

def generate_tx_samples(chan_idx=None,ZC_root=None):
    
    #data I-Q generation
    data_pointsI = np.random.randint(2,size=OCCUPIED_SUBCARS*N_DATA_SYMBOLS)
    data_pointsQ = np.random.randint(2,size=OCCUPIED_SUBCARS*N_DATA_SYMBOLS)
    constellation_points = (1.0 - 2*data_pointsI) + 1.0j * (1.0 - 2*data_pointsQ)

    #ZC generation
    if ZC_root is None:
        ZC_root = np.choose([1],[25,29,34])
    zc = commpy.sequences.zcsequence(ZC_root,63)

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
    if chan_idx is None:
        chan_idx = np.random.randint(NUM_CHANS)
    chan_diff = initial_chan - chan_idx
    fshift = chan_diff * FFT_SAMP_RATE # since this sample rate also equals channel width
    phase_per_samp = (1.0 / TARGET_SAMP_RATE) * 2.0 * np.pi * fshift
    phase_array = np.array([i*phase_per_samp for i in range(len(extended_full_rate))])
    extended_full_rate = extended_full_rate * np.exp(2.0j*phase_array)
    print("channel randomly chosen as {}".format(chan_idx))
    print("ZC root: {}".format(ZC_root))
    return extended_full_rate

def fshift_and_decimate(samples,chan_idx):
    desired_chan = 7.5
    chan_diff = chan_idx - desired_chan
    fshift = chan_diff * FFT_SAMP_RATE # since this sample rate also equals channel width
    phase_per_samp = (1.0 / TARGET_SAMP_RATE) * 2.0 * np.pi * fshift
    phase_array = np.array([i*phase_per_samp for i in range(len(samples))])
    r = samples * np.exp(2.0j*phase_array)
    return signal.resample(r,int(len(r)/16))


def detect_zc(samples, root,threshold):
    zc = commpy.sequences.zcsequence(root,63)
    padded = np.concatenate((np.zeros(L_GAURD_ZC),zc,np.zeros(R_GAURD_ZC)))
    shifted = np.fft.ifftshift(padded)
    zc_sig = np.fft.ifft(shifted)

    cor = np.abs(signal.correlate(samples,zc_sig))
    
    max_idx = np.argmax(cor)
    if cor[max_idx] > threshold:
        print("peak detected at idx {} for zc {}, score {}".format(max_idx,root,cor[max_idx]))
        plt.plot(cor)
        plt.show()

if __name__ == '__main__':
    fsamps = generate_tx_samples()
    for chan in range(16):
        print('chan: {}'.format(chan))
        samps = fshift_and_decimate(fsamps,chan)
        for zc in [25,29,34]:
            detect_zc(samps, zc,0.35)
    #print(np.abs(cor[:10]))
    