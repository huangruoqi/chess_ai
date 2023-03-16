import os
import tensorflow as tf
from tensorflow.keras import layers
import pygad.kerasga
from chess import Game 
from math import sqrt, tanh


MODEL_NAME = 'test'
model = tf.keras.Sequential([
    layers.Dense(600, input_shape=(448,), activation="relu", name="layer1"),
    layers.Dense(400, activation="relu", name="layer2"),
    layers.Dense(128, activation="relu", name="layer3"),
    layers.Dense(32, activation="sigmoid", name="layer4"),
    layers.Dense(8, activation="sigmoid", name="layer5"),
    layers.Dense(1, activation="sigmoid", name="layer6"),
])

winner = tf.keras.Sequential([
    layers.Dense(600, input_shape=(448,), activation="relu", name="layer1"),
    layers.Dense(400, activation="relu", name="layer2"),
    layers.Dense(128, activation="relu", name="layer3"),
    layers.Dense(32, activation="sigmoid", name="layer4"),
    layers.Dense(8, activation="sigmoid", name="layer5"),
    layers.Dense(1, activation="sigmoid", name="layer6"),
])
winner_fitness = 0
best_fitness = 0
best_weights = model.get_weights()

def save_model(model, name, fitness):
    model_path = os.path.join('model', name)
    tf.keras.models.save_model(model, os.path.join('model', name))
    info_path = os.path.join(model_path, "info.txt")
    with open(info_path, 'w') as f:
        f.write(f"<fitness> {fitness}")

def fitness_func(solution, sol_idx):
    global keras_ga, model, best_fitness, best_weights, winner, winner_fitness
    # depth = 2
    model_weights_matrix = pygad.kerasga.model_weights_as_matrix(model=model, weights_vector=solution)
    model.set_weights(weights=model_weights_matrix)
    # result = Game().run_game_avc(model, depth)
    result = Game().run_game_ava(model, winner)
    opponent_score = winner_fitness
    turn_score = -sqrt(result.turn)/16 + 1
    if result.winner is False:
        turn_score = -turn_score
    elif result.winner is None:
        turn_score = 0
    
    match_score = 2 if result.winner else -1
    piece_score = tanh(result.piece_score/25)
    if result.winner is None: 
        match_score = 0
    fitness = opponent_score + turn_score + match_score + piece_score
    print(result, fitness)
    if fitness > best_fitness:
        best_fitness = fitness
        best_weights = model_weights_matrix
    return fitness

def callback_generation(ga_instance):
    global keras_ga, model, best_fitness, best_weights, winner, winner_fitness
    print("Generation = {generation}".format(generation=ga_instance.generations_completed))
    print("Fitness    = {fitness}".format(fitness=ga_instance.best_solution()[1]))
    if winner_fitness < best_fitness:
        winner_fitness = best_fitness
        winner.set_weights(best_weights)
        save_model(winner, f'G_{str(ga_instance.generations_completed).zfill(4)}', winner_fitness)

keras_ga = pygad.kerasga.KerasGA(model=model, num_solutions=20)
initial_population = keras_ga.population_weights
ga_instance = pygad.GA(num_generations=1000, 
                       num_parents_mating=5, 
                       initial_population=initial_population,
                       fitness_func=fitness_func,
                       on_generation=callback_generation,
)
ga_instance.run()
