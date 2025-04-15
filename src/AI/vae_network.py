import os
import torch
from tqdm.auto import tqdm
from torch.utils.data import DataLoader
from diffusers import AutoencoderKL
from accelerate import Accelerator
import torch.nn.functional as F
#from audio_loss_functions import MultiResolutionSTFTLoss


class SpectrogramVAETrainer:
    def __init__(self, dataset, 
                 batch_size=16, 
                 lr=1e-4, latent_channels=256, 
                 reg_mrstft = 1.0, reg_kl = 0.1):

        self.reg_mrstft = reg_mrstft
        self.reg_kl = reg_kl
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        self.model = AutoencoderKL(
            in_channels=2,
            out_channels=2,
            latent_channels=latent_channels,
            scaling_factor=0.18215,
        )

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.accelerator = Accelerator()

        #Prepare to use accelerator class
        self.model, self.dataloader, self.optimizer = self.accelerator.prepare(
            self.model, self.dataloader, self.optimizer
        )

    def train(self, num_epochs=10, save_path=None):
        self.model.train()

        for epoch in range(num_epochs):
            total_loss = 0.0
            pbar = tqdm(self.dataloader, desc=f"Epoch {epoch+1}/{num_epochs}")
            for batch in pbar:
                batch = batch.to(self.accelerator.device)

                # Encode and sample from latent
                posterior = self.model.encode(batch).latent_dist
                latents = posterior.sample()
                latents = latents * self.model.config.scaling_factor

                # Decode
                recon = self.model.decode(latents).sample

                # Compute losses
                recon_loss = F.mse_loss(recon, batch)
                kl_loss = posterior.kl().mean()
                loss = recon_loss + kl_loss

                self.optimizer.zero_grad()
                self.accelerator.backward(loss)
                self.optimizer.step()

                pbar.set_postfix(loss=loss.item())

                total_loss += loss.item()

            avg_loss = total_loss / len(self.dataloader)
            print(f"Epoch {epoch+1}/{num_epochs} | Loss: {avg_loss:.4f}")
            # Save model after each epoch if path is provided
            if save_path:
                os.makedirs(save_path, exist_ok=True)
                torch.save(self.model.state_dict(), os.path.join(save_path, f"unet_epoch_{epoch+1}.pt"))

    def encode(self, spectrogram_batch):
        self.model.eval()
        with torch.no_grad():
            spectrogram_batch = spectrogram_batch.to(self.device)
            posterior = self.model.encode(spectrogram_batch).latent_dist
            return posterior.sample() * self.model.config.scaling_factor

    def decode(self, latents):
        self.model.eval()
        with torch.no_grad():
            latents = latents.to(self.device)
            return self.model.decode(latents).sample
        
    def load_model(self, checkpoint_path):
        self.model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
