"""
This script is for converting the dataset of wav files into spectrogram arrays
Final arrays are stored as csv files
"""

import os
import tqdm
import numpy as np
from scipy import signal
from scipy.io import wavfile

data_dir = "./dataset/clotho/development"
spectro_data_dir = "./dataset/clotho/develop_spectro"

eval_data_dir = "./dataset/clotho/evaluation"
eval_spectro_data_dir = "./dataset/clotho/eval_spectro"

for subdir, dirs, files in os.walk(eval_data_dir):
    for file in tqdm.tqdm(files):
        wav_path = os.path.join(subdir, file)
        fs, samples = wavfile.read(wav_path)
        f, t, Zxx = signal.stft(samples)
        np.savetxt(f"{os.path.join(eval_spectro_data_dir, file)}.csv", Zxx, delimiter=',')
        