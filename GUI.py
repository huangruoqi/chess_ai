from UI_BASE.UI.app import App
from game_scene_pvp import GameScenePVP
from game_scene_pvc import GameScenePVC
from game_scene_pvc2 import GameScenePVC2
from game_scene_cvc import GameSceneCVC
import os
import sys

MAX_HEIGHT = 900

scenes = {
    'pvp': GameScenePVP,
    'pvc': GameScenePVC,
    'pvc2': GameScenePVC2,
    'cvc': GameSceneCVC,
}

app = App(
    scenes[sys.argv[1]],
    800,
    600,
    title="Chess",
)
app.run()
