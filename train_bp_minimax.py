from save import load_arrays
import os
import tensorflow as tf
from keras import layers, models
from pygad.kerasga import model_weights_as_matrix, model_weights_as_vector
from chess import Game
from math import sqrt, tanh
import time
import gc
import keras.backend as K
import numpy
from utils import Chess_Model

chess_model = Chess_Model()
