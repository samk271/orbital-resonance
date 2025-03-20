import  scipy.io.wavfile  as wav
import matplotlib.pyplot as plt
import numpy as np
import librosa
import os

#note and frequency references: https://inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies

def find_pitch(fs,x): #sourced from https://github.com/parthmehta15/Pitch/blob/master/pitch/__init__.py
    
    ms20=int((fs/50))
    ms2=int(fs/500)

    x=[i/32767 for i in x]

    y=plt.acorr(x,maxlags=ms20,normed=True)

    y=y[1]
    z=y[round(len(y)/2):]
    z=z[ms2:ms20]
    zmax=max(z)

    index=np.where(z==zmax)
    index=index[0][0]

    pitch=fs/(ms2+index+2)

    return pitch

def find_semitone_shift(fs,x):
    original_pitch = find_pitch(fs,x)

    #Calculate closest note
    closest_note = librosa.hz_to_midi(original_pitch)

    #Calculate semitone shift
    semitone_shift = closest_note - librosa.hz_to_midi(original_pitch)
    return closest_note, semitone_shift


def gen_note_library(wav_file, library_folder):
    fs,x = wav.read(os.path.join("./AI",wav_file))
    closest_note, semitone_shift = find_semitone_shift(fs,x)

    if not os.path.isdir(os.path.join(library_folder, wav_file[:-4])):
        os.mkdir(os.path.join(library_folder, wav_file[:-4]))

    for step in range(128):
        x_n = librosa.effects.pitch_shift(y=x.astype(float), sr=fs, n_steps=semitone_shift + (step-closest_note))
        out_f = f"{wav_file[:-4]}_{step}.wav"
        rounded_x_n = np.round(x_n).astype(np.int16)
        wav.write(os.path.join(library_folder,wav_file[:-4],out_f), fs, rounded_x_n)


wav_file = "out_test.wav"
print(gen_note_library(wav_file, os.path.join(f"./AUDIO/")))