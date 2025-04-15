import numpy as np
from CustomDatasetNoText import CustomDatasetNoText
from vae_network import SpectrogramVAETrainer as vae_net

for i in range(4):
    cd = CustomDatasetNoText(root_dir="./dataset/clotho")

    vae = vae_net(dataset=cd, batch_size=2)
    vae.train(save_path=f"trained_vae_{i}")