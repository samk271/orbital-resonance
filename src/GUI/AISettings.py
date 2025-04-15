import os
import shutil
import tkinter as tk
from tkinter.colorchooser import askcolor
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

        self.tabview = CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.sample_tab = self.tabview.add("Sample Editor")
        self.sequence_tab = self.tabview.add("Sequence Editor")

        self.sample_editor(self.sample_tab)
        self.sequence_editor(self.sequence_tab)
        

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

        self.generate_button = CTkButton(parent, text="Generate Sound", fg_color="gray25", state="disabled")
        self.generate_button.grid(row=2, column=0, rowspan=3, padx=10)

        self.listbox = CTkListbox(parent, width=320,height=120, hover=True)
        self.listbox.grid(row=1,column=1,rowspan=2,pady=20,padx=10)

        self.sr = 0
        self.signal = []

        # doesnt crash if dataset is not found
        try:
            self.add_wav_to_listbox(listbox=self.listbox, wav_dir="./AUDIO/temp_samples")
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

        self.update_sound_button = CTkButton(parent, text="Crop", width=100, height=20, state="disabled")
        self.update_sound_button.configure(command=lambda: self.update_sound(plot=plot1))
        self.update_sound_button.grid(row=4,column=2,pady=10)

        # creates play sound button todo add function
        self.play_button = CTkButton(parent, text="Play Sound",width=100, height=20,  state="disabled", fg_color="gray25")
        self.play_button.configure(command=lambda: self.play_sound())
        self.play_button.grid(row=4,column=3,pady=10)


        #Create name input box
        self.name_label = CTkLabel(parent,height=10, text="Name your planet")
        self.name_label.grid(row=1, column=4, sticky="n", pady=(20,0))
        self.planet_name_input = CTkTextbox(parent, height=10)
        self.planet_name_input.grid(row=1, column=4, sticky="n",pady=(40))
        self.planet_name_input.insert(index=tk.END,text ="Planet")

        # creates add button todo add function
        self.add_button = CTkButton(parent, text="Save Sample", fg_color="gray25", state="disabled")
        self.add_button.configure(command=lambda: self.add_planet_to_ss())
        self.add_button.grid(row=2, column=4, sticky="s", pady=(0, 20))


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
        self.update_sound_button.configure(state="normal", fg_color=self.select_button.cget("fg_color"))
        

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

        planet_name = self.planet_name_input.get("1.0",'end-1c')

        if not (os.path.isdir(f"./AUDIO/planets/{planet_name}")):
            os.mkdir(f"./AUDIO/planets/{planet_name}")

        shutil.copy("./AUDIO/temp_wav.wav", f"./AUDIO/planets/{planet_name}/{planet_name}.wav")
        self.add_button.configure(state="normal", fg_color=self.select_button.cget("fg_color"))

        
    #Add planet to solar system
    def add_planet_to_ss(self):

        planet_name = self.planet_name_input.get("1.0",'end-1c')

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
        listbox.activate(0)