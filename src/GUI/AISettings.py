import io
import os
import queue
import shutil
import threading
import tkinter as tk
from contextlib import redirect_stderr
from tkinter.colorchooser import askcolor
from tkinter.scrolledtext import ScrolledText
from customtkinter import CTkFrame, CTkLabel, CTkTextbox, CTkButton, CTkCanvas, CTkTabview
from CTkListbox import *
import scipy.io.wavfile  as wav
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from RangeSlider.RangeSlider import RangeSliderH 
import librosa
import pygame
from random import randint
from diffusers import AudioLDM2Pipeline
import torch

# from GUI import note_lib_gen as nlg
from Physics.PlanetManager import PlanetManager
from Physics.Planet import Planet
from GUI.MidiEditor import MidiEditor


class AISettings(CTkFrame):
    """
    The class that will handle the settings menu that controls the AI planet generation

    todo add to solar system button functionality
    """

    def __init__(self, *args, **kwargs):
        """
        creates the settings window

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        #Check for planet manager in args
        if "planet_manager" in kwargs:
            self.planet_manager: PlanetManager = kwargs.pop("planet_manager")
        else:
            raise AttributeError("kwargs missing planet_manager")

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

        #initialize ai model
        repo_id = "cvssp/audioldm2"
        self.pipe = AudioLDM2Pipeline.from_pretrained(repo_id, torch_dtype=torch.float16)
        self.pipe = self.pipe.to("cuda" if torch.cuda.is_available() else "cpu")

        # sets column weights for dynamic resizing
        self.columnconfigure(0, weight=1)
        self.columnconfigure(7, weight=1)

        

    def sequence_editor(self, parent):
        self.midi = MidiEditor(parent, planet_manager=self.planet_manager, fg_color=self.cget("fg_color"))
        self.midi.grid(row=0, column=8)

    def sample_editor(self, parent):

        input_label = CTkLabel(parent, text="AI Input:", font=("Arial", 18))
        input_label.grid(row=0, column=0, sticky="nw", pady=20, padx=(20, 0))

        # creates user input text box
        self.ai_textbox = CTkTextbox(parent, height=200, width=400)
        self.ai_textbox.grid(row=1, column=0, rowspan=3, sticky="nw", padx=10)

        self.generate_button = CTkButton(parent, text="Generate Sound")
        self.generate_button.configure(command=lambda: self.generate_audio())
        self.generate_button.grid(row=2, column=0, rowspan=3, padx=10)

        self.gen_pbar = CTkLabel(parent, text = "", font=("Courier", 12), width=80)
        self.gen_pbar.grid(row=3,column=0, pady = 20, padx=10)

        self.listbox = CTkListbox(parent, width=320,height=120, hover=True)
        self.listbox.grid(row=1,column=1,rowspan=2,pady=20,padx=10)

        self.sr = 0
        self.signal = []

        # doesnt crash if dataset is not found
        try:
            self.add_wav_to_listbox(listbox=self.listbox, wav_dir="./AUDIO/prebuilt_samples")
        except:
            pass

        # creates the generated sound display
        fig = Figure(figsize = (5, 3), dpi = 100)
        plot1 = fig.add_subplot(111)
        self.sound_graph = FigureCanvasTkAgg(fig, master = parent)
        self.sound_graph.draw()
        self.sound_graph.get_tk_widget().grid(row=1, column=2, columnspan=2, rowspan=2, pady=(10,0), padx=10)

        self.select_button = CTkButton(parent, text="Select Sound")
        self.select_button.configure(command=lambda: self.select_sound(
            wav_dir="./AUDIO/temp_samples", plot=plot1))
        self.select_button.grid(row=3, column=1, pady=5)

        # create slider under graph
        self.hLeft = tk.DoubleVar(value=0)
        self.hRight = tk.DoubleVar(value=1)
        self.hSlider = RangeSliderH(parent , [self.hLeft, self.hRight],
                                     padX = 12, bgColor="gray17", font_color="#ffffff", digit_precision='.2f')
        self.hSlider.grid(row=3,column=2, columnspan=2,pady=10)
        self.hSlider.bind("<Button-1>", lambda e: self.update_sound(plot=plot1))

        # creates play sound button todo add function
        self.play_button = CTkButton(parent, text="Play Sound",width=100, height=20,  state="disabled", fg_color="gray25")
        self.play_button.configure(command=lambda: self.play_sound())
        self.play_button.grid(row=4,column=3,pady=10)


        #Create name input box
        self.name_label = CTkLabel(parent,height=10, text="Name your sample")
        self.name_label.grid(row=1, column=4, sticky="n", pady=(20,0))
        self.sample_name_input = CTkTextbox(parent, height=10)
        self.sample_name_input.grid(row=1, column=4, sticky="n",pady=(40))

        # creates add button todo add function
        self.save_button = CTkButton(parent, text="Save Sample", fg_color="gray25", state="disabled")
        self.save_button.configure(command=lambda: self.add_sample_to_list())
        self.save_button.grid(row=2, column=4, sticky="s", pady=(0, 20))


    def select_color(self):
        temp_planet_color = askcolor(color=self.planet_color)[1]
        if temp_planet_color != None:
            self.planet_color = temp_planet_color
            self.planet_canvas.delete("all")
            new_tag = self.planet_canvas.create_oval(0, 0, 60, 60, fill=self.planet_color)
            self.planet_canvas.tag_bind(new_tag, "<ButtonRelease-1>", lambda e: self.select_color())

    def select_sound(self, wav_dir, plot):
        wav_file = self.listbox.get()
        fs, x = wav.read(os.path.join(wav_dir,wav_file))

        self.sr=fs
        self.signal=x

        #Write the sound file with the slider cropping
        wav.write("./AUDIO/temp_wav.wav",self.sr, self.signal[
            int(len(self.signal)*self.hLeft.get()):int(len(self.signal)*self.hRight.get())])
        

        #average stereo wav signal
        if (len(x.shape) > 1):
            x = np.average(x, axis=1)

        plot.cla()
        
        #Draw signal with appropriate cropping
        plot.plot(range(len(x)),x)
        plot.plot(range(int(len(x)*self.hLeft.get())),x[:int(len(x)*self.hLeft.get())], color="skyblue")
        plot.plot(range(int(len(x)*self.hRight.get()),len(x)),x[int(len(x)*self.hRight.get()):], color="skyblue")
        self.sound_graph.draw()

        # enabled the buttons
        self.play_button.configure(state="normal", fg_color=self.select_button.cget("fg_color"))
        

    def update_sound(self,plot):

        if (len(self.signal.shape) > 1):
            x= np.average(self.signal, axis=1)
        else:
            x=self.signal

        #Update plot
        plot.cla()
        plot.plot(range(len(x)),x)
        plot.plot(range(int(len(x)*self.hLeft.get())),x[:int(len(x)*self.hLeft.get())], color="skyblue")
        plot.plot(range(int(len(x)*self.hRight.get()),len(x)),x[int(len(x)*self.hRight.get()):], color="skyblue")
        self.sound_graph.draw()

        #Write the sound file with the slider cropping
        wav.write("./AUDIO/temp_wav.wav",self.sr, self.signal[
            int(len(self.signal)*self.hLeft.get()):int(len(self.signal)*self.hRight.get())])
        


    def play_sound(self):

        if not os.path.isfile("./AUDIO/temp_wav.wav"):
            wav.write("./AUDIO/temp_wav.wav",self.sr, self.signal[
                int(len(self.signal)*self.hLeft.get()):int(len(self.signal)*self.hRight.get())])
            

        sound = pygame.mixer.Sound("./AUDIO/temp_wav.wav")
        sound.play()


    def generate_library(self):
        """
        stores cropped sample to dedicated planet wav file
        """

        planet_name = self.sample_name_input.get("1.0",'end-1c')

        if not (os.path.isdir(f"./AUDIO/planets/{planet_name}")):
            os.mkdir(f"./AUDIO/planets/{planet_name}")

        shutil.copy("./AUDIO/temp_wav.wav", f"./AUDIO/planets/{planet_name}/{planet_name}.wav")
        self.save_button.configure(state="normal", fg_color=self.select_button.cget("fg_color"))

        
    #Add planet to solar system
    def add_sample_to_list(self):

        planet_name = self.sample_name_input.get("1.0",'end-1c')

        planet= Planet(period=self.planet_duration.get()
                       ,radius=20, color=self.planet_color, 
                       sound_path=f"./AUDIO/planets/{planet_name}/{planet_name}.wav"
                       ,offset=self.planet_offset.get())

        self.planet_manager.add_planet(planet)

    #add all the wav files from the directory to the listbox
    def add_wav_to_listbox(self, listbox, wav_dir):
        wav_files = os.listdir(wav_dir)
        for i, file in enumerate(wav_files):
            listbox.insert(i, file)

    def generate_audio(self):
        prompt = self.ai_textbox.get("1.0", "end-1c")

        redirector = CTkLabelRedirector(self.gen_pbar)

        def start_pipe():
            def task():
                with redirect_stderr(redirector):
                    audio = self.pipe(prompt, num_inference_steps=200, audio_length_in_s=4.0).audios[0]
                    print("penis music")

                    wav.write("./AUDIO/temp/temp_gen.wav", rate=16000, data=audio)
                    num_user_samples = len(os.listdir("./AUDIO/user_samples"))
                    self.sample_name_input.insert(index=tk.END,text =f"sample_{num_user_samples}")

            threading.Thread(target=task).start()

        start_pipe()
        self.gen_pbar.configure(text = "Generated!")
        self.after(1000, self.gen_pbar.configure(text = ""))

        

# Redirect tqdm output to a CTkLabel
class CTkLabelRedirector(io.TextIOBase):
    def __init__(self, label):
        super().__init__()
        self.label = label
        self.buffer = ""

    def write(self, message):
        self.buffer += message
        if "\r" in message or "\n" in message:
            lines = self.buffer.strip().splitlines()
            if lines:
                last_line = lines[-1]
                self.label.after(0, lambda: self.label.configure(text=last_line))
            self.buffer = ""

    def flush(self):
        pass