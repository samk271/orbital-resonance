import torch
from torch import nn
from torch.utils.data import DataLoader
from diffusers import UNet2DConditionModel, DDPMScheduler
from tqdm.auto import tqdm
import os


class SpectrogramDiffusionTrainer:
    def __init__(
        self,
        image_shape=(2, 129, 861),  # (C, H, W)
        text_embedding_dim=384,
        learning_rate=1e-4,
        device="cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.device = device

        print(device)

        # Initialize UNet model
        self.model = UNet2DConditionModel(
            sample_size=image_shape[1:],  # (H, W)
            in_channels=image_shape[0],
            out_channels=image_shape[0],
            layers_per_block=2,
            block_out_channels=(128, 256, 512, 512),
            down_block_types=(
                "DownBlock2D", "DownBlock2D", "DownBlock2D", "DownBlock2D"
            ),
            up_block_types=(
                "UpBlock2D", "UpBlock2D", "UpBlock2D", "UpBlock2D"
            ),
            cross_attention_dim=text_embedding_dim,
        ).to(self.device)

        # Diffusion noise scheduler
        self.noise_scheduler = DDPMScheduler(num_train_timesteps=1000)

        # Optimizer
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)

        # Loss function
        self.loss_fn = nn.MSELoss()

    def train(self, dataset, batch_size=4, epochs=10, save_path=None):
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        self.model.train()
        for epoch in range(epochs):
            pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}")
            count = 0
            for batch in pbar:
                spectrograms = batch["spectrogram"].to(self.device)  # shape: (B, 2, 129, 861)
                text_embeddings = batch["text_embedding"].to(self.device)  # shape: (B, 384)

                # Sample random noise and timesteps
                noise = torch.randn_like(spectrograms)
                timesteps = torch.randint(0, self.noise_scheduler.config.num_train_timesteps, (spectrograms.shape[0],), device=self.device).long()

                # Add noise to spectrograms
                noisy_spectrograms = self.noise_scheduler.add_noise(spectrograms, noise, timesteps)

                # Predict the noise
                # Reshape embeddings to (B, 1, 384)

                try:
                    text_embeddings = text_embeddings.unsqueeze(1)
                    noise_pred = self.model(sample = noisy_spectrograms, timestep = timesteps, encoder_hidden_states=text_embeddings).sample

                except RuntimeError as e:
                    if "CUDA out of memory" in str(e):
                        print("💥 CUDA OOM! Try reducing batch size.")
                    else:
                        raise

                # Compute loss
                loss = self.loss_fn(noise_pred, noise)

                # Backpropagation
                self.optimizer.zero_grad(set_to_none=True)
                loss.backward()
                self.optimizer.step()
                pbar.set_postfix(loss=loss.item())


            # Save model after each epoch if path is provided
            if save_path:
                os.makedirs(save_path, exist_ok=True)
                torch.save(self.model.state_dict(), os.path.join(save_path, f"unet_epoch_{epoch+1}.pt"))

    @torch.no_grad()
    def predict(self, text_embedding, num_inference_steps=50):
        self.model.eval()
        text_embedding = text_embedding.to(self.device).unsqueeze(0).unsqueeze(1)  # Add batch dimension

        # Start from pure noise
        shape = (1, 2, 129, 861)
        sample = torch.randn(shape).to(self.device)

        for t in tqdm(self.noise_scheduler.timesteps[:num_inference_steps]):
            # Predict the noise
            noise_pred = self.model(sample=sample, timestep=t, encoder_hidden_states=text_embedding).sample

            # Remove noise according to the scheduler
            sample = self.noise_scheduler.step(noise_pred, t, sample).prev_sample

        return sample.squeeze(0).cpu()  # Remove batch dimension

    def load_model(self, checkpoint_path):
        self.model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
