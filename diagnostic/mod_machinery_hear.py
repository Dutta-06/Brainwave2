import torch
import torch.nn as nn
import torch.nn.functional as F
import sounddevice as sd
import numpy as np
import librosa
import os

# --- 1. Define the PyTorch Model Architecture ---
class AudioCNN(nn.Module):
    def __init__(self, num_classes=3):
        super(AudioCNN, self).__init__()
        # A tiny CNN for edge devices
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        # Assuming input MFCC size results in a flattened size of 32 * 10 * 20 (approx)
        # In a real scenario, calculate this dynamic dimension based on input shape
        self.fc1 = nn.Linear(32 * 10 * 20, 128) 
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(x.size(0), -1) # Flatten
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class TractorDoctor:
    def __init__(self, model_path="tractor_net.pth"):
        self.sample_rate = 22050
        self.labels = {0: "Healthy", 1: "Belt Slippage", 2: "Engine Knock"}
        
        # Initialize Model
        self.model = AudioCNN(num_classes=len(self.labels))
        
        # Load weights if they exist, else warn (safe for dev)
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            print("[Mechanic] PyTorch weights loaded.")
        else:
            print("[Mechanic] Warning: No weights found. Using random init (Mock Mode).")
        
        self.model.eval() # Set to inference mode

    def record_clip(self, duration=5):
        print(f"[Mechanic] Listening ({duration}s)...")
        recording = sd.rec(int(duration * self.sample_rate), 
                        samplerate=self.sample_rate, channels=1)
        sd.wait()
        return recording.flatten()

    def preprocess(self, audio_array):
        """Convert audio to Mel-Spectrogram tensor."""
        # Extract Mel Spectrogram
        S = librosa.feature.melspectrogram(y=audio_array, sr=self.sample_rate, n_mels=40)
        S_dB = librosa.power_to_db(S, ref=np.max)
        
        # Resize/Pad to fixed size for CNN (e.g., 40x80)
        # For this demo, we just crop/pad to a fixed length
        target_len = 80
        if S_dB.shape[1] > target_len:
            S_dB = S_dB[:, :target_len]
        else:
            pad_width = target_len - S_dB.shape[1]
            S_dB = np.pad(S_dB, ((0, 0), (0, pad_width)))

        # Convert to PyTorch Tensor: Shape (Batch, Channels, Height, Width)
        tensor = torch.tensor(S_dB, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        return tensor

    def diagnose(self, audio_data):
        input_tensor = self.preprocess(audio_data)
        
        with torch.no_grad():
            outputs = self.model(input_tensor)
            _, predicted = torch.max(outputs, 1)
            
        confidence = torch.nn.functional.softmax(outputs, dim=1)[0][predicted].item()
        diagnosis = self.labels[predicted.item()]
        
        return diagnosis, confidence

if __name__ == "__main__":
    doc = TractorDoctor()
    
    # 1. Record
    audio = doc.record_clip(duration=3)
    
    # 2. Diagnose
    # (Note: Will give random results until you train 'tractor_net.pth')
    result, conf = doc.diagnose(audio)
    print(f"\nDiagnosis: {result} (Confidence: {conf:.2f})")