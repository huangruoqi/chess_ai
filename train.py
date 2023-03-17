import os
import tensorflow as tf
from tensorflow.keras import layers
import pygad.kerasga
from chess import Game 
from math import sqrt, tanh


INITIAL_MODELS = [
    'G_02_0001',
    'G_05_0001',
    'G_05_0002',
    'G_09_0001',
    'G_09_0002',
    'G_09_0003',
    'G_09_0004',
]
MAX_WINNERS = 10
NUM_SOLUTION = 10
NUM_GENERATIONS = 1000
NUM_PARENTS_MATING = 4

round_numer = 0
with open('round.txt', 'r') as f:
    round_numer = int(f.read())
with open('round.txt', 'w') as f:
    f.write(str(round_numer + 1))

dummy = tf.keras.Sequential([
    layers.Dense(600, input_shape=(448,), activation="relu", name="layer1"),
    layers.Dense(400, activation="relu", name="layer2"),
    layers.Dense(128, activation="relu", name="layer3"),
    layers.Dense(32, activation="sigmoid", name="layer4"),
    layers.Dense(8, activation="sigmoid", name="layer5"),
    layers.Dense(1, activation="sigmoid", name="layer6"),
])

def add_to_winners(winners_, fitness, weights):
    if len(winners_) < MAX_WINNERS:
        model = tf.keras.Sequential([
            layers.Dense(600, input_shape=(448,), activation="relu", name="layer1"),
            layers.Dense(400, activation="relu", name="layer2"),
            layers.Dense(128, activation="relu", name="layer3"),
            layers.Dense(32, activation="sigmoid", name="layer4"),
            layers.Dense(8, activation="sigmoid", name="layer5"),
            layers.Dense(1, activation="sigmoid", name="layer6"),
        ])
        model.set_weights(weights)
        winners_.append([fitness, model])
    else:
        winners_[0][0] = fitness
        winners_[0][1].set_weights(weights)
    winners_.sort(key=lambda x: x[0])

def load_model(name):
    model_path = os.path.join('model', name)
    model = tf.keras.models.load_model(os.path.join('model', name))
    info_path = os.path.join(model_path, "info.txt")
    fitness = 0
    with open(info_path, 'r') as f:
        content = f.read().split()
        assert len(content) == 2
        fitness = float(content[1])
    return [fitness, model]

def save_model(model, name, fitness):
    model_path = os.path.join('model', name)
    tf.keras.models.save_model(model, os.path.join('model', name))
    info_path = os.path.join(model_path, "info.txt")
    with open(info_path, 'w') as f:
        f.write(f"<fitness> {fitness}")

winners = [load_model(i) for i in INITIAL_MODELS]
dummy.set_weights(winners[0][1].get_weights())
winners.sort(key=lambda x: x[0])
last_winner = winners[0]
last_fitness = last_winner[0]
last_weights = last_winner[1].get_weights()
previous_fitness = last_fitness


def calculate_rank_score(base, result):
    opponent_score = base
    turn_score = -sqrt(result.turn)/16 + 1
    if result.winner is False:
        turn_score = -turn_score
    elif result.winner is None:
        turn_score = 0
    
    match_score = 2 if result.winner else -1
    piece_score = tanh(result.piece_score/25)
    if result.winner is None: 
        match_score = 0
    return opponent_score + turn_score + match_score + piece_score


def fitness_func(solution, sol_idx):
    global keras_ga, dummy, last_fitness, last_weights, winners
    model_weights_matrix = pygad.kerasga.model_weights_as_matrix(model=dummy, weights_vector=solution)
    dummy.set_weights(weights=model_weights_matrix)
    rank_score = 0
    for i in range(len(winners)):
        base, opponent = winners[i]
        result = Game().run_game_ava(dummy, opponent)
        rank_score += calculate_rank_score(base, result)
        print(result)
    rank_score /= len(winners)
    print("{:.3f}".format(rank_score))
    if rank_score > last_fitness:
        last_fitness = rank_score
        last_weights = model_weights_matrix
    return rank_score

def callback_generation(ga_instance):
    global keras_ga, dummy, last_fitness, last_weights, winners, previous_fitness
    print("Generation = {generation}".format(generation=ga_instance.generations_completed))
    print("Fitness    = {fitness}".format(fitness=ga_instance.best_solution()[1]))
    if winners[0][0] < last_fitness and abs(previous_fitness - last_fitness) > 0.01:
        add_to_winners(winners, last_fitness, last_weights)
        previous_fitness = last_fitness
        dummy.set_weights(last_weights)
        save_model(dummy, f'G_{str(round_numer).zfill(2)}_{str(ga_instance.generations_completed).zfill(4)}', last_fitness)
        last_fitness = 0

keras_ga = pygad.kerasga.KerasGA(model=dummy, num_solutions=NUM_SOLUTION)
initial_population = keras_ga.population_weights
ga_instance = pygad.GA(num_generations=NUM_GENERATIONS, 
                       num_parents_mating=NUM_PARENTS_MATING, 
                       initial_population=initial_population,
                       fitness_func=fitness_func,
                       on_generation=callback_generation,
)
ga_instance.run()
