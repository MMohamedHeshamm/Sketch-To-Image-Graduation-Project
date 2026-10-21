import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
from keras.models import load_model
import matplotlib.pyplot as plt
import time
import threading

class ImageGeneratorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Sketchy HeiHei")
        
        # Set window size and position
        window_width = 550
        window_height = 350
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.model = load_model("C:\Users\m3394\OneDrive\Desktop\GP\\flask\\FlaskApp\CGAN ehab demo\gen_150.h5")  # Load your .h5 generative model
        
        self.selected_image_label = tk.Label(self.master)
        self.selected_image_label.pack(side="left", padx=10)
        self.selected_image_label.pack_propagate(0)
        
        self.generated_image_label = tk.Label(self.master)
        self.generated_image_label.pack(side="right", padx=10)
        self.generated_image_label.pack_propagate(0)
        
        self.selected_image_display = None
        
        self.select_button = tk.Button(self.master, text="Select Image", command=self.select_image)
        self.select_button.place(x=window_width//2, y=window_height-30, anchor="center")
        
    def select_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            self.selected_image_display = image.resize((256, 256))  # Displayed selected image size
            self.show_selected_image(self.selected_image_display)
            # Prepare input image for model (resize to 128x128)
            input_image = image.resize((128, 128))
            input_image_array = np.array(input_image) / 127.5 - 1.
            
            # Create a thread to generate and display the image
            t = threading.Thread(target=self.generate_and_show_image, args=(input_image_array,))
            t.start()
    
    def generate_and_show_image(self, input_image):
        # Generate the image
        generated_image = self.generate_image(input_image)
        # Show the generated image
        self.show_generated_image(generated_image)
    
    def generate_image(self, input_image):
        input_image = np.expand_dims(input_image, axis=0)
        generated_image = self.model.predict(input_image)[0]
        # plt.imshow(0.5 * generated_image + 0.5)
        # plt.show()
        generated_image = (0.5 * generated_image + 0.5) * 255.0
        generated_image = np.clip(generated_image, 0, 255)
        # generated_image *= 255.0

        generated_image = generated_image.astype(np.uint8)
        return generated_image
    
    def show_selected_image(self, image):
        photo = ImageTk.PhotoImage(image)
        self.selected_image_label.configure(image=photo)
        self.selected_image_label.image = photo
    
    def show_generated_image(self, image):
        image = Image.fromarray(image)
        image = image.resize((256, 256))
        photo = ImageTk.PhotoImage(image)

        # Update the generated image label
        self.generated_image_label.configure(image=photo)
        self.generated_image_label.image = photo



if __name__ == "__main__":
    root = tk.Tk()
    app = ImageGeneratorApp(root)
    root.mainloop()
