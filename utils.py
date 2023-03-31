import tensorflow as tf
from keras import layers, models
import os
from math import tanh

class Chess_Model:
    def __init__(self):
        d = tf.keras.Sequential(
            [
                layers.Dense(600, input_shape=(448,), activation="tanh", name="layer1"),
                layers.Dense(400, activation="tanh", name="layer2"),
                layers.Dense(128, activation="tanh", name="layer3"),
                layers.Dense(1, activation="tanh", name="layer4"),
            ]
        )
        input_layer = layers.Input(batch_shape=d.layers[0].input_shape)
        prev_layer = input_layer
        for layer in d.layers:
            layer._inbound_nodes = []
            prev_layer = layer(prev_layer)
        self.dummy = models.Model([input_layer], [prev_layer])

    def get_clone(self):
        return models.clone_model(self.dummy)

    def load_model(self, model_path):
        model = models.clone_model(self.dummy)
        model.load_weights(os.path.join(model_path, "weights.h5"))
        info_path = os.path.join(model_path, "info.txt")
        fitness = 0
        with open(info_path, "r") as f:
            content = f.read().split()
            assert len(content) == 2
            fitness = float(content[1])
        return [fitness, model]


    def save_model(self, model, instance, name, fitness, temp=False):
        instance_path = os.path.join("model", instance)
        if temp:
            instance_path = os.path.join("temp_model", instance)
        model_path = os.path.join(instance_path, name)
        if not os.path.exists(instance_path):
            os.mkdir(instance_path)
        if not os.path.exists(model_path):
            os.mkdir(model_path)
        model.save_weights(os.path.join(model_path, "weights.h5"))
        info_path = os.path.join(model_path, "info.txt")
        with open(info_path, "w") as f:
            f.write(f"<fitness> {fitness}")


def load_inputs(file):
    inputs = []
    with open(file, "rb") as f:
        content = bytearray(f.read())
        row = [0] * (64 * 7)
        count = 0
        for byte in content:
            for j in range(8):
                x = byte & 1
                byte >>= 1
                if x == 1:
                    row[8 * count + j] = 1
            count += 1
            if count == 64 * 7 // 8:
                inputs.append(row)
                row = [0] * (64 * 7)
                count = 0
    return inputs

def save_inputs(file, inputs):
    with open(file, "wb") as f:
        for i in inputs:
            byte = 0
            count = 0
            arr = []
            for j in range(64 * 7):
                byte <<= 1
                if (i & 1) != 0:
                    byte += 1
                count += 1
                i >>= 1
                if count == 8:
                    arr.append(byte.to_bytes(1, "little", signed=False))
                    byte = 0
                    count = 0
            for j in reversed(arr):
                f.write(j)

def clamp_score(scores):
    return list(map(lambda s: tanh(s / 25), scores))