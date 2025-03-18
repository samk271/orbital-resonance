from customtkinter import CTkFrame, CTkLabel, CTkSlider, CTkButton, CTkTabview, CTkComboBox
from tkinter import Canvas 


class PlanetSettings(CTkFrame):
    """
    The class that will handle the settings menu that controls the planet settings
    """

    def __init__(self, *args, **kwargs):
        """
        creates the settings window

        :param args: the arguments to be passed to the super class
        :param kwargs: the key word arguments to be passed to the super class
        """

        super().__init__(*args, **kwargs)
        self.tabview = CTkTabview(self)
        self.tabview.pack(fill="both" , expand= True, padx=10, pady= 10)

        #tabs for different settings
        self.sun_tab= self.tabview.add("Sun Settings")

        #sun 
        self.sun_settings(self.sun_tab)
    
    def sun_settings(self, parent):
        "UI for sun settings"
        
        self.sun_label = CTkLabel(parent, text="Sun Settings",font=("Arial",
                                                                    18, "bold"))
        self.sun_label.pack(pady=5, padx=10)

        #slider for the size
        self.size_label = CTkLabel(parent, text="Size:")
        self.size_label.pack(pady=(10,2))
        self.size_slider = CTkSlider(parent, from_=0, to=100)
        self.size_slider.pack(pady=2, padx=10, fill="x")


        #select shape
        self.shape = CTkLabel(parent,text="Shape:")
        self.shape.pack(pady=(10, 0))
        self.shape_options = CTkComboBox (parent, values=["cloud", "circle","square", 
                                                          "Triangle", "Rectangle"])
        self.shape_options.pack()


        #choose color
        self.color_label = CTkLabel (parent, text="Color:")
        self.color_label.pack(pady=(10, 0))

        #Color choices
        self.color_frame =CTkFrame(parent, fg_color= "transparent")
        self.color_frame.pack(pady=5)
        self.colors = ["Yellow", "Green", "Blue", "Orange", "Purple","Red"]

        self.color_buttons = {}      

        for color in self.colors:
            button = Canvas(self.color_frame, width=30, height=30, bg=color,highlightthickness=0)
            button.bind("<Button-1>", lambda e, c=color: self.change_sun_color(c))  
            button.bind("<Enter>", lambda e, b=button: b.config(width=35, height=35))
            button.bind("<Leave>", lambda e, b=button: b.config(width=30, height=30)) 
            button.pack(side="left", padx=5)
            self.color_buttons[color] = button

        # apply button
        self.apply_button = CTkButton(self, text=" Apply Sun changes", 
                                      command=self.apply_settings)
        self.apply_button.pack(pady=10)

        #reset button 
        self.reset_button = CTkButton(parent, text="Reset to Default", fg_color="gray", 
                                      command=self.reset_settings)
        self.reset_button.pack(pady=5)

        #save button
        self.save_button = CTkButton(parent, text="Save",command=self.save_settings)
        self.save_button.pack(pady=10)

    def change_sun_color(self):
        "will be implemented later"
    
    def save_settings(self):
        "will be implemented later"

    def apply_settings(self):
        "will be implemented later"

    def reset_settings(self):
        "will be implemented later"
