import os
import tensorflow as tf
from keras import layers, models


def get_new_models():
    os.system("git pull origin main")
    training_instances = os.listdir("saved_model")
    candidates = []
    for i in training_instances:
        # if i==LETTER: continue
        instance_path = os.path.join("saved_model", i)
        model_names = os.listdir(instance_path)
        model_names.sort(reverse=True)
        print(model_names[:10])
        for j in model_names:
            model_path = os.path.join(instance_path, j)
            with open(os.path.join(model_path, "info.txt"), "r") as f:
                content = f.read().split()
                assert len(content) == 2
                fitness = float(content[1])
                candidates.append((fitness, model_path))


dummy = tf.keras.Sequential(
    [
        layers.Dense(600, input_shape=(448,), activation="relu", name="layer1"),
        layers.Dense(400, activation="relu", name="layer2"),
        layers.Dense(128, activation="relu", name="layer3"),
        layers.Dense(32, activation="sigmoid", name="layer4"),
        layers.Dense(8, activation="sigmoid", name="layer5"),
        layers.Dense(1, activation="sigmoid", name="layer6"),
    ]
)
input_layer = layers.Input(batch_shape=dummy.layers[0].input_shape)
prev_layer = input_layer
for layer in dummy.layers:
    layer._inbound_nodes = []
    prev_layer = layer(prev_layer)

funcmodel = models.Model([input_layer], [prev_layer])
# funcmodel.save_weights(os.path.join('test','checkpoint1.h5'))
# funcmodel.save_weights(os.path.join('test','checkpoint2.h5'))
# funcmodel.load_weights(os.path.join('test', 'checkpoint1.h5'))


def load_model(model_path):
    model = tf.keras.models.load_model(model_path)
    weights = model.get_weights()
    input_layer = layers.Input(batch_shape=dummy.layers[0].input_shape)
    prev_layer = input_layer
    for layer in dummy.layers:
        layer._inbound_nodes = []
        prev_layer = layer(prev_layer)
    funcmodel = models.Model([input_layer], [prev_layer])
    funcmodel.set_weights(weights)
    info_path = os.path.join(model_path, "info.txt")
    fitness = 0
    with open(info_path, "r") as f:
        content = f.read().split()
        assert len(content) == 2
        fitness = float(content[1])
    return [fitness, funcmodel]


LETTER = "A"


def save_model(model, name, fitness):
    model_path = os.path.join("weights", LETTER, name)
    os.mkdir(model_path)
    model.save_weights(os.path.join(model_path, "weights.h5"))
    # tf.keras.models.save_model(model, model_path)
    info_path = os.path.join(model_path, "info.txt")
    with open(info_path, "w") as f:
        f.write(f"<fitness> {fitness}")


training_instances = os.listdir("model")
candidates = []
for i in training_instances:
    if i != LETTER:
        continue
    instance_path = os.path.join("model", i)
    model_names = os.listdir(instance_path)
    for j in model_names:
        model_path = os.path.join(instance_path, j)
        fitness, model = load_model(model_path)
        save_model(model, j, fitness)
