import tensorflow as tf
from keras import layers, models
import numpy as np
import os

from utils import save_model

INSTANCE = 'init'

def shuffle_weights(model, weights=None):
    """Randomly permute the weights in `model`, or the given `weights`.
    This is a fast approximation of re-initializing the weights of a model.
    Assumes weights are distributed independently of the dimensions of the weight tensors
      (i.e., the weights have the same distribution along each dimension).
    :param Model model: Modify the weights of the given model.
    :param list(ndarray) weights: The model's weights will be replaced by a random permutation of these weights.
      If `None`, permute the model's current weights.
    """
    if weights is None:
        weights = model.get_weights()
    weights = [np.random.permutation(w.flat).reshape(w.shape) for w in weights]
    # Faster, but less random: only permutes along the first dimension
    # weights = [np.random.permutation(w) for w in weights]
    model.set_weights(weights)

dummy = tf.keras.Sequential(
    [
        layers.Dense(600, input_shape=(448,), activation="tanh", name="layer1"),
        layers.Dense(400, activation="tanh", name="layer2"),
        layers.Dense(128, activation="tanh", name="layer3"),
        layers.Dense(1, activation="tanh", name="layer4"),
    ]
)
input_layer = layers.Input(batch_shape=dummy.layers[0].input_shape)
prev_layer = input_layer
for layer in dummy.layers:
    layer._inbound_nodes = []
    prev_layer = layer(prev_layer)
dummy = models.Model([input_layer], [prev_layer])

for i in range(10):
    shuffle_weights(dummy)
    print(dummy.get_weights()[0][0][:20])
    save_model(dummy, INSTANCE, f'{str(i).zfill(2)}', 0)
