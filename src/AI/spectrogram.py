import numpy as np
from scipy import signal
from scipy.io import wavfile
import matplotlib.pyplot as plt

fs = 1024

N = 10*fs
nperseg = 512
amp = 2 * np.sqrt(2)
noise_power = 0.001 * fs / 2
time = np.arange(N) / float(fs)

fs, samples = wavfile.read(".\dataset\clotho\development\\09 hn_handrail.wav")

print(samples)

f, t, Zxx = signal.stft(samples)

# plt.pcolormesh(t, f, np.abs(Zxx))
# plt.title('STFT Magnitude')
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [sec]')
# plt.show()

#Zxx = np.where(np.abs(Zxx) >= amp/10, Zxx, 0)
_, xrec = signal.istft(Zxx, fs)

rounded_xrec = np.round(xrec).astype(np.int16)

# plt.figure()
# plt.plot(range(len(xrec)), xrec, label = "recreated signal")
# plt.plot(range(len(samples)), samples, label = "original signal")
# plt.plot(range(len(samples)), xrec-samples, label = "difference")

# plt.legend()
# plt.show()

out_f = 'out_test.wav'
wavfile.write(out_f, fs, rounded_xrec[:10000])