import base64
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, send_file
import io
import pickle
import math
import os
import cv2
from PIL import Image, ImageTk
import numpy as np
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from diffusers.utils import load_image, make_image_grid
from io import BytesIO
from keras.models import load_model
import torch
from model import build_generator, transform_image

###### controlnet ######

# controlnet = ControlNetModel.from_pretrained(
#     "lllyasviel/sd-controlnet-scribble", use_safetensors=True)
# pipe = StableDiffusionControlNetPipeline.from_pretrained(
#     "runwayml/stable-diffusion-v1-5", controlnet=controlnet, use_safetensors=True)


# def generate_with_controlnet(sketch):
#     image = np.array(sketch)

#     low_threshold = 100
#     high_threshold = 200

#     image = cv2.Canny(image, low_threshold, high_threshold)
#     image = image[:, :, None]
#     image = np.concatenate([image, image, image], axis=2)
#     canny_image = Image.fromarray(image)

#     image = pipe("", image=canny_image, guess_mode=True,
#                  guidance_scale=3.0).images[0]
#     return image

##### CGAN ######
generator = build_generator('generator-150.pth')
def generate_with_cgan(sketch):
    image = transform_image(sketch)
    generated_image = generator(image.unsqueeze(0))
    generated_image = generated_image[0].detach().cpu().permute(1, 2, 0).squeeze().numpy()
    # input_image = sketch.resize((128, 128))
    # input_image_array = np.array(input_image) / 127.5 - 1.
    # model = load_model('gen_150.h5')
    # input_image = np.expand_dims(input_image_array, axis=0)
    # generated_image = model.predict(input_image)[0]
    # generated_image = (0.5 * generated_image + 0.5) * 255.0
    # generated_image = np.clip(generated_image, 0, 255)
    # generated_image = generated_image.astype(np.uint8)
    if np.min(generated_image) < 0:
      generated_image = (generated_image - np.min(generated_image)) * (255 / (np.max(generated_image) - np.min(generated_image)))
    return generated_image

#####################################################################


def models(model, sketch):
    print(type(sketch))
    genImg = ""
    if model == "ControlNet Model":
        # genImg = generate_with_controlnet(sketch)
        return genImg
    elif model == "CGAN Model":
        genImg = generate_with_cgan(sketch)
        return genImg

# def models(model, sketch):
#     return sketch


app = Flask(__name__)


@app.route('/')
def home():
    return render_template("home.html", pagetitle="Home", custom_css="css/home.css")


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if request.method == 'POST':
        model = request.form['model']
        action = request.form['action']

        if action == 'sketch':
            return redirect(url_for('sketching', model=model, type=action))
        elif action == 'upload':
            return redirect(url_for('uploading', model=model, type=action))

    return render_template('menu.html', custom_css='css/menu.css', pagetitle='Menu')


@app.route("/menu/sketching", methods=['GET', 'POST'])
def sketching():
    model = request.args.get('model', None)
    type = request.args.get('type', None)
    return render_template("sketching.html", pagetitle="sketching", custom_css="css/style.css", model=model, type=type, image_path="test")


@app.route("/menu/uploading", methods=['GET', 'POST'])
def uploading():
    model = request.args.get('model', None)
    type = request.args.get('type', None)
    return render_template("uploading.html", pagetitle="uploading", custom_css="css/style.css", model=model, type=type, image_path="test")


@app.route("/generate", methods=['GET', 'POST'])
def generate():
    model = request.args.get('model', None)
    action = request.args.get('action', None)
    type = request.args.get('type', None)
    generated_image_path = 'static/images/genImages/gen.png'

    if action == 'generate':

        if os.path.exists(generated_image_path):
            if type == "sketch":
                image_data = request.form['canvasImage']
                header, encoded = image_data.split(",", 1)
                sketch = base64.b64decode(encoded)
                sketch = Image.open(BytesIO(sketch))
                white_background = Image.new('RGB', sketch.size, (255, 255, 255))

                # Convert the sketch image to 'RGBA' if it's not already
                sketch = sketch.convert('RGBA')

                # Composite the sketch onto the white background
                composite = Image.alpha_composite(white_background.convert('RGBA'), sketch)
                composite.save('static/images/genImages/sketch.png')

                # if u want to pass an image to the model then this will work .. if base64 is wanted then use "encoded" var instead
                genImg = models(model, composite)
                # if uncommented >>> will override the gen.png with the sketch .. uncomment when model returns an image not the sketch
                Image.fromarray(genImg.astype(np.uint8)).save(generated_image_path)

                return render_template("sketching.html", pagetitle="Generation", custom_css="css/style.css", model=model, image_path=generated_image_path, type=type)

            elif type == "upload":
                if 'file' not in request.files:
                    return jsonify({"error": "No file part in the request"}), 400

                file = request.files['file']
                if file.filename == '':
                    return jsonify({"error": "No selected file"}), 400

                if file:
                    file_path = os.path.join(
                        "static/images/genImages", "sketch.png")
                    file.save(file_path)
                    # now the file var holds the image uploaded and saved .. use it to feed the model

                try:
                    sketch = Image.open("static/images/genImages/sketch.png")

                except IOError:
                    print(f"Unable to load image from path")
                    
                # if u want to pass an image to the model then this will work .. if base64 is wanted then use "encoded" var instead
                genImg = models(model, sketch)
                print(genImg.shape)
                # if uncommented >>> will override the gen.png with the sketch .. uncomment when model returns an image not the sketch
                Image.fromarray(genImg.astype(np.uint8)).save(generated_image_path)

                return render_template("uploading.html", pagetitle="Generation", custom_css="css/style.css", model=model, image_path=generated_image_path, type=type)

        else:
            return 'Error: Generated image not found.'

    elif action == 'download':
        if os.path.exists(generated_image_path):
            # Sending the file for download
            return send_file(generated_image_path, mimetype='image/png', as_attachment=True)
        else:
            return 'Error: Generated image not found.'


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    return render_template("contact.html", pagetitle="contact", custom_css="css/style.css")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9999)
