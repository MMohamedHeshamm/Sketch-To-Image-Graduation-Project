import gc
import os
import cv2
import torch
import numpy as np
import pandas as pd
import torch.nn as nn
from PIL import Image
import matplotlib.pyplot as plt

from torch.optim import Adam
from torchvision.transforms import ToTensor
from diffusers import StableDiffusionPipeline
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from diffusers.utils import load_image, make_image_grid

dataset_path = r"C:\Users\m3394\ourDataSet\our_dataset"
dataset = []

for class_dir in sorted(os.listdir(dataset_path)):
    class_folder_path = os.path.join(dataset_path, class_dir)
    image_folder_path = os.path.join(class_folder_path, "images")
    sketches_folder_path = os.path.join(class_folder_path, "sketches")

    # Limit the number of images and sketches for butterfly and camel classes
    max_images = 20
    cnt = 0
    for i, filename in enumerate(sorted(os.listdir(image_folder_path))):
        if i >= max_images:
            break  # Stop after reaching the limit
        cnt = cnt + 1
        image_path = os.path.join(image_folder_path, filename)
        image = load_image(image_path)
        image.resize((512, 512))
        directory, filename = os.path.split(image_path)
        name, extension = os.path.splitext(filename)
        sketch_path = os.path.join(sketches_folder_path, name + '.png')
        sketch = load_image(sketch_path)
        sketch.resize((512, 512))
        prompt = class_dir
        dataset.append((image, sketch, prompt, i))
    print("found " + str(cnt) + " in class " + class_dir)

controlnet = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-scribble", use_safetensors=True)
pipe = StableDiffusionControlNetPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", controlnet=controlnet,
                                                         use_safetensors=True).to("cuda")

pipe.safety_checker = lambda images, **kwargs: (images, [False] * len(images))

df = pd.DataFrame(dataset, columns=["Image", "Sketch", "Prompt", "Index"])

shuffled_df = df.sample(frac=1).reset_index(drop=True)

shuffled_dataset = list(zip(shuffled_df["Image"], shuffled_df["Sketch"], shuffled_df["Prompt"], shuffled_df["Index"]))

for _, _, p, i in shuffled_dataset:
    print(str(p) + " " + str(i))

output_base_folder = r'C:\Users\m3394\Downloads\training\training3'

for i in range(30):
    output_folder = os.path.join(output_base_folder, str(i))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

loss_fn = nn.MSELoss()
optimizer = Adam(pipe.controlnet.parameters(), lr=1e-3)

for epoch in range(30):  # Run for 40 epochs
    print("epoch " + str(epoch))

    # Create a folder for each epoch
    epoch_folder = os.path.join(output_base_folder, str(epoch))
    os.makedirs(epoch_folder, exist_ok=True)

    for image, sketch, protmpt, idx in shuffled_dataset:
        original_sketch = sketch
        sketch = np.array(original_sketch)
        low_threshold = 100
        high_threshold = 200
        sketch = cv2.Canny(sketch, low_threshold, high_threshold)
        sketch = sketch[:, :, None]
        sketch = np.concatenate([sketch, sketch, sketch], axis=2)
        canny_sketch = Image.fromarray(sketch)
        new_image = pipe("", image=canny_sketch, guess_mode=True, guidance_scale=3.0).images[0]
        new_image_path = os.path.join(epoch_folder, protmpt + f"generated_image_{idx}.png")
        new_image.save(os.path.join(epoch_folder, protmpt + f"generated_image_{idx}.png"))


        new_image = new_image.resize((512, 512))
        new_image = np.array(new_image)
        new_image = new_image[:, :, :3]
        new_image = Image.fromarray(new_image)
        image = image.resize((512, 512))
        image = np.array(image)
        image = image[:, :, :3]
        image = Image.fromarray(image)
        to_tensor = ToTensor()
        new_image_tensor = to_tensor(new_image)
        image_tensor = to_tensor(image)
        new_image_tensor = to_tensor(new_image).requires_grad_()
        image_tensor = to_tensor(image).requires_grad_()
        loss = loss_fn(new_image_tensor, image_tensor)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # Save the model after every 10 epochs
    if (epoch + 1) % 10 == 0:
        torch.save(pipe.controlnet.state_dict(), os.path.join(output_base_folder, f"model_epoch_{epoch}.pt"))