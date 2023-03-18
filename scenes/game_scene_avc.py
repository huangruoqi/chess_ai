from UI_BASE.UI.scene import Scene
from UI_BASE.UI.components.button import Button
from UI_BASE.UI.components.container import Container
from UI_BASE.UI.components.text import Text
from UI_BASE.UI.utils import IMAGE
import os
import pygame
from pygame.locals import *  # noqa
from chess import Game
import tensorflow as tf
from utils import Chess_Model

EMPTY = pygame.Surface([1, 1], pygame.SRCALPHA)

DEPTH = 3
MODEL_NAME = "init/00"


class GameSceneAVC(Scene):
    def __init__(self, screen, *args, **kwargs):
        super(GameSceneAVC, self).__init__(screen, *args, **kwargs)
        white = pygame.Surface([1, 1])
        white.fill((235, 236, 208))
        black = pygame.Surface([1, 1])
        black.fill((119, 149, 86))
        self.chess_pos = [[0] * 8 for _ in range(8)]
        self.game = Game()
        self.selected_piece = None
        self.text_display = self.add("text_display", Text("", size=20, x=600, y=100))

        for i in range(8):
            for j in range(8):
                x = i * 70 + 55
                y = j * 70 + 55
                self.chess_pos[i][j] = x, y
                self.add(
                    f"bg_{i}{j}",
                    Container(
                        "images/white.png" if (i + j) & 1 == 0 else "images/black.png",
                        width=70,
                        height=70,
                        x=x,
                        y=y,
                    ),
                    0,
                )
        for i in range(8):
            for j in range(8):
                x, y = self.chess_pos[i][j]
                self.add(f"board_{i}{j}", Button(x=-1, y=-1))

        for p in self.game.wpieces:
            row, col = p.pos
            self.set_board(row, col, p)
        for p in self.game.bpieces:
            row, col = p.pos
            self.set_board(row, col, p)

        self.stop = False
        self.color = True
        self.wait_time = 0

        self.chess_model = Chess_Model()
        self.model = self.chess_model.load_model(os.path.join("model", MODEL_NAME))[1]

    def set_board(self, row, col, piece):
        square = self.get(f"board_{col}{row}")
        if piece is None:
            square.hide()
        else:
            square.set_image(
                IMAGE(f"images/{'bw'[piece.color]+piece.type}.png", False), 60, 60
            ).set_pos(self.chess_pos[col][row])
            square.show()
            square.can_hover = lambda: False

    def computer_move(self, color):
        if color:
            piece, move = self.game.get_ai_move(self.model, color)
            p_row, p_col = piece.pos
            row, col = move
            self.game.move(piece, *move)
            self.set_board(p_row, p_col, None)
            self.set_board(row, col, piece)
        else:
            piece, move = self.game.get_computer_move(color, DEPTH)
            p_row, p_col = piece.pos
            row, col = move
            self.game.move(piece, *move)
            self.set_board(p_row, p_col, None)
            self.set_board(row, col, piece)
        if self.game.is_checkmate(not color):
            self.stop = True
            self.text_display.change_text("BWlhaictke"[color::2] + " Checkmate!!!")

    def update(self, delta_time, mouse_pos, clicked, pressed):
        super().update(delta_time, mouse_pos, clicked, pressed)
        if self.stop:
            return
        if self.wait_time > 0.05:
            self.computer_move(self.color)
            self.wait_time = 0
            self.color = not self.color
        self.wait_time += delta_time
