from sys import getsizeof
from chess import Result, Game
import random
import numpy
import os
import time
from utils import load_inputs, save_inputs

DEPTH = 2
ROUND = 100


def main():
    history = load_arrays()
    while 1:
        board2scores = {}
        for i in range(ROUND):
            save_game(board2scores)
        results = {}
        for k, v in board2scores.items():
            avg_score = sum(v) / len(v)
            history[k] = (history.get(k, avg_score) + avg_score) / 2
            results[k] = history[k]
        print(f"Saved: {len(results)}")
        print(f"Total: {len(history)}")
        save_results(results)

def load_arrays():
    instances = os.listdir("nparrays")
    result = {}
    for i in instances:
        instance_path = os.path.join("nparrays", i)
        inputs = load_inputs(os.path.join(instance_path, "inputs.bin"))
        target = numpy.load(os.path.join(instance_path, "target.npy"))
        assert len(inputs) == len(target)
        for i in range(len(inputs)):
            result[convert(inputs)] = target[i]
    return result


def convert(board):
    key = 0
    for i in board:
        key <<= 1
        if i != 0:
            key += 1
    return key


def save_game(board2score):
    g = Game()
    r = None
    color = True
    turn = 0
    total0, total1 = {}, {}
    while 1:
        turn += 1
        score, move, results = minimax_mod(
            g, 0, color, -10000, 10000, color, True, DEPTH
        )
        if color:
            for a, b in results:
                total1[a] = total1.get(a, [])
                total1[a].append(b)
        else:
            for a, b in results:
                total0[a] = total0.get(a, [])
                total0[a].append(b)
        piece, square = move
        g.move(piece, *square)
        if g.is_checkmate(not color):
            r = Result(color, turn, g.get_piece_score(True))
            break
        color = not color
        if turn > 200:
            r = Result(None, turn, g.get_piece_score(True))
            break
    if r.winner is None:
        return
    total = total0
    if r.winner:
        total = total1
    for k, v in total.items():
        real_key = convert(k)
        if board2score.get(real_key) is None:
            board2score[real_key] = v
        else:
            board2score[real_key].extend(v)


def minimax_mod(self: Game, depth, color, alpha, beta, flipped, checked, max_depth):
    results = []
    random_choice = True
    opponent_pieces_alive = self.bpieces_alive if color else self.wpieces_alive
    if depth >= max_depth:
        return self.get_score(flipped), None
    best = []
    moves = self.get_real_moves(color) if checked else self.get_all_moves(color)
    is_minimizing = not color if flipped else color
    moves.sort(reverse=not is_minimizing)
    minimax_value = 1000 if is_minimizing else -1000
    for move in moves:
        piece = move[1][0]
        square = move[1][1]

        # move piece
        captured = self.board[square[1]][square[0]]
        current_square = piece.pos[0], piece.pos[1]
        if captured is not None:
            opponent_pieces_alive[captured.index] = False
        self.board[square[1]][square[0]] = piece
        piece.pos[0] = square[0]
        piece.pos[1] = square[1]
        self.board[current_square[1]][current_square[0]] = None

        value, _ = minimax_mod(
            self, depth + 1, not color, alpha, beta, flipped, checked, max_depth
        )
        if depth == 0:
            results.append((self.convert_board(), value))

        # undo move
        if captured is not None:
            opponent_pieces_alive[captured.index] = True
        self.board[square[1]][square[0]] = captured
        piece.pos[0] = current_square[0]
        piece.pos[1] = current_square[1]
        self.board[current_square[1]][current_square[0]] = piece

        if is_minimizing:
            if value < minimax_value:
                minimax_value = value
                beta = min(beta, value)
                if beta < alpha or (not random_choice and beta == alpha):
                    return -10000, None
                best.clear()
            if depth == 0 and value == minimax_value:
                best.append((piece, square))
        if not is_minimizing:
            if value > minimax_value:
                minimax_value = value
                alpha = max(alpha, value)
                if beta < alpha or (not random_choice and beta == alpha):
                    return 10000, None
                best.clear()
            if depth == 0 and value == minimax_value:
                best.append((piece, square))

    best_choice = random.choice(best) if best else None
    if depth == 0:
        return minimax_value, best_choice, results
    else:
        return minimax_value, best_choice


def save_results(board2score):
    array_path = os.path.join("nparrays", f"D{DEPTH}_{str(int(time.time()))[4:]}")
    if not os.path.exists(array_path):
        os.mkdir(array_path)
    inputs, target = [], []
    for k, v in board2score.items():
        inputs.append(k)
        target.append(v)
    save_inputs(os.path.join(array_path, "inputs.bin"), inputs)
    numpy.save(
        os.path.join(array_path, "target.npy"), numpy.array(target, dtype=numpy.float64)
    )


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


if __name__ == "__main__":
    main()
