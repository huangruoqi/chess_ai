from UI_BASE.UI.scene import Scene
from UI_BASE.UI.components.button import Button
from UI_BASE.UI.components.container import Container
from UI_BASE.UI.components.text import Text
from UI_BASE.UI.utils import IMAGE
from chess import Game


import pygame
from pygame.locals import *  # noqa
EMPTY = pygame.Surface([1, 1], pygame.SRCALPHA)

class GameScenePVP(Scene):
    def __init__(self, screen, *args, **kwargs):
        super(GameScenePVP, self).__init__(screen, *args, **kwargs)
        self.chess_pos = [[0]*8 for _ in range(8)]
        self.game = Game()
        self.selected_piece = None
        self.text_display = self.add("text_display", Text("", size=20, x=600, y=100))
        self.current_color = True

        for i in range(8):
            for j in range(8):
                x = i*70 + 55
                y = j*70 + 55
                self.chess_pos[i][j] = x, y
                self.add(
                    f"bg_{i}{j}", 
                    Container(
                        "images/white.png" if (i+j)&1==0 else "images/black.png",
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
                self.add(f"indicator_{i}{j}", Button(image_file="images/black_circle.png", x=x, y=y, width=40, height=40, opacity=0.8), 1)
                self.get(f"indicator_{i}{j}").hide()
        for i in range(8):
            for j in range(8):
                x, y = self.chess_pos[i][j] 
                self.add(f"capture_{i}{j}", Container(image_file="images/black_ring.png", x=x, y=y, width=69, height=69, opacity=0.3), 2)
                self.get(f"capture_{i}{j}").hide()
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

    def set_board(self, row, col, piece):
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
            moves = list(filter(lambda x: self.game.is_legal(*x[1]), moves))
            if len(moves)==0:
                return
            for move in moves:
                row, col = move[1][1]
                if self.game.board[col][row] is not None:
                    indicator = self.get(f"board_{col}{row}")
                    indicator.on_click = (lambda r, c:lambda:self.move(piece, r, c))(row, col)
                    indicator.can_hover = lambda: True
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
                self.get(f"capture_{i}{j}").hide()
        for p in self.game.wpieces:
            if not self.game.wpieces_alive[p.index]: continue
            row, col = p.pos
            self.get(f"board_{col}{row}").on_click = self.get_select_piece_func(p)
            self.get(f"board_{col}{row}").can_hover = lambda: self.current_color
        for p in self.game.bpieces:
            if not self.game.bpieces_alive[p.index]: continue
            row, col = p.pos
            self.get(f"board_{col}{row}").on_click = self.get_select_piece_func(p)
            self.get(f"board_{col}{row}").can_hover = lambda: not self.current_color
            

    def move(self, piece, row, col):
        p_row, p_col = piece.pos
        self.game.move(piece, row, col)
        self.clear_moves()
        self.set_board(p_row, p_col, None)
        self.set_board(row, col, piece)
        self.selected_piece = None
        self.current_color = not self.current_color
        if self.game.is_checkmate(self.current_color):
            self.text_display.change_text(f'{"WBhliatcek"[self.current_color::2]} Checkmate!!!')

