import os
import tensorflow as tf
from pygad.kerasga import model_weights_as_matrix, model_weights_as_vector
import pygad
from chess import Game
from math import sqrt, tanh
import time
import gc
import keras.backend as K
from utils import Chess_Model

d = tf.config.experimental.list_physical_devices("GPU")
if d:
    tf.config.experimental.set_memory_growth(d[0], True)
# tf.debugging.set_log_device_placement(True)


INSTANCE = str(int(time.time()))
NUM_SOLUTION = 8
NUM_PARENTS_MATING = 4
NUM_MATCH = 10
NUM_WINNERS = 20
DEPTH = 1
DEBUG = True


def get_initial_models():
    candidates = []
    model_names = os.listdir("model")
    for j in model_names:
        model_path = os.path.join("model", j)
        with open(os.path.join(model_path, "info.txt"), "r") as f:
            content = f.read().split()
            assert len(content) >= 2
            fitness = float(content[1])
            candidates.append((fitness, model_path))
    candidates.sort(reverse=True)
    return sorted([chess_model.load_model(k[1]) for k in candidates][:NUM_WINNERS], key=lambda x: x[0])

    


def get_initial_population(models):
    population = []
    for fitness, model in models[:NUM_SOLUTION]:
        population.append(model_weights_as_vector(model))
    return population


def calculate_rank_score(result):
    turn_score = -sqrt(result.turn) / 8 + 1
    if result.winner is False:
        turn_score = -turn_score
    elif result.winner is None:
        turn_score = 0

    match_score = NUM_MATCH*2 if result.winner else -NUM_MATCH
    if result.winner is None:
        match_score = -NUM_MATCH//2

    piece_score = tanh(result.piece_score / 25)
    return turn_score + match_score + piece_score


def fitness_func(solution, sol_idx):
    global dummy, last_fitness, last_weights, last_record, game
    model_weights_matrix = model_weights_as_matrix(model=dummy, weights_vector=solution)
    dummy.set_weights(weights=model_weights_matrix)
    rank_score = 0
    wins = 0
    record = ""
    for i in range(NUM_MATCH):
        game.reset()
        result = game.run_game_avc(model=dummy, depth=DEPTH)
        if result.winner:
            wins += 1
        rank_score += calculate_rank_score(result)
        record += str(result) + '\n'
        if DEBUG:
            print(result)
    rank_score /= NUM_MATCH
    print("Rank: {:.3f} Wins: {}".format(rank_score, wins))
    if rank_score > last_fitness:
        last_fitness = rank_score
        last_weights = model_weights_matrix
        last_record = record
    K.clear_session()
    gc.collect()
    return rank_score


def callback_generation(ga_instance):
    global dummy, last_fitness, last_weights, start, previous_fitness, last_record
    generation = ga_instance.generations_completed
    print("Generation = {generation}".format(generation=generation))
    print("Fitness    = {fitness}".format(fitness=last_fitness))
    add_to_winners(last_fitness, last_weights)
    previous_fitness = last_fitness
    dummy.set_weights(last_weights)
    chess_model.save_model(
        dummy, INSTANCE, f"{str(generation).zfill(4)}", last_fitness, True, last_record
    )
    last_fitness = -10000
    current = time.time()
    print(f"Time elasped: {current - start} seconds")
    start = current


chess_model = Chess_Model()
dummy = chess_model.get_clone()
game = Game()

def add_to_winners(fitness, weights):
    global chess_model, winners
    for w in winners:
        if abs(w[0] - fitness) < 0.001:
            print("Duplicate winner found!!!")
            return

    if len(winners) < NUM_WINNERS:
        model = chess_model.get_clone()
        model.set_weights(weights)
        winners.append([fitness, model])
    else:
        if winners[0][0] >= fitness:
            return
        winners[0][0] = fitness
        winners[0][1].set_weights(weights)
    winners.sort(key=lambda x: x[0])

def run():
    global chess_model, game, winners, last_fitness, last_weights, start, last_record
    winners = get_initial_models()
    last_fitness = -10000

    ga_instance = pygad.GA(
        num_generations=1,
        num_parents_mating=NUM_PARENTS_MATING,
        initial_population=get_initial_population(winners),
        fitness_func=fitness_func,
        on_generation=callback_generation,
        parallel_processing=None,
    )
    # print(f"Instance: <{INSTANCE}> started!!!")
    start = time.time()
    ga_instance.run()

    os.system("git pull origin main")
    new_winners = get_initial_models()
    for fitness, model in new_winners:
        add_to_winners(fitness, model.get_weights())
    fitness = 0
    for i, v in enumerate(winners):
        fitness, model = v
        chess_model.save_model(model, INSTANCE, f"{str(i).zfill(2)}", fitness, False, last_record)
    os.system("git add .")
    os.system(f'git commit -m "Best: {fitness}"')
    os.system("git push origin main")

if __name__ == '__main__':
    while 1:
        run()