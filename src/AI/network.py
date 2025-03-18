import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

"""
VAE Network with mini-unet diffusion model in between encoder-decoder.

Text embeddings come from Sentence Transformer as part of MiniLM
"""


# --------------------
# U-Net Model for Diffusion
# --------------------
class UNetDiffusion(nn.Module):
    def __init__(self, latent_dim, text_embedding_dim, timesteps=1000):
        super(UNetDiffusion, self).__init__()

        self.timesteps = timesteps

        # Time embedding
        self.time_mlp = nn.Sequential(
            nn.Linear(1, 128),  # (B, 1) -> (B, 128)
            nn.ReLU(),
            nn.Linear(128, latent_dim)  # (B, 128) -> (B, latent_dim)
        )

        # Downsampling Path
        self.down1 = nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1)  # (B, 1, 256, 1) -> (B, 64, 256, 1)
        self.down2 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)  # (B, 64, 256, 1) -> (B, 128, 256, 1)
        self.down3 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1)  # (B, 128, 256, 1) -> (B, 256, 256, 1)

        # Bottleneck (Cross-Attention with Text Embeddings)
        self.cross_attention = nn.MultiheadAttention(embed_dim=latent_dim, num_heads=8)

        # Upsampling Path
        self.up3 = nn.ConvTranspose2d(256, 128, kernel_size=3, stride=1, padding=1)  # (B, 256, 256, 1) -> (B, 128, 256, 1)
        self.up2 = nn.ConvTranspose2d(128, 64, kernel_size=3, stride=1, padding=1)  # (B, 128, 256, 1) -> (B, 64, 256, 1)
        self.up1 = nn.ConvTranspose2d(64, 1, kernel_size=3, stride=1, padding=1)  # (B, 64, 256, 1) -> (B, 1, 256, 1)


    def forward(self, z, text_embedding, t):
        """
        Denoises the latent tensor `z` using U-Net while conditioning on text embeddings.
        """
        # Time embedding
        t_embed = self.time_mlp(t.unsqueeze(1))

        # Encode (Downsample)
        d1 = F.relu(self.down1(z))
        d2 = F.relu(self.down2(d1))
        d3 = F.relu(self.down3(d2))

        # Cross-Attention with Text
        text_embedding = text_embedding.unsqueeze(1)  # Add sequence dim
        attn_output, _ = self.cross_attention(d3.view(1, -1, d3.shape[-1]), text_embedding, text_embedding)
        d3 = d3 + attn_output.view(d3.shape)

        # Decode (Upsample)
        u3 = F.relu(self.up3(d3))
        u2 = F.relu(self.up2(u3))
        u1 = self.up1(u2)

        return u1

# --------------------
# VAE with U-Net Diffusion
# --------------------
class UNetDiffusionVAE(nn.Module):
    def __init__(self, latent_dim=256, text_embedding_dim=128, timesteps=1000):
        super(UNetDiffusionVAE, self).__init__()

        self.latent_dim = latent_dim
        self.text_embedding_dim = text_embedding_dim
        self.timesteps = timesteps

        # Text Encoder (SBERT)
        self.text_encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  

        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(2, 32, kernel_size=(3, 9), stride=(1, 2), padding=(1, 4)),  # (B, 2, 129, 1722) -> (B, 32, 129, 861)
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=(3, 7), stride=(2, 2), padding=(1, 3)),  # (B, 32, 129, 861) -> (B, 64, 65, 431)
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=(3, 5), stride=(2, 2), padding=(1, 2)),  # (B, 64, 65, 431) -> (B, 128, 33, 216)
            nn.ReLU(),
            nn.Conv2d(128, 256, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1)),  # (B, 128, 33, 216) -> (B, 256, 17, 108)
            nn.ReLU(),
            nn.Conv2d(256, 512, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1)),  # (B, 256, 17, 108) -> (B, 512, 9, 54)
            nn.ReLU(),
        )

        self.feature_map_size = 512 * 9 * 54

        # Latent Space
        self.fc_mu = nn.Linear(self.feature_map_size + text_embedding_dim, latent_dim)  # (B, feature_map_size + text_dim) -> (B, latent_dim)
        self.fc_logvar = nn.Linear(self.feature_map_size + text_embedding_dim, latent_dim)  # (B, feature_map_size + text_dim) -> (B, latent_dim)

        # U-Net Diffusion Model
        self.diffusion = UNetDiffusion(latent_dim, text_embedding_dim, timesteps)

        # Decoder
        self.fc_decode = nn.Linear(latent_dim + text_embedding_dim, self.feature_map_size)  # (B, latent_dim + text_dim) -> (B, feature_map_size)

        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(512, 256, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), output_padding=(1, 1)),  # (B, 512, 9, 54) -> (B, 256, 17, 108)
            nn.ReLU(),
            nn.ConvTranspose2d(256, 128, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), output_padding=(1, 1)),  # (B, 256, 17, 108) -> (B, 128, 33, 216)
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, kernel_size=(3, 5), stride=(2, 2), padding=(1, 2), output_padding=(1, 1)),  # (B, 128, 33, 216) -> (B, 64, 65, 431)
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, kernel_size=(3, 7), stride=(2, 2), padding=(1, 3), output_padding=(1, 1)),  # (B, 64, 65, 431) -> (B, 32, 129, 861)
            nn.ReLU(),
            nn.ConvTranspose2d(32, 2, kernel_size=(3, 9), stride=(1, 2), padding=(1, 4), output_padding=(0, 1)),  # (B, 32, 129, 861) -> (B, 2, 129, 1722)
            nn.Sigmoid(),
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
            # Sample latent vector from normal distribution
            z = torch.randn(1, 1, 256, 1).to(text_embedding.device)  # Adjust shape for UNet

            # Apply the diffusion process
            for t in reversed(range(self.timesteps)):
                z = self.diffusion(z, text_embedding, torch.tensor([t]).to(text_embedding.device))

        else:
            # Standard VAE encoding
            mu, logvar = self.encode(x, text_embedding)
            z = self.reparameterize(mu, logvar)
            z = z.view(-1, 1, 256, 1)  # Adjust for UNet input

            # Apply the diffusion process
            for t in reversed(range(self.timesteps)):
                z = self.diffusion(z, text_embedding, torch.tensor([t]).to(text_embedding.device))

        recon = self.decode(z.view(z.shape[0], -1), text_embedding)
        return recon, mu if not generate else None, logvar if not generate else None

# Example: Generate a spectrogram based on a text prompt
model = UNetDiffusionVAE(latent_dim=256, text_embedding_dim=128, timesteps=100)

text_prompt = "A futuristic, robotic soundscape with deep echoes"
generated_spectrogram, _, _ = model(text=text_prompt, generate=True)

print(generated_spectrogram.shape)  # Output shape should be (1, 2, 129, 1722)
