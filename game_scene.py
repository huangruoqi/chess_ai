from UI_BASE.UI.scene import Scene
from UI_BASE.UI.components.button import Button
from UI_BASE.UI.components.container import Container
from UI_BASE.UI.components.text import Text
from UI_BASE.UI.utils import IMAGE
import os
import time

import pygame
from pygame.locals import *  # noqa

class GameScene(Scene):
    def __init__(self, screen, *args, **kwargs):
        super(GameScene, self).__init__(screen, *args, **kwargs)
        white = pygame.Surface([1, 1])
        white.fill((235,236,208))
        black = pygame.Surface([1, 1])
        black.fill((119,149,86))
        chess_pos = [[0]*8 for _ in range(8)]
        for i in range(8):
            for j in range(8):
                x = i*70 + 55
                y = j*70 + 55
                chess_pos[i][j] = x, y
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
                x, y = chess_pos[i][j] 
                self.add(
                    f"indicator_{i}{j}", 
                    Button(
                        text="X",
                        x=x,
                        y=y,
                    ),
                    1
                )
        for i in range(8):
            for j in range(8):
                x, y = chess_pos[i][j] 
                self.add(
                    f"board_{i}{j}", 
                    Button(
                        image=IMAGE("images/wr.png", False),
                        width=60, 
                        height=60,
                        x=x,
                        y=y,
                    ),
                    1
                )

    def close(self):
        return super().close()
