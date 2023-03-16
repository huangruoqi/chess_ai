from UI_BASE.UI.app import App
from scenes.game_scene_pvp import GameScenePVP
from scenes.game_scene_pvc import GameScenePVC
from scenes.game_scene_pvc2 import GameScenePVC2
from scenes.game_scene_cvc import GameSceneCVC
from scenes.game_scene_avc import GameSceneAVC
from scenes.game_scene_ava import GameSceneAVA
import os
import sys

MAX_HEIGHT = 900

scenes = {
    'pvp': GameScenePVP,
    'pvc': GameScenePVC,
    'pvc2': GameScenePVC2,
    'cvc': GameSceneCVC,
    'avc': GameSceneAVC,
    'ava': GameSceneAVA,
}

app = App(
    [scenes[sys.argv[1]]],
    800,
    600,
    title="Chess",
)
app.run()
