from UI_BASE.UI.app import App
from game_scene_pvp import GameScenePVP
from game_scene_pvc import GameScenePVC
import os
import sys

MAX_HEIGHT = 900

scenes = {
    'pvp': GameScenePVP,
    'pvc': GameScenePVC,
}

app = App(
    scenes[sys.argv[1]],
    800,
    600,
    title="Chess",
)
app.run()
