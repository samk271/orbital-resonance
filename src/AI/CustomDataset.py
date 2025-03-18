import os
import torch
import random
import numpy as np
from torch.utils.data import Dataset

"""
Dataset returns 4.87 second intervals from the clotho dataset

129x1722 images

For more info on why this specific second interval was chosen see
comment at bottom of file
"""

class CustomDataset(Dataset):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def __len__(self):
        count = 0
        # Iterate directory
        for path in os.listdir(self.root_dir):
            # check if current path is a file
            if os.path.isfile(os.path.join(self.root_dir, path)):
                count += 1
        return count
    
     #Transform complex image tensor into two channel image tensor
    def preprocess_complex_image(image):
        real_part = image.real
        imag_part = image.imag
        stacked = np.stack([real_part, imag_part], axis=0)  # Shape: (2, H, W)
        return torch.tensor(stacked, dtype=torch.float32)
    
    #Transform two channel image tensor into complex image tensor
    def postprocess_complex_output(output):
        real_part = output[0].cpu().detach().numpy()
        imag_part = output[1].cpu().detach().numpy()
        return real_part + 1j * imag_part


    def __getitem__(self, idx):
        file_path = os.listdir(self.root_dir)[idx]

        uncropped_data = np.genfromtxt(os.path.join(self.root_dir, file_path),dtype=np.complex128, delimiter=",", comments="#")

        num_columns = uncropped_data.shape[1]
        
        start_index = random.randint(0, num_columns - 1722) #Find random starting index

        cropped_spectrogram = uncropped_data[:,start_index:start_index+1722] #Crop spectrogram to 5 second interval

        two_channel_tensor = self.preprocess_complex_image(cropped_spectrogram)

        return two_channel_tensor

"""
Maximum wav file length was 30 seconds, full spectrograms are 129x10337
too large to train on, so ~5 second intervals were chosen instead.

1722/10337 * 30 seconds ~= 5
"""