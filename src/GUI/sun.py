from customtkinter import CTkButton, CTkFrame, CTkSlider, CTkLabel, StringVar

class SunSettings(CTkFrame):
    "This class will handle sun settings menu"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(width = 200, height = 180)
        self.pack_propagate(False)

        #The title:
        self.label_text = StringVar(value = "Sun Settings")
        self.label = CTkLabel(self, textvariable = self.label_text, font = ("Arial", 18, "bold"))
        self.label.pack(pady = 5, padx = 10)

        #Size Slider
        self.size_label = CTkLabel(self, text = "size: ")
        self.size_label.pack(pady= (10, 2))
        self.size_slider = CTkSlider(self,from_ = 0, to = 100)
        self.size_slider.pack(pady = 2, padx = 10, fill = "x")

        # Brightness
        self.size_label = CTkLabel(self, text = "Brighness: ")
        self.size_label.pack(pady= (10, 2))
        self.size_slider = CTkSlider(self,from_ = 0, to = 100)
        self.size_slider.pack(pady = 2, padx = 10, fill = "x")

        #apply button
        self.apply_button = CTkButton(self, text = " Apply changes")
        self.apply_button.pack(pady = 10)
        
        #seperator line
        self.separator = CTkFrame(self, height=2, fg_color="gray")
        self.separator.pack(fill="x", pady=5, padx=10)




