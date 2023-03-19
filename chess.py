import random
import time
from collections import namedtuple
import tensorflow as tf
from tensorflow.keras import layers
import numpy as np

Piece = namedtuple(
    "Piece", ["color", "type", "score", "pos", "start_pos", "moved", "index", ]
)

Result = namedtuple("Result", ["winner", "turn", "piece_score"])

AI_MARGIN = 0.1
DEBUG = False

def timeit(func):
    def timeit_func(*args, **kwargs):
        t = time.time()
        result = func(*args, **kwargs)
        print(f"{int(time.time()-t)} seconds")
        return result

    return timeit_func


class Game:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]
        self.bpieces = [
            Piece(False, "r", 5, [0, 0], (0, 0), [False], 0),
            Piece(False, "n", 3, [0, 1], (0, 1), [False], 1),
            Piece(False, "b", 3, [0, 2], (0, 2), [False], 2),
            Piece(False, "q", 9, [0, 3], (0, 3), [False], 3),
            Piece(False, "k", 200, [0, 4], (0, 4), [False], 4),
            Piece(False, "b", 3, [0, 5], (0, 5), [False], 5),
            Piece(False, "n", 3, [0, 6], (0, 6), [False], 6),
            Piece(False, "r", 5, [0, 7], (0, 7), [False], 7),
            Piece(False, "p", 1, [1, 0], (1, 0), [False], 8),
            Piece(False, "p", 1, [1, 1], (1, 1), [False], 9),
            Piece(False, "p", 1, [1, 2], (1, 2), [False], 10),
            Piece(False, "p", 1, [1, 3], (1, 3), [False], 11),
            Piece(False, "p", 1, [1, 4], (1, 4), [False], 12),
            Piece(False, "p", 1, [1, 5], (1, 5), [False], 13),
            Piece(False, "p", 1, [1, 6], (1, 6), [False], 14),
            Piece(False, "p", 1, [1, 7], (1, 7), [False], 15),
        ]
        self.bpieces_alive = [True] * 16
        self.wpieces = [
            Piece(True, "r", 5, [7, 0], (7, 0), [False], 0),
            Piece(True, "n", 3, [7, 1], (7, 1), [False], 1),
            Piece(True, "b", 3, [7, 2], (7, 2), [False], 2),
            Piece(True, "q", 9, [7, 3], (7, 3), [False], 3),
            Piece(True, "k", 200, [7, 4], (7, 4), [False], 4),
            Piece(True, "b", 3, [7, 5], (7, 5), [False], 5),
            Piece(True, "n", 3, [7, 6], (7, 6), [False], 6),
            Piece(True, "r", 5, [7, 7], (7, 7), [False], 7),
            Piece(True, "p", 1, [6, 0], (6, 0), [False], 8),
            Piece(True, "p", 1, [6, 1], (6, 1), [False], 9),
            Piece(True, "p", 1, [6, 2], (6, 2), [False], 10),
            Piece(True, "p", 1, [6, 3], (6, 3), [False], 11),
            Piece(True, "p", 1, [6, 4], (6, 4), [False], 12),
            Piece(True, "p", 1, [6, 5], (6, 5), [False], 13),
            Piece(True, "p", 1, [6, 6], (6, 6), [False], 14),
            Piece(True, "p", 1, [6, 7], (6, 7), [False], 15),
        ]
        self.wpieces_alive = [True] * 16
        for p in self.wpieces:
            row, col = p.pos
            self.board[col][row] = p
        for p in self.bpieces:
            row, col = p.pos
            self.board[col][row] = p

    def reset(self):
        self.board = [[None] * 8 for _ in range(8)]
        for i in range(8):
            for j in range(8):
                self.board[i][j] = None
        for p in self.wpieces:
            row, col = p.start_pos
            p.pos[0] = row
            p.pos[1] = col
            self.board[col][row] = p
            p.moved[0] = False
        for p in self.bpieces:
            row, col = p.start_pos
            p.pos[0] = row
            p.pos[1] = col
            self.board[col][row] = p
            p.moved[0] = False
        for i in range(16):
            self.bpieces_alive[i] = True
            self.wpieces_alive[i] = True

    def move(self, piece, row, col):
        p_row, p_col = piece.pos
        if self.board[col][row] is not None:
            self.capture(self.board[col][row])
        self.board[col][row] = piece
        self.board[p_col][p_row] = None
        piece.pos[0] = row
        piece.pos[1] = col
        piece.moved[0] = True

    def capture(self, piece):
        if piece.color:
            self.wpieces_alive[piece.index] = False
        else:
            self.bpieces_alive[piece.index] = False

    def move_and_run(self, piece, square, func):
        opponent_pieces_alive = (
            self.bpieces_alive if piece.color else self.wpieces_alive
        )
        # move piece
        captured = self.board[square[1]][square[0]]
        current_square = piece.pos[0], piece.pos[1]
        if captured is not None:
            opponent_pieces_alive[captured.index] = False
        self.board[square[1]][square[0]] = piece
        piece.pos[0] = square[0]
        piece.pos[1] = square[1]
        self.board[current_square[1]][current_square[0]] = None

        result = func()
        # undo move
        if captured is not None:
            opponent_pieces_alive[captured.index] = True
        self.board[square[1]][square[0]] = captured
        piece.pos[0] = current_square[0]
        piece.pos[1] = current_square[1]
        self.board[current_square[1]][current_square[0]] = piece
        return result

    def is_checkmate(self, color):
        for move in self.get_all_moves(color):
            if self.is_legal(move[1][0], move[1][1]):
                return False
        return True

    def is_legal(self, piece, square):
        return self.move_and_run(piece, square, lambda: not self.is_check(piece.color))

    def is_check(self, color):
        moves = self.get_all_moves(not color)
        if len(moves) == 0:
            return False
        return sorted(moves, reverse=True)[0][0] == 200

    def get_possible_moves(self, piece):
        return [
            (i[0], (piece, i[1]))
            for i in {
                "p": Rules.pawn,
                "r": Rules.rook,
                "q": Rules.queen,
                "b": Rules.bishop,
                "k": Rules.king,
                "n": Rules.knight,
            }[piece.type](piece, self.board)
        ]

    def get_all_moves(self, color):
        pieces = self.wpieces if color else self.bpieces
        pieces_alive = self.wpieces_alive if color else self.bpieces_alive
        moves = []
        for p in pieces:
            if pieces_alive[p.index]:
                moves.extend(self.get_possible_moves(p))
        return moves

    def get_real_moves(self, color):
        return list(filter(lambda x: self.is_legal(*x[1]), self.get_all_moves(color)))

    def get_score(self, flipped):
        p_score = 0
        for p in self.bpieces:
            if self.bpieces_alive[p.index]:
                p_score += p.score
        for p in self.wpieces:
            if self.wpieces_alive[p.index]:
                p_score -= p.score
        white_moves = self.get_all_moves(True)
        black_moves = self.get_all_moves(False)
        t_score = 0
        for i in white_moves:
            t_score -= i[0]
        for i in black_moves:
            t_score += i[0]
        score = p_score + t_score // 4
        return -score if flipped else score

    def get_piece_score(self, flipped):
        p_score = 0
        for p in self.bpieces:
            if self.bpieces_alive[p.index]:
                p_score += p.score
        for p in self.wpieces:
            if self.wpieces_alive[p.index]:
                p_score -= p.score
        assert abs(p_score) < 100
        return -p_score if flipped else p_score

    def minimax(self, depth, color, alpha, beta, flipped, checked, max_depth):
        random_choice = False
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

            value, _ = self.minimax(
                depth + 1, not color, alpha, beta, flipped, checked, max_depth
            )

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
        return (minimax_value, best_choice)

    def get_computer_move(self, color, depth):
        score, move = self.minimax(0, color, -10000, 10000, color, True, depth)
        return move

    def get_ai_move(self, model, color):
        moves = self.get_real_moves(color)
        output = model.predict(self.get_moves_input(moves), verbose=0)
        output = [x[0] if color else -x[0] for x in output]
        if DEBUG:
            print(output)
        output = [(b, a) for a, b in enumerate(output)]
        max_value = max(output)[0]
        candidates = list(filter(lambda x: x[0]>max_value-AI_MARGIN, output))
        return moves[random.choice(candidates)[1]][1]

    def get_moves_input(self, moves):
        result = []
        for move in moves:
            piece, square = move[1]
            inputs = self.move_and_run(piece, square, lambda: self.convert_board())
            result.append(inputs)
        return np.array(result)

    def convert_board(self):
        piece2index = {
            p: [int(j == i) for j in range(6)] for i, p in enumerate("kqrbnp")
        }
        board_code = []
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece is None:
                    board_code.extend([0] * 7)
                else:
                    board_code.extend(piece2index[piece.type])
                    board_code.append(int(piece.color))
        return board_code

    # @timeit
    def run_game_cvc(self):
        color = True
        depth = 2
        turn = 0
        while 1:
            turn += 1
            move = self.get_computer_move(color, depth)
            piece, square = move
            self.move(piece, *square)
            if self.is_checkmate(not color):
                return Result(color, turn, self.get_piece_score(True))
            color = not color
            if turn > 200:
                return Result(None, turn, self.get_piece_score(True))

    # @timeit
    def run_game_avc(self, model, depth):
        color = True
        turn = 0
        previous_move2 = None
        previous_move1 = None

        while 1:
            turn += 1
            if color:
                move = self.get_ai_move(model, color)
                piece, square = move
                self.move(piece, *square)
            else:
                move = self.get_computer_move(color, depth)
                piece, square = move
                if previous_move2 == move:
                    return Result(None, turn, self.get_piece_score(True))
                self.move(piece, *square)
                previous_move2 = previous_move1
                previous_move1 = move
            if self.is_checkmate(not color):
                return Result(color, turn, self.get_piece_score(True))
            color = not color
            if turn > 200:
                return Result(None, turn, self.get_piece_score(True))

    def run_game_ava(self, model1, model2):
        color = True
        turn = 0

        while 1:
            turn += 1
            if color:
                move = self.get_ai_move(model1, color)
                piece, square = move
                self.move(piece, *square)
            else:
                move = self.get_ai_move(model2, color)
                piece, square = move
                self.move(piece, *square)
            if self.is_checkmate(not color):
                return Result(color, turn, self.get_piece_score(True))
            color = not color
            if turn > 200:
                return Result(None, turn, self.get_piece_score(True))


class Rules:
    def pawn(piece, board):
        moves = []
        row, col = piece.pos
        next_row = row + [1, -1][piece.color]
        front = Rules.get(board, next_row, col)
        left = Rules.get(board, next_row, col - 1)
        right = Rules.get(board, next_row, col + 1)
        if front is None:
            moves.append((0, (next_row, col)))
            if not piece.moved[0]:
                next_2_row = row + [2, -2][piece.color]
                if Rules.get(board, next_2_row, col) is None:
                    moves.append((0, (next_2_row, col)))
        if left and left.color != piece.color:
            moves.append((left.score, (next_row, col - 1)))
        if right and right.color != piece.color:
            moves.append((right.score, (next_row, col + 1)))
        return moves

    def rook(piece, board):
        moves = []
        row, col = piece.pos
        for r in range(row + 1, 8):
            p = Rules.get(board, r, col)
            if p is None:
                moves.append((0, (r, col)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (r, col)))
                break
        for r in range(row - 1, -1, -1):
            p = Rules.get(board, r, col)
            if p is None:
                moves.append((0, (r, col)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (r, col)))
                break
        for c in range(col + 1, 8):
            p = Rules.get(board, row, c)
            if p is None:
                moves.append((0, (row, c)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (row, c)))
                break
        for c in range(col - 1, -1, -1):
            p = Rules.get(board, row, c)
            if p is None:
                moves.append((0, (row, c)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (row, c)))
                break
        return moves

    def queen(piece, board):
        moves = []
        row, col = piece.pos
        for r in range(row + 1, 8):
            p = Rules.get(board, r, col)
            if p is None:
                moves.append((0, (r, col)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (r, col)))
                break
        for r in range(row - 1, -1, -1):
            p = Rules.get(board, r, col)
            if p is None:
                moves.append((0, (r, col)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (r, col)))
                break
        for c in range(col + 1, 8):
            p = Rules.get(board, row, c)
            if p is None:
                moves.append((0, (row, c)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (row, c)))
                break
        for c in range(col - 1, -1, -1):
            p = Rules.get(board, row, c)
            if p is None:
                moves.append((0, (row, c)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (row, c)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row - i, col - i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row - i, col - i)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (row - i, col - i)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row + i, col + i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row + i, col + i)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (row + i, col + i)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row - i, col + i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row - i, col + i)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (row - i, col + i)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row + i, col - i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row + i, col - i)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (row + i, col - i)))
                break
        return moves

    def bishop(piece, board):
        moves = []
        row, col = piece.pos
        for i in range(1, 8):
            p = Rules.get(board, row - i, col - i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row - i, col - i)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (row - i, col - i)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row + i, col + i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row + i, col + i)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (row + i, col + i)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row - i, col + i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row - i, col + i)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (row - i, col + i)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row + i, col - i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row + i, col - i)))
            else:
                if p.color != piece.color:
                    moves.append((p.score, (row + i, col - i)))
                break
        return moves

    def king(piece, board):
        moves = []
        row, col = piece.pos
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 == j:
                    continue
                p = Rules.get(board, row + i, col + j)
                if p is False:
                    continue
                if p is None:
                    moves.append((0, (row + i, col + j)))
                elif p.color != piece.color:
                    moves.append((p.score, (row + i, col + j)))
        return moves

    def knight(piece, board):
        moves = []
        row, col = piece.pos
        for a, b in [(1, 2), (2, 1)]:
            for i in (1, -1):
                for j in (1, -1):
                    r, c = row + a * i, col + b * j
                    p = Rules.get(board, r, c)
                    if p is False:
                        continue
                    if p is None:
                        moves.append((0, (r, c)))
                    elif p.color != piece.color:
                        moves.append((p.score, (r, c)))
        return moves

    def get(board, row, col):
        if 0 <= row <= 7 and 0 <= col <= 7:
            return board[col][row]
        else:
            return False


if __name__ == "__main__":
    model = tf.keras.Sequential(
        [
            layers.Dense(600, input_shape=(448,), activation="relu", name="layer1"),
            layers.Dense(400, activation="relu", name="layer2"),
            layers.Dense(128, activation="relu", name="layer3"),
            layers.Dense(32, activation="sigmoid", name="layer4"),
            layers.Dense(8, activation="sigmoid", name="layer5"),
            layers.Dense(1, activation="sigmoid", name="layer6"),
        ]
    )
    game = Game()
    for i in range(10000):
        game.reset()
        print(game.run_game_ava(model, model))
        print(model.get_weights()[0][0][:20])
