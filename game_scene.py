from UI_BASE.UI.scene import Scene
from UI_BASE.UI.components.button import Button
from UI_BASE.UI.components.container import Container
from UI_BASE.UI.components.text import Text
from UI_BASE.UI.utils import IMAGE
import os
import time
from collections import namedtuple

Piece = namedtuple('Piece',[
    "name", "score", "pos"
])

import pygame
from pygame.locals import *  # noqa
EMPTY = pygame.Surface([1, 1], pygame.SRCALPHA)

class GameScene(Scene):
    def __init__(self, screen, *args, **kwargs):
        super(GameScene, self).__init__(screen, *args, **kwargs)
        white = pygame.Surface([1, 1])
        white.fill((235,236,208))
        black = pygame.Surface([1, 1])
        black.fill((119,149,86))
        self.chess_pos = [[0]*8 for _ in range(8)]
        self.board = [[None]*8 for _ in range(8)]
        self.selected_piece = None
        self.wpieces = [
            Piece("wr",   5, [0, 0]),
            Piece("wn",   3, [0, 1]),
            Piece("wb",   3, [0, 2]),
            Piece("wq",   9, [0, 3]),
            Piece("wk", 200, [0, 4]),
            Piece("wb",   3, [0, 5]),
            Piece("wn",   3, [0, 6]),
            Piece("wr",   5, [0, 7]),
            Piece("wp",   1, [1, 0]),
            Piece("wp",   1, [1, 1]),
            Piece("wp",   1, [1, 2]),
            Piece("wp",   1, [1, 3]),
            Piece("wp",   1, [1, 4]),
            Piece("wp",   1, [1, 5]),
            Piece("wp",   1, [1, 6]),
            Piece("wp",   1, [1, 7]),
        ]
        self.bpieces = [
            Piece("br",   5, [7, 0]),
            Piece("bn",   3, [7, 1]),
            Piece("bb",   3, [7, 2]),
            Piece("bq",   9, [7, 3]),
            Piece("bk", 200, [7, 4]),
            Piece("bb",   3, [7, 5]),
            Piece("bn",   3, [7, 6]),
            Piece("br",   5, [7, 7]),
            Piece("bp",   1, [6, 0]),
            Piece("bp",   1, [6, 1]),
            Piece("bp",   1, [6, 2]),
            Piece("bp",   1, [6, 3]),
            Piece("bp",   1, [6, 4]),
            Piece("bp",   1, [6, 5]),
            Piece("bp",   1, [6, 6]),
            Piece("bp",   1, [6, 7]),
        ]




        for i in range(8):
            for j in range(8):
                x = i*70 + 55
                y = j*70 + 55
                self.chess_pos[i][j] = x, y
                self.add(
                    f"bg_{i}{j}", 
                    Container(
                        white if (i+j)&1==0 else black,
                        width=70, 
                        height=70, 
                        x=x,
                        y=y,
                    ),
                    0
                )
        for i in range(8):
            for j in range(8):
                x, y = self.chess_pos[i][j] 
                self.add(f"indicator_{i}{j}", Button(text="X", x=x, y=y))
                self.get(f"indicator_{i}{j}").hide()
        for i in range(8):
            for j in range(8):
                x, y = self.chess_pos[i][j] 
                self.add(f"board_{i}{j}", Button(image=EMPTY, x=-1, y=-1))
        for p in self.wpieces:
            row, col = p.pos
            self.board[col][row] = p
            self.set_board(row, col, p)
        for p in self.bpieces:
            row, col = p.pos
            self.board[col][row] = p
            self.set_board(row, col, p)

    def set_board(self, row, col, piece):
        self.board[col][row] = piece
        square = self.get(f"board_{col}{row}")
        if piece is None:
            square.hide()
        else:
            square.set_image(IMAGE(f"images/{piece.name}.png", False), 60, 60).set_pos(self.chess_pos[col][row])
            square.show()
            square.on_click = self.get_select_piece_func(piece)

    def get_select_piece_func(self, piece):
        # if piece is None: return lambda:0
        def select_piece():
            print("SELECT")
            if self.selected_piece == piece:
                self.clear_moves()
                self.selected_piece = None
                return
            self.selected_piece = piece
            moves = self.get_possible_moves(piece)
            for move in moves:
                row, col = move
                indicator = self.get(f"indicator_{col}{row}")
                indicator.show()
                indicator.on_click = lambda: self.move(piece, row, col)
            
        return select_piece

    def get_possible_moves(self, piece):
        return [(3, 3), (4, 5)]

    def clear_moves(self):
        for i in range(8):
            for j in range(8):
                self.get(f"indicator_{i}{j}").hide()

    def move(self, piece, row, col):
        p_row, p_col = piece.pos
        self.set_board(p_row, p_col, None)
        piece.pos[0] = row
        piece.pos[1] = col
        self.set_board(row, col, piece)
        self.clear_moves()


    def close(self):
        return super().close()
