import os
import tensorflow as tf
from keras import layers, models
import pygad.kerasga
from chess import Game 
from math import sqrt, tanh
import time

INSTANCE = str(int(time.time()))
MAX_WINNERS = 10
NUM_SOLUTION = 10
NUM_GENERATIONS = 1000
NUM_PARENTS_MATING = 4

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
dummy = models.Model([input_layer], [prev_layer])

def get_initial_models():
    training_instances = os.listdir('model')
    candidates = []
    for i in training_instances:
        instance_path = os.path.join('model', i)
        model_names = os.listdir(instance_path)
        for j in model_names:
            model_path = os.path.join(instance_path, j)
            with open(os.path.join(model_path, 'info.txt'), 'r') as f:
                content = f.read().split()
                assert len(content) == 2
                fitness = float(content[1])
                candidates.append((fitness, model_path))
    candidates.sort(reverse=True)
    print(candidates[:MAX_WINNERS])
    return [load_model(k[1]) for k in candidates[:MAX_WINNERS]]


def add_to_winners(fitness, weights):
    global dummy, winners
    if winners[0][0] >= fitness: return
    for w in winners:
        if abs(w[0] - fitness) < 0.01:
            print("Duplicate winner found!!!")
            return

    if len(winners) < MAX_WINNERS:
        model = models.clone_model(dummy)
        model.set_weights(weights)
        winners.append([fitness, model])
    else:
        winners[0][0] = fitness
        winners[0][1].set_weights(weights)
    winners.sort(key=lambda x: x[0])

def load_model(model_path):
    global dummy
    model = models.clone_model(dummy)
    model.load_weights(os.path.join(model_path, 'weights.h5'))
    info_path = os.path.join(model_path, "info.txt")
    fitness = 0
    with open(info_path, 'r') as f:
        content = f.read().split()
        assert len(content) == 2
        fitness = float(content[1])
    return [fitness, model]

def save_model(model, name, fitness, temp=False):
    model_path = os.path.join('model', INSTANCE, name)
    if temp:
        model_path = os.path.join('temp_model', INSTANCE, name)
    if not os.path.exists(model_path):
        os.mkdir(model_path)
    model.save_weights(os.path.join(model_path, 'weights.h5'))
    # tf.keras.models.save_model(model, model_path)
    info_path = os.path.join(model_path, "info.txt")
    with open(info_path, 'w') as f:
        f.write(f"<fitness> {fitness}")

winners = get_initial_models()
winners.sort(key=lambda x: x[0])
dummy.set_weights(winners[len(winners)-1][1].get_weights())
last_winner = winners[0]
last_fitness = last_winner[0]
last_weights = last_winner[1].get_weights()
previous_fitness = last_fitness
minimax_depth = 1
increase_minimax_depth = False

def calculate_rank_score(base, result):
    opponent_score = base
    turn_score = -sqrt(result.turn)/8 + 1
    if result.winner is False:
        turn_score = -turn_score
    elif result.winner is None:
        turn_score = 0
    
    match_score = 3 if result.winner else -1
    piece_score = tanh(result.piece_score/25)
    if result.winner is None: 
        match_score = 0
    return opponent_score + turn_score + match_score + piece_score


def fitness_func(solution, sol_idx):
    global keras_ga, dummy, last_fitness, last_weights, winners, increase_minimax_depth, minimax_depth
    model_weights_matrix = pygad.kerasga.model_weights_as_matrix(model=dummy, weights_vector=solution)
    dummy.set_weights(weights=model_weights_matrix)
    rank_score = 0
    for i in range(len(winners)):
        base, opponent = winners[i]
        result = Game().run_game_ava(dummy, opponent)
        rank_score += calculate_rank_score(base, result)
        # print(result)
    rank_score /= len(winners)
    try:
        result = Game().run_game_avc(dummy, minimax_depth)
        if result.winner:
            print(f"Win against depth {minimax_depth} minimax")
            save_model(dummy, f"WIN_MINIMAX_{minimax_depth}", rank_score + 1, True)
            increase_minimax_depth = True
            rank_score += minimax_depth
    except Exception as e:
        with open(os.path.join('logs', f'{int(time.time())}.txt')) as f:
            f.write(e)
    print("Rank: {:.3f}".format(rank_score))
    if rank_score > last_fitness:
        last_fitness = rank_score
        last_weights = model_weights_matrix
    return rank_score


def callback_generation(ga_instance):
    global keras_ga, dummy, last_fitness, last_weights, winners, previous_fitness, increase_minimax_depth, minimax_depth
    generation = ga_instance.generations_completed
    print("Generation = {generation}".format(generation=generation))
    print("Fitness    = {fitness}".format(fitness=last_fitness))
    print([x[0] for x in winners])
    if winners[0][0] < last_fitness and abs(previous_fitness - last_fitness) > 0.01:
        add_to_winners(last_fitness, last_weights)
        previous_fitness = last_fitness
        dummy.set_weights(last_weights)
        save_model(dummy, f'{str(generation).zfill(4)}', last_fitness, True)
    last_fitness = 0
    if increase_minimax_depth:
        if minimax_depth < 3:
            minimax_depth += 1
    if generation%20==0:
        try:
            for i, v in enumerate(winners):
                fitness, model = v
                save_model(model, f"{str(i).zfill(2)}", fitness)
            os.system('git add .')
            os.system(f'git commit -m "{INSTANCE} - generation {generation}"')
            os.system('git push origin main')
            candidates = get_new_models()
            for c in candidates:
                fitness, model = c
                add_to_winners(fitness, model.get_weights())
        except Exception as e:
            import time
            with open(os.path.join('logs', f'{int(time.time())}.txt')) as f:
                f.write(e)
    


def get_new_models():
    os.system("git pull origin main")
    training_instances = os.listdir('model')
    candidates = []
    for i in training_instances:
        if i==INSTANCE: continue
        instance_path = os.path.join('model', i)
        model_names = os.listdir(instance_path)
        model_names.sort(reverse=True)
        for j in model_names:
            model_path = os.path.join(instance_path, j)
            with open(os.path.join(model_path, 'info.txt'), 'r') as f:
                content = f.read().split()
                assert len(content) == 2
                fitness = float(content[1])
                candidates.append((fitness, model_path))
    candidates.sort(reverse=True)
    return [load_model(k[1]) for k in candidates[:4]]
        
keras_ga = pygad.kerasga.KerasGA(model=dummy, num_solutions=NUM_SOLUTION)
initial_population = keras_ga.population_weights
ga_instance = pygad.GA(num_generations=NUM_GENERATIONS, 
                       num_parents_mating=NUM_PARENTS_MATING, 
                       initial_population=initial_population,
                       fitness_func=fitness_func,
                       on_generation=callback_generation,
)
ga_instance.run()
