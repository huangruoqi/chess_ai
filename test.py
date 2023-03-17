import os
import tensorflow as tf
from keras import layers, models

def get_new_models():
    os.system("git pull origin main")
    training_instances = os.listdir('saved_model')
    candidates = []
    for i in training_instances:
        # if i==LETTER: continue
        instance_path = os.path.join('saved_model', i)
        model_names = os.listdir(instance_path)
        model_names.sort(reverse=True)
        print(model_names[:10])
        for j in model_names:
            model_path = os.path.join(instance_path, j) 
            with open(os.path.join(model_path, 'info.txt'), 'r') as f:
                content = f.read().split()
                assert len(content) == 2
                fitness = float(content[1])
                candidates.append((fitness, model_path))

dummy = tf.keras.Sequential([
    layers.Dense(600, input_shape=(448,), activation="relu", name="layer1"),
    layers.Dense(400, activation="relu", name="layer2"),
    layers.Dense(128, activation="relu", name="layer3"),
    layers.Dense(32, activation="sigmoid", name="layer4"),
    layers.Dense(8, activation="sigmoid", name="layer5"),
    layers.Dense(1, activation="sigmoid", name="layer6"),
])
input_layer = layers.Input(batch_shape=dummy.layers[0].input_shape)
prev_layer = input_layer
for layer in dummy.layers:
    layer._inbound_nodes = []
    prev_layer = layer(prev_layer)

funcmodel = models.Model([input_layer], [prev_layer])
funcmodel.save_weights(os.path.join('test','checkpoint1.h5'))
funcmodel.save_weights(os.path.join('test','checkpoint2.h5'))
# funcmodel.load_weights(os.path.join('test', 'checkpoint1.h5'))