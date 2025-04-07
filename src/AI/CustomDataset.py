import os
import csv
import json
import torch
import random
import numpy as np
from torch.utils.data import Dataset
from sentence_transformers import SentenceTransformer

"""
Dataset returns 5 second intervals from the clotho dataset

2x129x861 images

For more info on why this specific second interval was chosen see
comment at bottom of file
"""

class CustomDataset(Dataset):
    def __init__(self, root_dir, train=True):
        print("Loading captions")
        self.text_encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        if (train):
            self.data_dir = os.path.join(root_dir, "develop_spectro")
            #Load captions as a dictionary object
            with open(os.path.join(root_dir, "clotho_embedded_captions_development.json"), 'r', encoding='utf-8') as file:
                self.captions = json.load(file)
        else:
            self.data_dir = os.path.join(root_dir, "eval_spectro")
            #Load captions as a dictionary object
            with open(os.path.join(root_dir, "clotho_embedded_captions_evaluation.json"), 'r', encoding='utf-8') as file:
                self.captions = json.load(file)
        print("Done.")
    def __len__(self):
        count = 0
        # Iterate directory
        for path in os.listdir(self.data_dir):
            # check if current path is a file
            if os.path.isfile(os.path.join(self.data_dir, path)):
                count += 1
        return count
    
     #Transform complex image tensor into two channel image tensor
    def preprocess_complex_image(self, image):
        real_part = image.real
        imag_part = image.imag
        stacked = np.stack([real_part, imag_part], axis=0)  # Shape: (2, H, W)
        return torch.tensor(stacked, dtype=torch.float32)
    
    #Transform two channel image tensor into complex image tensor
    def postprocess_complex_output(self, output):
        real_part = output[0].cpu().detach().numpy()
        imag_part = output[1].cpu().detach().numpy()
        return real_part + 1j * imag_part


    def __getitem__(self, idx):
        file_name = os.listdir(self.data_dir)[idx]

        #Find caption for index
        caption_list = self.captions[file_name[:-8]]
        caption = torch.tensor(caption_list[random.randint(0,4)])

        uncropped_data = np.genfromtxt(os.path.join(self.data_dir, file_name),dtype=np.complex128, delimiter=",", comments="#")
        num_columns = uncropped_data.shape[1]
        start_index = random.randint(0, num_columns - 861) #Find random starting index
        cropped_spectrogram = uncropped_data[:,start_index:start_index+861] #Crop spectrogram to 2.5 second interval

        two_channel_tensor = self.preprocess_complex_image(cropped_spectrogram)

        return {"spectrogram": two_channel_tensor, "text_embedding": caption}

"""
Maximum wav file length was 30 seconds, full spectrograms are 129x10337
too large to train on, so ~2.5 second intervals were chosen instead.

861/10337 * 30 seconds ~= 2.5
"""