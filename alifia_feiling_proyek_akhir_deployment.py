# -*- coding: utf-8 -*-
"""Alifia Feiling - Proyek Akhir Deployment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qtQgOkkQpggY6uZsqI2-iWfMFJ7waouu
"""

!pip install -q kaggle

from google.colab import files
files.upload()

!mkdir -p ~/.kaggle

!cp kaggle.json ~/.kaggle/

!chmod 600 ~/.kaggle/kaggle.json

!ls ~/.kaggle

!kaggle datasets download -d madisona/translated-animals10

!mkdir animals
!unzip -qq translated-animals10.zip -d animals
!ls animals

!ls animals/animals10/raw-img/

from io import BytesIO
from IPython.display import Image as IMG
from google.colab import files
from keras.preprocessing import image
from shutil import copyfile
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import RMSprop
from urllib.request import urlopen
import seaborn as sns
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import tensorflow as tf
import zipfile, os
import warnings
warnings.filterwarnings("ignore")

import shutil
import os

hewan = os.path.join('/content/animals/animals10/raw-img/')

print(os.listdir(hewan))

hewan_bye = ['cat', 'cow', 'elephant', 'horse', 'sheep', 'squirrel']

for x in hewan_bye:
  path = os.path.join(hewan, x)
  shutil.rmtree(path)

hewanku = os.listdir(hewan)
print(hewanku)

for animal in hewanku:
    print(f'{animal} images: ', len(os.listdir(f'/content/animals/animals10/raw-img/{animal}')))

import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(2, 2, figsize=(15,15))
fig.suptitle("Menampilkan sample acak.", fontsize=24)
hewan_sort = sorted(hewanku)
hewan_id = 0
for i in range(2):
  for j in range(2):
    try:
      hewan_pilih = hewan_sort[hewan_id] 
      hewan_id += 1
    except:
      break
    if hewan_pilih == '.TEMP':
        continue
    hewan_pilih_gambar = os.listdir(os.path.join(hewan, hewan_pilih))
    hewan_pilih_acak= np.random.choice(hewan_pilih_gambar)
    img = plt.imread(os.path.join(hewan, hewan_pilih, hewan_pilih_acak))
    ax[i][j].imshow(img)
    ax[i][j].set_title(hewan_pilih, pad=10, fontsize=22)
    
plt.setp(ax, xticks=[],yticks=[])
plt.show

try:
  os.mkdir('/content/animals/animals10/training')
  os.mkdir('/content/animals/animals10/testing')
  for hewanku in hewanku:
    os.mkdir(f'/content/animals/animals10/training/{hewanku}')
    os.mkdir(f'/content/animals/animals10/testing/{hewanku}')
except OSError:
  pass

def split_data(images_path, training_path, testing_path, split_size):
    files = []
    for filename in os.listdir(images_path):
        file = images_path + filename
        if os.path.getsize(file) > 0:
            files.append(filename)
        else:
            print(filename + " others")

    training_length = int(len(files) * split_size)
    testing_length = int(len(files) - training_length)
    shuffled_set = random.sample(files, len(files))
    training_set = shuffled_set[0:training_length]
    testing_set = shuffled_set[training_length:]

    for filename in training_set:
        this_file = images_path + filename
        destination = training_path + filename
        copyfile(this_file, destination)

    for filename in testing_set:
        this_file = images_path + filename
        destination = testing_path + filename
        copyfile(this_file, destination)

split_size = 0.8 # 80% Data Training and 20% Data Validation

butterfly_images_path = "/content/animals/animals10/raw-img/butterfly/"
butterfly_train_path = "/content/animals/animals10/training/butterfly/"
butterfly_test_path = "/content/animals/animals10/testing/butterfly/"
split_data(butterfly_images_path, butterfly_train_path, butterfly_test_path, split_size)

chicken_images_path = "/content/animals/animals10/raw-img/chicken/"
chicken_train_path = "/content/animals/animals10/training/chicken/"
chicken_test_path = "/content/animals/animals10/testing/chicken/"
split_data(chicken_images_path, chicken_train_path, chicken_test_path, split_size)

dog_images_path = "/content/animals/animals10/raw-img/dog/"
dog_train_path = "/content/animals/animals10/training/dog/"
dog_test_path = "/content/animals/animals10/testing/dog/"
split_data(dog_images_path, dog_train_path, dog_test_path, split_size)

spider_images_path = "/content/animals/animals10/raw-img/spider/"
spider_train_path = "/content/animals/animals10/training/spider/"
spider_test_path = "/content/animals/animals10/testing/spider/"
split_data(spider_images_path, spider_train_path, spider_test_path, split_size)

total_train = len(os.listdir(butterfly_train_path)) + len(os.listdir(chicken_train_path)) + \
              len(os.listdir(dog_train_path)) + len(os.listdir(spider_train_path)) 
total_test  = len(os.listdir(butterfly_test_path)) + len(os.listdir(chicken_test_path)) + \
              len(os.listdir(dog_test_path)) + len(os.listdir(spider_test_path)) 

print("Total data training " + str(total_train) + " baris dan data validasi " + str(total_test))

batch_size = 64
TRAINING_DIR = '/content/animals/animals10/training'
train_datagen = ImageDataGenerator(
    rescale = 1./255,
    rotation_range = 30,
    width_shift_range = 0.1,
    height_shift_range = 0.2,
    shear_range = 0.2,
    zoom_range = 0.2,
    horizontal_flip = True,
    fill_mode = 'nearest'
) 

train_generator = train_datagen.flow_from_directory(
    TRAINING_DIR, 
    batch_size = batch_size,
    class_mode = 'categorical',
    target_size = (150,150)
)

VALIDATION_DIR = "/content/animals/animals10/testing"
validation_datagen = ImageDataGenerator(rescale = 1./255)
validation_generator = validation_datagen.flow_from_directory(
    VALIDATION_DIR,
    batch_size = batch_size,
    class_mode = 'categorical',
    target_size = (150, 150)
)

reduceku = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss', 
    factor=0.2,
    patience=5, 
    min_lr=1.5e-5
)

stopku = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    min_delta=0,
    patience=12,
    verbose=0,
    mode="auto",
    baseline=None,
    restore_best_weights=True
)

plt.style.use('seaborn-whitegrid')

def plot_acc(history):
  acc = history.history['accuracy']
  val_acc = history.history['val_accuracy']
  epochs = range(len(acc))
  plt.subplot(1, 2, 1)
  acc_plot, = plt.plot(epochs, acc, 'r')
  val_acc_plot, = plt.plot(epochs, val_acc, 'b')
  plt.title('Training and Validation Accuracy')
  plt.legend([acc_plot, val_acc_plot], ['Training Accuracy', 'Validation Accuracy'])


def plot_loss(history):
  loss = history.history['loss']
  val_loss = history.history['val_loss']
  epochs = range(len(loss))
  plt.subplot(1, 2, 2)
  loss_plot, = plt.plot(epochs, loss, 'r')
  val_loss_plot, = plt.plot(epochs, val_loss, 'b')
  plt.title('Training and Validation Loss')
  plt.legend([loss_plot, val_loss_plot], ['Training Loss', 'Validation Loss'])

def plot_history(history):
  plt.figure(figsize=(15,5))
  plot_acc(history)
  plot_loss(history)

tf.keras.backend.clear_session()

modelku = tf.keras.models.Sequential([
    InceptionV3(weights = "imagenet", include_top = False, input_shape = (150, 150, 3)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dropout(0.5), 
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(4, activation='softmax')
])

modelku.layers[0].trainable = False

modelku.summary()

modelku.compile(
    optimizer = 'adam', 
    loss = 'categorical_crossentropy', 
    metrics = ['accuracy']
)

historyku = modelku.fit(
    train_generator,
    epochs=5,
    callbacks = [reduceku, stopku],
    verbose=1,
    validation_data=validation_generator
)

plot_history(historyku)

modelku.save_weights('modelkuweights.h5')
modelku.save('modelku.h5')

konvert = tf.lite.TFLiteConverter.from_keras_model(modelku)
tflite_modelku = konvert.convert()

with tf.io.gfile.GFile('modelku.tflite', 'wb') as f:
  f.write(tflite_modelku)

validation_generator = validation_datagen.flow_from_directory(
    VALIDATION_DIR,
    batch_size=159,
    class_mode='categorical',
    target_size=(150, 150),
    shuffle = False
)
filenames = validation_generator.filenames
nb_ku = len(filenames)

Y_pred = modelku.predict_generator(validation_generator, steps = nb_ku)
y_pred = np.argmax(Y_pred, axis=1)

file_names = ['butterfly','chicken','dog','spider']
print(classification_report(validation_generator.classes, y_pred, target_names=file_names))

