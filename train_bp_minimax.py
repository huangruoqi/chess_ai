from save import load_arrays
import os
import tensorflow as tf
from keras import layers, models
import keras
from pygad.kerasga import model_weights_as_matrix, model_weights_as_vector
from chess import Game
from math import sqrt, tanh
import time
import gc
import keras.backend as K
import numpy
from utils import Chess_Model, clamp_score

EPOCHS = 20
BATCH_SIZE = 128



DATA = load_arrays(converted=False)
chess_model = Chess_Model()
dummy = chess_model.get_clone()
# dummy = keras.Model()
dummy.compile(optimizer='adam', loss='mse', metrics=['mse'])
x_train = numpy.array(list(DATA.keys()))
y_train = numpy.array(clamp_score(list(DATA.values())))
history = dummy.fit(x=x_train, y=y_train, validation_split=0.5,shuffle=True, epochs=EPOCHS, batch_size=BATCH_SIZE)
evaluation = dummy.evaluate(x_train, y_train, verbose=0)
model_name = f"{str(int(time.time()//1))[2:]}"
chess_model.save_model(dummy, "BackPropagation", model_name, evaluation[1])
