import torch
from torchvision import models, transforms
from PIL import Image
import os

class CropDoctor:
    def __init__(self, use_optimized_model=True):
        print("[Vision] Initializing Crop Doctor...")
        
        # 1. Load Model Architecture
        # MobileNetV3 is ~5MB (Fast). ResNet50 is ~100MB (Slow).
        # We use MobileNet to respect the "Low-End Phone" constraint.
        if use_optimized_model:
            self.model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)
        else:
            self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            
        self.model.eval() # Inference Mode
        
        # 2. Define Image Preprocessing (Standard for ImageNet models)
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                std=[0.229, 0.224, 0.225]),
        ])
        
        # 3. Load Labels (In a real app, these would be plant diseases)
        # For this hackathon demo, we use ImageNet classes.
        # You would fine-tune this on a 'PlantVillage' dataset.
        with open("imagenet_classes.txt", "r") as f:
            self.labels = [line.strip() for line in f.readlines()]
            
        print("[Vision] Model Loaded on CPU.")

    def diagnose(self, image_path):
        """
        Diagnoses the disease from an image file.
        """
        if not os.path.exists(image_path):
            return "Error: Image not found."

        # Load and Preprocess
        input_image = Image.open(image_path).convert('RGB')
        input_tensor = self.preprocess(input_image)
        input_batch = input_tensor.unsqueeze(0) # Create mini-batch

        # Inference (No GPU needed for single image)
        with torch.no_grad():
            output = self.model(input_batch)
            
        # Get Top Prediction
        probabilities = torch.nn.functional.softmax(output[0], dim=0)