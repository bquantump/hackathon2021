
import numpy as np
import matplotlib.pyplot as plt
import commpy
SUBCAR_SPACING = 15e3 #15khz
SIG_BW = 1.4e6
SAMP_RATE = 1.92e6
FFT_SIZE = 128
OCCUPIED_SUBCARS = 72
DUTY_CYCLE = 0.1
N_DATA_SYMBOLS = 2
ZC_IDX = 1


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

    #packing & IFFT
    

if __name__ == '__main__':
    generate_tx_samples()