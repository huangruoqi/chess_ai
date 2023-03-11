from collections import namedtuple
Piece = namedtuple('Piece',[
    "color", "type", "score", "pos", "moved"
])

DEPTH = 4

class Game:
    def __init__(self):
        self.board = [[None]*8 for _ in range(8)]
        self.bpieces = [
            Piece(False, "r",   5, [0, 0], [False]),
            Piece(False, "n",   3, [0, 1], [False]),
            Piece(False, "b",   3, [0, 2], [False]),
            Piece(False, "q",   9, [0, 3], [False]),
            Piece(False, "k", 200, [0, 4], [False]),
            Piece(False, "b",   3, [0, 5], [False]),
            Piece(False, "n",   3, [0, 6], [False]),
            Piece(False, "r",   5, [0, 7], [False]),
            Piece(False, "p",   1, [1, 0], [False]),
            Piece(False, "p",   1, [1, 1], [False]),
            Piece(False, "p",   1, [1, 2], [False]),
            Piece(False, "p",   1, [1, 3], [False]),
            Piece(False, "p",   1, [1, 4], [False]),
            Piece(False, "p",   1, [1, 5], [False]),
            Piece(False, "p",   1, [1, 6], [False]),
            Piece(False, "p",   1, [1, 7], [False]),
        ]
        self.wpieces = [
            Piece(True, "r",   5, [7, 0], [False]),
            Piece(True, "n",   3, [7, 1], [False]),
            Piece(True, "b",   3, [7, 2], [False]),
            Piece(True, "q",   9, [7, 3], [False]),
            Piece(True, "k", 200, [7, 4], [False]),
            Piece(True, "b",   3, [7, 5], [False]),
            Piece(True, "n",   3, [7, 6], [False]),
            Piece(True, "r",   5, [7, 7], [False]),
            Piece(True, "p",   1, [6, 0], [False]),
            Piece(True, "p",   1, [6, 1], [False]),
            Piece(True, "p",   1, [6, 2], [False]),
            Piece(True, "p",   1, [6, 3], [False]),
            Piece(True, "p",   1, [6, 4], [False]),
            Piece(True, "p",   1, [6, 5], [False]),
            Piece(True, "p",   1, [6, 6], [False]),
            Piece(True, "p",   1, [6, 7], [False]),
        ]
        for p in self.wpieces:
            row, col = p.pos
            self.board[col][row] = p
        for p in self.bpieces:
            row, col = p.pos
            self.board[col][row] = p

    def move(self, piece, row, col):
        if self.board[col][row] is not None:
            self.capture(self.board[col][row])
        piece.pos[0] = row
        piece.pos[1] = col
        piece.moved[0] = True

    def capture(self, piece):
        if piece.color:
            self.wpieces.remove(piece)
        else:
            self.bpieces.remove(piece)

    def get_possible_moves(self, piece):
        return {
            'p': Rules.pawn,
            'r': Rules.rook,
            'q': Rules.queen,
            'b': Rules.bishop,
            'k': Rules.king,
            'n': Rules.knight,
        }[piece.type](piece, self.board)

    def get_all_moves(self, color):
        pieces = self.wpieces if color else self.bpieces
        moves = []
        for p in pieces:
            moves.extend([(i[0], (p, i[1])) for i in self.get_possible_moves(p)])
        return moves

    def get_computer_move(self):
        move = self.minimax(0, False, -10000, 10000)
        return move[1]

    def get_score(self):
        p_score = 0
        for p in self.bpieces:
            p_score+=p.score
        for p in self.wpieces:
            p_score-=p.score
        white_moves = self.get_all_moves(True)
        black_moves = self.get_all_moves(False)
        t_score = 0
        for i in white_moves:
            t_score -= i[0]
        for i in black_moves:
            t_score += i[0]

        return p_score + t_score//2

    def minimax(self, depth, color, alpha, beta):
        opponent_pieces = self.bpieces if color else self.wpieces
        if depth >= DEPTH:
            return self.get_score(), None
        best_piece = None
        best_move = None
        moves = self.get_all_moves(color)
        moves.sort(reverse=not color)
        minimax_value = 10000 if color else -10000
        for move in moves:
            piece = move[1][0]
            square = move[1][1]
            captured = self.board[square[1]][square[0]]
            current_square = piece.pos[0], piece.pos[1]
            if captured is not None:
                opponent_pieces.remove(captured)
            self.board[square[1]][square[0]] = piece
            piece.pos[0] = square[0]
            piece.pos[1] = square[1]
            self.board[current_square[1]][current_square[0]] = None
            value, _ = self.minimax(depth+1, not color, alpha, beta)
            if captured is not None:
                opponent_pieces.append(captured)
            self.board[square[1]][square[0]] = captured
            piece.pos[0] = current_square[0]
            piece.pos[1] = current_square[1]
            self.board[current_square[1]][current_square[0]] = piece
            if color and value < minimax_value:
                minimax_value = value
                beta = min(beta, value)
                if beta <= alpha:
                    return -10000, None
                best_piece = piece
                best_move = square
            if not color and value > minimax_value:
                minimax_value = value
                alpha = max(alpha, value)
                if beta <= alpha:
                    return 10000, None
                best_piece = piece
                best_move = square
        
        return (minimax_value, (best_piece, best_move))
            
            


    



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
        if left and left.color!=piece.color:
            moves.append((left.score, (next_row, col - 1)))
        if right and right.color!=piece.color:
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
                if p.color!=piece.color:
                    moves.append((p.score, (r, col)))
                break
        for r in range(row - 1, -1, -1):
            p = Rules.get(board, r, col)
            if p is None:
                moves.append((0, (r, col)))
            else:
                if p.color!=piece.color:
                    moves.append((p.score, (r, col)))
                break
        for c in range(col + 1, 8):
            p = Rules.get(board, row, c)
            if p is None:
                moves.append((0, (row, c)))
            else:
                if p.color!=piece.color:
                    moves.append((p.score, (row, c)))
                break
        for c in range(col - 1, -1, -1):
            p = Rules.get(board, row, c)
            if p is None:
                moves.append((0, (row, c)))
            else:
                if p.color!=piece.color:
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
                if p.color!=piece.color:
                    moves.append((p.score, (r, col)))
                break
        for r in range(row - 1, -1, -1):
            p = Rules.get(board, r, col)
            if p is None:
                moves.append((0, (r, col)))
            else:
                if p.color!=piece.color:
                    moves.append((p.score, (r, col)))
                break
        for c in range(col + 1, 8):
            p = Rules.get(board, row, c)
            if p is None:
                moves.append((0, (row, c)))
            else:
                if p.color!=piece.color:
                    moves.append((p.score, (row, c)))
                break
        for c in range(col - 1, -1, -1):
            p = Rules.get(board, row, c)
            if p is None:
                moves.append((0, (row, c)))
            else:
                if p.color!=piece.color:
                    moves.append((p.score, (row, c)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row - i, col - i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row - i, col - i)))
            else:
                if p.color!=piece.color:
                    moves.append((p.score, (row - i, col - i)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row + i, col + i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row + i, col + i)))
            else:
                if p.color!=piece.color:
                    moves.append((p.score, (row + i, col + i)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row - i, col + i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row - i, col + i)))
            else:
                if p.color!=piece.color:
                    moves.append((p.score, (row - i, col + i)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row + i, col - i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row + i, col - i)))
            else:
                if p.color!=piece.color:
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
                if p.color!=piece.color:
                    moves.append((p.score, (row - i, col - i)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row + i, col + i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row + i, col + i)))
            else:
                if p.color!=piece.color:
                    moves.append((p.score, (row + i, col + i)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row - i, col + i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row - i, col + i)))
            else:
                if p.color!=piece.color:
                    moves.append((p.score, (row - i, col + i)))
                break
        for i in range(1, 8):
            p = Rules.get(board, row + i, col - i)
            if p is False:
                break
            if p is None:
                moves.append((0, (row + i, col - i)))
            else:
                if p.color!=piece.color:
                    moves.append((p.score, (row + i, col - i)))
                break
        return moves

    def king(piece, board):
        moves = []
        row, col = piece.pos
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i==0==j: continue
                p = Rules.get(board, row + i, col + j)
                if p is False:
                    continue
                if p is None:
                    moves.append((0, (row + i, col + j)))
                elif p.color!=piece.color:
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
                    elif p.color!=piece.color:
                        moves.append((p.score, (r, c)))
        return moves

    def get(board, row, col):
        if 0<=row<=7 and 0<=col<=7:
            return board[col][row]
        else:
            return False
