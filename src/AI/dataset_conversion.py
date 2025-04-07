"""
This script is for converting the captions for the dataset into text embeddings.
"""

import os
import tqdm
import json
import numpy as np
from scipy import signal
from scipy.io import wavfile
import csv
from sentence_transformers import SentenceTransformer

data_dir = "./dataset/clotho/"

text_encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

#Load captions as a dictionary object
with open(os.path.join(data_dir,"clotho_captions_evaluation.csv"), mode='r') as infile:
    reader = csv.reader(infile)
    captions = {row[0][:-4]:text_encoder.encode(sentences=row[1:]).tolist() for row in reader}

file_path = "./dataset/clotho/clotho_embedded_captions_evaluation.json"
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(captions, file, ensure_ascii=False, indent=4)