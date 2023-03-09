from UI_BASE.UI.app import App
from game_scene import GameScene
import os
import sys

MAX_HEIGHT = 900


app = App(
    GameScene,
    800,
    600,
    title="Chess",
)
app.run()
