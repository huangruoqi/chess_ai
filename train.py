import os
import tensorflow as tf
from tensorflow.keras import layers

MODEL_NAME = 'test'

tf.keras.models.save_model(
    tf.keras.Sequential([
        layers.Dense(600, input_shape=(448,), activation="relu", name="layer1"),
        layers.Dense(400, activation="relu", name="layer2"),
        layers.Dense(128, activation="relu", name="layer3"),
        layers.Dense(32, activation="sigmoid", name="layer4"),
        layers.Dense(8, activation="sigmoid", name="layer5"),
        layers.Dense(1, activation="sigmoid", name="layer6"),
    ]), os.path.join('model', MODEL_NAME)
)