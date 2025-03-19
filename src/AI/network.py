import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

"""
VAE Network for spectrogram generation.

Text embeddings come from Sentence Transformer as part of MiniLM
"""

class GenerativeCVAE(nn.Module):
    def __init__(self, latent_dim=256, text_embedding_dim=128):
        super(GenerativeCVAE, self).__init__()

        self.latent_dim = latent_dim
        self.text_embedding_dim = text_embedding_dim

        # Text encoder (SBERT)
        self.text_encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  

        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(2, 32, kernel_size=(3, 9), stride=(1, 2), padding=(1, 4)),  # (2, 129, 1722) → (32, 129, 861)
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=(3, 7), stride=(2, 2), padding=(1, 3)),  # (64, 65, 431)
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=(3, 5), stride=(2, 2), padding=(1, 2)),  # (128, 33, 216)
            nn.ReLU(),
            nn.Conv2d(128, 256, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1)),  # (256, 17, 108)
            nn.ReLU(),
            nn.Conv2d(256, 512, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1)),  # (512, 9, 54)
            nn.ReLU(),
        )

        self.feature_map_size = 512 * 9 * 54

        # Fully connected layers for latent space
        self.fc_mu = nn.Linear(self.feature_map_size + text_embedding_dim, latent_dim)
        self.fc_logvar = nn.Linear(self.feature_map_size + text_embedding_dim, latent_dim)

        # Decoder
        self.fc_decode = nn.Linear(latent_dim + text_embedding_dim, self.feature_map_size)

        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(512, 256, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), output_padding=(1, 1)),  # (256, 17, 108)
            nn.ReLU(),
            nn.ConvTranspose2d(256, 128, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), output_padding=(1, 1)),  # (128, 33, 216)
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, kernel_size=(3, 5), stride=(2, 2), padding=(1, 2), output_padding=(1, 1)),  # (64, 65, 431)
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, kernel_size=(3, 7), stride=(2, 2), padding=(1, 3), output_padding=(1, 1)),  # (32, 129, 861)
            nn.ReLU(),
            nn.ConvTranspose2d(32, 2, kernel_size=(3, 9), stride=(1, 2), padding=(1, 4), output_padding=(0, 1)),  # (2, 129, 1722)
            nn.Sigmoid(),  # Normalize output to [0,1]
        )

    def encode_text(self, text):
        """Encodes text prompt into a fixed-size embedding."""
        with torch.no_grad():
            text_embedding = self.text_encoder.encode([text], convert_to_tensor=True)
        return text_embedding

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def encode(self, x, text_embedding):
        x = self.encoder(x)
        x = torch.flatten(x, start_dim=1)
        x = torch.cat([x, text_embedding], dim=1)  
        mu = self.fc_mu(x)
        logvar = self.fc_logvar(x)
        return mu, logvar

    def decode(self, z, text_embedding):
        z = torch.cat([z, text_embedding], dim=1)  
        x = self.fc_decode(z)
        x = x.view(-1, 512, 9, 54)
        x = self.decoder(x)
        return x

    def forward(self, x=None, text=None, generate=False):
        text_embedding = self.encode_text(text)  

        if generate:
            # Sampling a random latent vector for generation
            z = torch.randn(1, self.latent_dim).to(text_embedding.device)
        else:
            # Standard VAE forward pass
            mu, logvar = self.encode(x, text_embedding)
            z = self.reparameterize(mu, logvar)

        recon = self.decode(z, text_embedding)
        return recon, mu if not generate else None, logvar if not generate else None

    def loss_function(self, recon_x, x, mu, logvar):
        recon_loss = F.mse_loss(recon_x, x, reduction='sum')
        kl_div = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        return recon_loss + kl_div, recon_loss, kl_div

# # Example: Generate a spectrogram based on a text prompt
# model = GenerativeCVAE(latent_dim=256, text_embedding_dim=128)

# text_prompt = "A deep bass sound with a smooth ambient background"
# generated_spectrogram, _, _ = model(text=text_prompt, generate=True)

# print(generated_spectrogram.shape)  # Output shape should be (1, 2, 129, 1722)
