import tensorflow as tf
from keras import layers, models
import os

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
