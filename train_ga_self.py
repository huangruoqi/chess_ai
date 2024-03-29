import os
import tensorflow as tf
from keras import layers, models
from pygad.kerasga import model_weights_as_matrix, model_weights_as_vector
import pygad
from chess import Game
from math import sqrt, tanh
import time
import gc
import keras.backend as K
import numpy
from utils import Chess_Model

d = tf.config.experimental.list_physical_devices("GPU")
if d:
    tf.config.experimental.set_memory_growth(d[0], True)
# tf.debugging.set_log_device_placement(True)


INSTANCE = str(int(time.time()))
MAX_WINNERS = 10
NUM_SOLUTION = 10
NUM_PARENTS_MATING = 5
DEBUG = True


def get_initial_models():
    training_instances = os.listdir("model")
    candidates = []
    for i in training_instances:
        instance_path = os.path.join("model", i)
        model_names = os.listdir(instance_path)
        for j in model_names:
            model_path = os.path.join(instance_path, j)
            with open(os.path.join(model_path, "info.txt"), "r") as f:
                content = f.read().split()
                assert len(content) == 2
                fitness = float(content[1])
                candidates.append((fitness, model_path))
    candidates.sort(reverse=True)
    [print(i) for i in candidates[:MAX_WINNERS]]
    return [chess_model.load_model(k[1]) for k in candidates[:MAX_WINNERS]]


def get_initial_population(models):
    population = []
    for fitness, model in models:
        population.append(model_weights_as_vector(model))
    return population


def add_to_winners(fitness, weights):
    global chess_model, winners
    if winners[0][0] >= fitness:
        return
    for w in winners:
        if abs(w[0] - fitness) < 0.001:
            print("Duplicate winner found!!!")
            return

    if len(winners) < MAX_WINNERS:
        model = chess_model.get_clone()
        model.set_weights(weights)
        winners.append([fitness, model])
    else:
        winners[0][0] = fitness
        winners[0][1].set_weights(weights)
    winners.sort(key=lambda x: x[0])


def calculate_rank_score(base, result):
    opponent_score = base
    turn_score = -sqrt(result.turn) / 8 + 1
    if result.winner is False:
        turn_score = -turn_score
    elif result.winner is None:
        turn_score = 0

    match_score = 3 if result.winner else -1
    piece_score = tanh(result.piece_score / 25)
    if result.winner is None:
        match_score = 0
    return opponent_score + turn_score + match_score + piece_score


def fitness_func(solution, sol_idx):
    global dummy, last_fitness, last_weights, winners, increase_minimax_depth, minimax_depth, game
    model_weights_matrix = model_weights_as_matrix(model=dummy, weights_vector=solution)
    dummy.set_weights(weights=model_weights_matrix)
    rank_score = 0
    wins = 0
    for i in range(len(winners)):
        base, opponent = winners[i]
        game.reset()
        result = game.run_game_ava(dummy, opponent)
        if result.winner:
            wins += 1
        rank_score += calculate_rank_score(base, result)
        if DEBUG:
            print(result)
    rank_score /= len(winners)
    try:
        game.reset()
        result = game.run_game_avc(dummy, minimax_depth)
        if result.winner:
            print(f"Win against depth {minimax_depth} minimax")
            chess_model.save_model(
                dummy, INSTANCE, f"WIN_MINIMAX_{minimax_depth}", rank_score + 1, True
            )
            increase_minimax_depth = True
            rank_score += minimax_depth
    except Exception as e:
        with open(os.path.join("logs", f"{int(time.time())}.txt"), "w") as f:
            f.write(e)
    print("Rank: {:.3f} Wins: {}".format(rank_score, wins))
    if rank_score > last_fitness:
        last_fitness = rank_score
        last_weights = model_weights_matrix
    K.clear_session()
    gc.collect()
    return rank_score


def callback_generation(ga_instance):
    global dummy, last_fitness, last_weights, winners, previous_fitness, increase_minimax_depth, minimax_depth, start
    generation = ga_instance.generations_completed
    print("Generation = {generation}".format(generation=generation))
    print("Fitness    = {fitness}".format(fitness=last_fitness))
    if winners[0][0] < last_fitness and abs(previous_fitness - last_fitness) > 0.001:
        add_to_winners(last_fitness, last_weights)
        previous_fitness = last_fitness
        dummy.set_weights(last_weights)
        chess_model.save_model(
            dummy, INSTANCE, f"{str(generation).zfill(4)}", last_fitness, True
        )
    last_fitness = 0
    # if increase_minimax_depth:
    #     if minimax_depth < 3:
    #         minimax_depth += 1
    if generation % 20 == 0:
        try:
            for i, v in enumerate(winners[6:]):
                fitness, model = v
                chess_model.save_model(model, INSTANCE, f"{str(i).zfill(2)}", fitness)
            os.system("git add .")
            os.system(f'git commit -m "{INSTANCE} - generation {generation}"')
            os.system("git pull origin main")
            os.system("git push origin main")
            candidates = get_new_models()
            for c in candidates:
                fitness, model = c
                add_to_winners(fitness, model.get_weights())
        except Exception as e:
            with open(os.path.join("logs", f"{int(time.time())}.txt"), "w") as f:
                f.write(e)
    print([x[0] for x in winners])
    current = time.time()
    print(f"Time elasped: {current - start} seconds")
    start = current


def get_new_models():
    training_instances = os.listdir("model")
    candidates = []
    for i in training_instances:
        if i == INSTANCE:
            continue
        instance_path = os.path.join("model", i)
        model_names = os.listdir(instance_path)
        model_names.sort(reverse=True)
        for j in model_names:
            model_path = os.path.join(instance_path, j)
            with open(os.path.join(model_path, "info.txt"), "r") as f:
                content = f.read().split()
                assert len(content) == 2
                fitness = float(content[1])
                candidates.append((fitness, model_path))
    candidates.sort(reverse=True)
    return [chess_model.load_model(k[1]) for k in candidates[:4]]

chess_model = Chess_Model()
dummy = chess_model.get_clone()
game = Game()
def run():
    global chess_model, game, winners, dummy, last_winner, last_fitness, last_weights, previous_fitness, minimax_depth, increase_minimax_depth, start
    winners = get_initial_models()
    winners.sort(key=lambda x: x[0])
    dummy.set_weights(winners[len(winners) - 1][1].get_weights())
    last_winner = winners[0]
    last_fitness = last_winner[0]
    last_weights = last_winner[1].get_weights()
    previous_fitness = last_fitness
    minimax_depth = 1
    increase_minimax_depth = False

    ga_instance = pygad.GA(
        num_generations=20,
        num_parents_mating=NUM_PARENTS_MATING,
        initial_population=get_initial_population(winners),
        fitness_func=fitness_func,
        on_generation=callback_generation,
        parallel_processing=None,
    )
    print(f"Instance: <{INSTANCE}> started!!!")
    start = time.time()
    try:
        ga_instance.run()
        for i, v in enumerate(winners[6:]):
            fitness, model = v
            chess_model.save_model(model, INSTANCE, f"{str(i).zfill(2)}", fitness)
        os.system("git add .")
        os.system(f'git commit -m "Instance: {INSTANCE}"')
        os.system("git pull origin main")
        os.system("git push origin main")
    except Exception as e:
        with open(os.path.join("logs", f"{int(time.time())}.txt"), "w") as f:
            f.write(e)

if __name__ == '__main__':
    while 1:
        run()