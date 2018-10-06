# Import all the required things
from __future__ import division, print_function
import sys
import os
import glob
import re
import numpy as np
import cv2
import string
import random

# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

# Image Utils
from PIL import Image
from io import BytesIO
import base64

# define the configuration dictionary
CONFIG = {
    # define the set of class labels (these were derived from the
    # label binarizer from the previous post)
    "labels": ["Bulbasaur", "Charmander", "Mewtwo", "Pikachu", "Squirtle"]
}

# Define a flask app
app = Flask(__name__)

# Model saved with Keras model.save()
MODEL_PATH = './models/pokedex.model'

# Load your trained model
model = load_model(MODEL_PATH)
model._make_predict_function()          # Necessary
print('Model loaded. Start serving...')

# You can also use pretrained model from Keras
# Check https://keras.io/applications/
#from keras.applications.resnet50 import ResNet50
#model = ResNet50(weights='imagenet')
#print('Model loaded. Check http://127.0.0.1:5000/')

# Generates random strings of length 10
def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))


def model_predict(img_path, model):
    #img = image.load_img(img_path, target_size=(224, 224))
    #img = cv2.LoadImage(img_path)
    
    # Read the image and convert it to right size
    img = cv2.imread(img_path)
    img = cv2.resize(img, (96, 96))
    img = img.astype("float") / 255.0
    
    # Preprocessing the image
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)

    # Try predicting the pokemon using the trained model
    preds = model.predict(x)
    return preds


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = Image.open(BytesIO(base64.b64decode(request.data)))

        # Save the file to ./uploads
        basepath = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(basepath, 'uploads/')

        file_path += random_string_generator() + '.png'
        print(file_path)
        print(basepath)
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)

        # Process your result for human
        out = CONFIG["labels"][np.argmax(preds)]    # The right label for the pokemon
        #print(preds)
        print(out)  # print the right label to the console
        return out
    return None


if __name__ == '__main__':
    # Serve the app with gevent
    #app.run(host='0.0.0.0', ssl_context='adhoc')
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
