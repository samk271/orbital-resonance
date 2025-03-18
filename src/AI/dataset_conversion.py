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

sample_rates = []
sample_lengths = []
frequencies = []

for subdir, dirs, files in os.walk(data_dir):
    
    for file in tqdm.tqdm(files):
        wav_path = os.path.join(subdir, file)
        fs, samples = wavfile.read(wav_path)
        f, t, Zxx = signal.stft(samples)

        sample_rates.append(fs)
        sample_lengths.append(Zxx.shape[1])
        frequencies.append(Zxx.shape[0])
        # np.savetxt(f"{os.path.join(eval_spectro_data_dir, file)}.csv", Zxx, delimiter=',')

print(f"Sample rate mean: {np.mean(sample_rates)}")
print(f"Sample lengths max: {np.max(sample_lengths)}")
print(f"frequence ranges: {np.mean(frequencies)}")