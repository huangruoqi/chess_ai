from UI_BASE.UI.scene import Scene
from UI_BASE.UI.components.button import Button
from UI_BASE.UI.components.container import Container
from UI_BASE.UI.components.text import Text
from UI_BASE.UI.utils import IMAGE
from chess import Game


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
        self.game = Game()
        self.selected_piece = None

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
                self.add(f"indicator_{i}{j}", Button(image=IMAGE(f"images/black_circle.png", False), x=x, y=y, width=40, height=40, opacity=0.8), 1)
                self.get(f"indicator_{i}{j}").hide()
        for i in range(8):
            for j in range(8):
                x, y = self.chess_pos[i][j] 
                self.add(f"capture_{i}{j}", Container(image=IMAGE(f"images/black_ring.png", False), x=x, y=y, width=69, height=69, opacity=0.3), 2)
                self.get(f"capture_{i}{j}").hide()
        for i in range(8):
            for j in range(8):
                x, y = self.chess_pos[i][j] 
                self.add(f"board_{i}{j}", Button(image=EMPTY, x=-1, y=-1))

        for p in self.game.wpieces:
            row, col = p.pos
            self.set_board(row, col, p)
        for p in self.game.bpieces:
            row, col = p.pos
            self.set_board(row, col, p)

    def set_board(self, row, col, piece):
        self.game.board[col][row] = piece
        square = self.get(f"board_{col}{row}")
        if piece is None:
            square.hide()
        else:
            square.set_image(IMAGE(f"images/{'bw'[piece.color]+piece.type}.png", False), 60, 60).set_pos(self.chess_pos[col][row])
            square.show()
            square.on_click = self.get_select_piece_func(piece)

    def get_select_piece_func(self, piece):
        def select_piece():
            self.clear_moves()
            if self.selected_piece == piece:
                self.selected_piece = None
                return
            self.selected_piece = piece
            moves = self.game.get_possible_moves(piece)
            print(moves)
            for move in moves:
                row, col = move[1]
                if self.game.board[col][row] is not None:
                    indicator = self.get(f"board_{col}{row}")
                    indicator.on_click = (lambda r, c:lambda:self.move(piece, r, c))(row, col)
                    self.get(f"capture_{col}{row}").show()
                else:
                    indicator = self.get(f"indicator_{col}{row}")
                    indicator.show()
                    indicator.on_click = (lambda r, c:lambda:self.move(piece, r, c))(row, col)
        return select_piece


    def clear_moves(self):
        for i in range(8):
            for j in range(8):
                self.get(f"indicator_{i}{j}").hide()
        for p in self.game.wpieces:
            row, col = p.pos
            self.get(f"board_{col}{row}").on_click = self.get_select_piece_func(p)
            self.get(f"capture_{col}{row}").hide()
        for p in self.game.bpieces:
            row, col = p.pos
            self.get(f"board_{col}{row}").on_click = self.get_select_piece_func(p)
            self.get(f"capture_{col}{row}").hide()
            

    def move(self, piece, row, col):
        p_row, p_col = piece.pos
        self.game.move(piece, row, col)
        self.set_board(p_row, p_col, None)
        self.set_board(row, col, piece)
        self.clear_moves()
        self.selected_piece = None


    def close(self):
        return super().close()
