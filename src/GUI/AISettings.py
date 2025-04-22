from os import listdir, mkdir
from os.path import isdir
from pathlib import Path
from shutil import copy
from threading import Thread
from librosa import midi_to_note, yin, note_to_hz, hz_to_midi, note_to_midi
from librosa.effects import pitch_shift
from scipy.io.wavfile import read, write
from numpy import round as np_round, average, isnan, median, mean, int16, array
from pygame.mixer import Sound
from contextlib import redirect_stderr
from tkinter.colorchooser import askcolor
from GUI.SignalPlot import AudioPlotFrame
from GUI.PlanetSettings import PlanetSettings
from Physics.PlanetManager import PlanetManager
from GUI.MidiEditor import MidiEditor
from FileManagement.IORedirect import IORedirect
from tkinter.filedialog import askopenfilename
from customtkinter import CTkFrame, CTkLabel, CTkTextbox, CTkButton, CTkOptionMenu, CTkTabview, CTkProgressBar, \
    StringVar


class AISettings(CTkFrame):
    """
    The class that will handle the settings menu that controls the AI planet generation
    """

    LOAD_OPTIONS = {
        "initialdir": Path("./AUDIO/prebuilt_samples"),
        "title": "Select a File",
        "filetypes": [
            (".wav files", "*.wav")
        ],
        "defaultextension": ".wav",
        "parent": None,  # will be set when initial window is loaded
    }

    def __init__(self, *args, **kwargs):
        """
        creates the settings window

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        #Check for planet manager in args
        self.planet_manager: PlanetManager = kwargs.pop("planet_manager")
        self.planet_settings: PlanetSettings = kwargs.pop("planet_settings")
        self.pipe = kwargs.pop("pipe")

        # initializes superclass and binds user actions
        super().__init__(*args, **kwargs)


        """
        TEMPORARILY DISABLING AI PROMPT
        # creates the input label
        input_label = CTkLabel(self, text="AI Input:", font=("Arial", 20))
        input_label.grid(row=0, column=1, rowspan=3, sticky="ne", pady=20, padx=(20, 0))

        # creates user input text box
        self.textbox = CTkTextbox(self, height=94)
        self.textbox.grid(row=0, column=2, rowspan=3, pady=20, padx=10)
        """

        #Intiialize tabs
        self.tabview = CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.sample_tab = self.tabview.add("Sample Editor")
        self.sequence_tab = self.tabview.add("Sequence Editor")

        self.sample_editor(self.sample_tab)
        self.sequence_editor(self.sequence_tab)


        # sets column weights for dynamic resizing
        self.tabview.grid_propagate(False)


    def sequence_editor(self, parent):
        self.midi = MidiEditor(parent, planet_manager=self.planet_manager, fg_color=parent.cget("fg_color"))
        self.midi.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

    def sample_editor(self, parent):

        input_label = CTkLabel(parent, text="AI Input:", font=("Arial", 18))
        input_label.grid(row=0, column=1, sticky="nw", pady=(10, 5), padx=(10, 0))

        # creates user input text box
        self.ai_textbox = CTkTextbox(parent, height=200, width=400)
        self.ai_textbox.grid(row=1, column=1, sticky="nsw", padx=(10, 0), rowspan=5)

        self.generate_button = CTkButton(parent, text="Generate Sound")
        self.generate_button.configure(command=lambda: self.generate_audio())
        self.generate_button.grid(row=6, column=1, padx=(10, 0), pady=10, sticky="ew")

        self.gen_pbar = CTkProgressBar(parent, width = 300, mode = 'determinate')
        self.gen_pbar.grid(row=6,column=3, sticky="ew", padx=20)
        self.gen_pbar.set(1)

        # self.listbox_label = CTkLabel(parent, text="Preset Samples:", font=("Arial", 18))
        # self.listbox_label.grid(row=0, column=1, sticky="nw", pady=20, padx=(20, 0))
        #
        # self.listbox = CTkListbox(parent, width=290,height=150, hover=True)
        # self.listbox.grid(row=1,column=1,rowspan=2,pady=20,padx=10)

        self.sr = 16000
        self.signal = [None]
        self.shifted_signal = None
        self.midi_note = -1
        self.raw_pitch = -1

        # # doesnt crash if dataset is not found
        # try:
        #     self.add_wav_to_listbox(listbox=self.listbox, wav_dir="./AUDIO/prebuilt_samples")
        # except:
        #     pass

        # creates the generated sound display

        generated_label = CTkLabel(parent, text="Generated Audio:", font=("Arial", 18))
        generated_label.grid(row=0, column=3, sticky="nw", pady=(10, 5), padx=20)
        self.audio_frame = AudioPlotFrame(parent, audio_signal=self.signal, sample_rate=self.sr, fg_color=parent.cget("fg_color"))
        self.audio_frame.grid(row=1, column=3, rowspan=5, padx=20, sticky="ns")

        # self.select_button = CTkButton(parent, text="Select Sound")
        # self.select_button.configure(command=lambda: self.select_sound(
        #     wav_dir="./AUDIO/prebuilt_samples"))
        # self.select_button.grid(row=3, column=1, pady=5)

        # creates play sound button todo add function
        self.play_button = CTkButton(parent, text="Play Sound")
        self.play_button.configure(command=lambda: self.play_sound(self.signal,self.sr))
        self.play_button.grid(row=4, column=5, sticky="sew", columnspan=2)

        #Create name input box
        self.name_label = CTkLabel(parent, text="Sample Name:", font=("Arial", 18))
        self.name_label.grid(row=0, column=5, sticky="w", pady=(10, 5), columnspan=2)
        self.sample_name_input = CTkTextbox(parent, height=10)
        self.sample_name_input.grid(row=1, column=5, sticky="new", columnspan=2)

        # Create pitch dropdowns
        self.pitch_label = CTkLabel(parent, text="Pitch:", font=("Arial", 18))
        self.pitch_label.grid(row=2, column=5, sticky="sw", columnspan=2, pady=(10, 5))

        # Note letter dropdown (A to G)
        self.note_letter_var = StringVar(value="C")
        self.octave_number_var = StringVar(value="4")
        self.note_letter_menu = CTkOptionMenu(parent, values=["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
                                              variable=self.note_letter_var,
                                              command=self.update_pitch)
        self.note_letter_menu.grid(row=3, column=5, sticky="nw")

        # Octave number dropdown (2 to 7)
        self.octave_number_menu = CTkOptionMenu(parent, values=[str(i) for i in range(1, 8)], variable=self.octave_number_var,
                                                command=self.update_pitch)
        self.octave_number_menu.grid(row=3, column=6, sticky="nw")

        # creates add button todo add function
        self.save_button = CTkButton(parent, text="Save Sample")
        self.save_button.configure(command=lambda: self.add_sample_to_list())
        self.save_button.grid(row=6, column=5, sticky="ew", columnspan=2)

        # creates load file button
        load = CTkButton(parent, text="Load Audio File", command=self.load_sound_from_file)
        load.grid(row=5, column=5, sticky="ew", columnspan=2, pady=(1, 20))

        # sets sizing
        parent.rowconfigure(3, weight=1)
        # parent.rowconfigure(2, weight=3)
        parent.columnconfigure(0, weight=2)
        parent.columnconfigure(2, weight=1)
        parent.columnconfigure(4, weight=1)
        parent.columnconfigure(7, weight=2)


    def select_color(self):
        temp_planet_color = askcolor(color=self.planet_color)[1]
        if temp_planet_color != None:
            self.planet_color = temp_planet_color
            self.planet_canvas.delete("all")
            new_tag = self.planet_canvas.create_oval(0, 0, 60, 60, fill=self.planet_color)
            self.planet_canvas.tag_bind(new_tag, "<ButtonRelease-1>", lambda e: self.select_color())

    def load_sound_from_file(self):
        wav_path = askopenfilename(**AISettings.LOAD_OPTIONS)
        fs, x = read(wav_path)

        if x.ndim > 1:
            x = mean(x, axis=1)

        nearest = self.find_nearest_midi(x,fs)
        self.midi_note = nearest
        self.raw_pitch = nearest
        self.sr=fs
        self.signal=x
        self.shifted_signal=x

        self.update_plot()

        # enable the buttons
        self.sample_name_input.delete('1.0', "end")
        num_user_samples = len(listdir("./AUDIO/user_samples"))
        self.sample_name_input.insert(index="end",text =f"sample_{num_user_samples}")


    def update_plot(self):

        if len(self.signal) == 0:
            return

        if (len(self.signal.shape) > 1):
            x= average(self.signal, axis=1)
        else:
            x=self.signal

        self.audio_frame.update_waveform(new_signal=x, new_sample_rate=self.sr)

        left, right = self.audio_frame.get_crop_indices()
        self.midi_note = self.find_nearest_midi(self.signal[left:right],self.sr)

        #Change displayed pitch to closest midi
        self.set_pitch_dropdown(note_str=midi_to_note(self.midi_note))



    def play_sound(self, signal, sr):

        try:

            left, right = self.audio_frame.get_crop_indices()

            self.shifted_signal = self.shifted_signal.astype(int16)

            if (self.shifted_signal is None):
                write("./AUDIO/temp/temp.wav", sr, signal[left:right].astype(int16))
            else:
                write("./AUDIO/temp/temp.wav", sr, self.shifted_signal[left:right])


            sound = Sound("./AUDIO/temp/temp.wav")
            sound.play()

        # handles default no sound
        except AttributeError:
            pass


    def generate_library(self):
        """
        stores cropped sample to dedicated planet wav file
        """

        planet_name = self.sample_name_input.get("1.0",'end-1c')

        if not (isdir(f"./AUDIO/planets/{planet_name}")):
            mkdir(f"./AUDIO/planets/{planet_name}")

        copy("./AUDIO/temp_wav.wav", f"./AUDIO/planets/{planet_name}/{planet_name}.wav")
        self.save_button.configure(state="normal", fg_color=self.select_button.cget("fg_color"))


    #Save sample
    def add_sample_to_list(self):

        sample_name = self.sample_name_input.get("1.0",'end-1c')
        prompt = self.ai_textbox.get("1.0", "end-1c")

        sample_data = {
            'name':sample_name,
            'raw_signal_array':self.signal,
            'shifted_signal_array':self.shifted_signal,
            'sample_rate':self.sr,
            'prompt':prompt,
            'crops':self.audio_frame.get_crop_indices(),
            'raw_pitch':self.raw_pitch,
            'pitch':self.midi_note,
            "volume": 1
        }
        if self.shifted_signal is not None:
            left, right = self.audio_frame.get_crop_indices()
            if not (isdir(f"./AUDIO/user_samples/{sample_name}")):
                mkdir(f"./AUDIO/user_samples/{sample_name}")
            write(f"./AUDIO/user_samples/{sample_name}/{sample_name}_{self.midi_note}.wav",self.sr, self.shifted_signal[left:right].astype(int16))
        self.planet_manager.add_sample(sample_name, sample_data)

    #add all the wav files from the directory to the listbox
    def add_wav_to_listbox(self, listbox, wav_dir):
        wav_files = listdir(wav_dir)
        for i, file in enumerate(wav_files):
            listbox.insert(i, file)

    def generate_audio(self):
        prompt = self.ai_textbox.get("1.0", "end-1c")

        redirector = IORedirect(self.gen_pbar)

        def start_pipe():
            def task():
                with redirect_stderr(redirector):
                    self.generate_button.configure(text="Generating...", fg_color="gray25", state="disabled")
                    audio = self.pipe(prompt, negative_prompt="Low quality, noisy, and with ambience.", num_inference_steps=100, audio_length_in_s=4.0).audios[0]
                    num_user_samples = len(listdir("./AUDIO/user_samples"))
                    self.generate_button.configure(text = "Generate", state="normal", fg_color=self.save_button.cget("fg_color"))

                self.sr = 16000
                self.midi_note = self.find_nearest_midi(audio,self.sr)
                self.signal = audio*32767 #Adjust float to int range
                self.shifted_signal = audio*32767

                self.generate_button.configure(text = "Generate", state="normal", fg_color=self.save_button.cget("fg_color"))
                #Change displayed pitch to closest midi
                self.set_pitch_dropdown(note_str=midi_to_note(self.midi_note))

                self.update_plot()
                self.play_button.configure(state="normal", fg_color=self.save_button.cget("fg_color"))
                self.sample_name_input.delete('1.0', "end")
                self.sample_name_input.insert(index="end",text =f"sample_{num_user_samples}")
                self.save_button.configure(state="normal", fg_color=self.save_button.cget("fg_color"))

            Thread(target=task).start()

        start_pipe()

    #Sets the pitch menu to the param note
    def set_pitch_dropdown(self, note_str):
        """
        Given a string note like 'C#5', sets the pitch dropdowns accordingly.

        Parameters:
        - note_str: str, musical note in the format like 'C4', 'D#5', etc.
        """

        octave = note_str[-1]
        note_letter = note_str[:-1]

        # Update the dropdown values
        self.note_letter_var.set(note_letter)
        self.octave_number_var.set(octave)


    def find_nearest_midi(self, y, sr):
        """
        Given an audio signal and sample rate, returns the closest MIDI note of the signal.

        Parameters:
        - y: np.ndarray, the input audio signal.
        - sr: int, the sample rate.

        Returns:
        - midi_note: int, the closest MIDI note to the detected pitch.
        - y_tuned: np.ndarray, the pitch-shifted (autotuned) signal.
        """
        # Step 1: Estimate the fundamental frequency (f0) using YIN
        f0 = yin(y.astype(float), fmin=note_to_hz('C1'), fmax=note_to_hz('C7'), sr=sr)

        # Remove unvoiced (nan) values
        f0_clean = f0[~isnan(f0)]

        if len(f0_clean) == 0:
            raise ValueError("No fundamental frequency detected in the signal.")

        # Step 2: Take the median frequency as the representative pitch
        median_f0 = median(f0_clean)

        # Step 3: Convert to MIDI note
        midi_note = int(np_round(hz_to_midi(median_f0)))

        return midi_note

    def update_pitch(self, _=None):
        """
        Pitch shifts the signal to the note in the pitch menu, saves to temp
        """

        if (self.signal[0] is None):
            return

        desired_note = self.note_letter_var.get() + self.octave_number_var.get()
        desired_midi = note_to_midi(desired_note)
        steps_to_shift = desired_midi - self.find_nearest_midi(self.signal, self.sr)

        self.shifted_signal = pitch_shift(self.signal.astype(float), sr=self.sr, n_steps=steps_to_shift)

        self.play_sound(signal=self.shifted_signal,sr=self.sr)
        self.midi_note = desired_midi

    def load_sample(self, sample_name):
        """
        Takes a sample dictionary object and loads it to the UI

        sample_data = {
            'raw_signal_array':self.signal,
            'shifted_signal_array':self.shifted_signal,
            'sample_rate':self.sr,
            'prompt':prompt,
            'crops':self.audio_frame.get_crop_indices(),
            'pitch':self.midi_note,
            "volume": 1
        }
        """

        sample = self.planet_manager.samples[sample_name]
        self.signal = sample["raw_signal_array"] if "raw_signal_array" in sample else array([0, 0])
        self.shifted_signal = sample["shifted_signal_array"] if "raw_signal_array" in sample else None
        self.sr = sample["sample_rate"] if "raw_signal_array" in sample else 16000

        #Add prompt to textbox
        self.ai_textbox.delete("0.0", "end")
        self.ai_textbox.insert(index="end", text=sample["prompt"]) if "raw_signal_array" in sample else None

        #Add pitch to pitch box
        note_pitch = midi_to_note(sample["pitch"])
        letter = note_pitch[1]
        octave = note_pitch[-1]
        if len(note_pitch) > 2:
            letter += "#"

        self.note_letter_var.set(letter)
        self.octave_number_var.set(octave)

        self.sample_name_input.delete('1.0', "end")
        self.sample_name_input.insert(index="end",text =sample_name)
        self.update_plot()
        self.audio_frame.set_crop_positions(sample["crops"][0],sample["crops"][1]) if "raw_signal_array" in sample else None

        self.midi.load_sample(sample_name)