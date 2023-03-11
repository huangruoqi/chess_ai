from collections import namedtuple
Piece = namedtuple('Piece',[
    "color", "type", "score", "pos", "moved"
])

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



class Rules:
    def pawn(piece, board):
        moves = []
        row, col = piece.pos
        next_row = row + [1, -1][piece.color]
        if Rules.get(board, next_row, col) is None:
            moves.append((next_row, col))
        left = Rules.get(board, next_row, col - 1)
        right = Rules.get(board, next_row, col + 1)
        if left and left.color!=piece.color:
            moves.append((next_row, col - 1))
        if right and right.color!=piece.color:
            moves.append((next_row, col + 1))
        if not piece.moved[0]:
            next_row = row + [2, -2][piece.color]
            if Rules.get(board, next_row, col) is None:
                moves.append((next_row, col))
        return moves

    def rook(piece, board):
        return []

    def queen(piece, board):
        return []

    def bishop(piece, board):
        return []

    def king(piece, board):
        return []

    def knight(piece, board):
        return []

    def get(board, row, col):
        if 0<=row<=7 and 0<=col<=7:
            return board[col][row]
        else:
            return False
