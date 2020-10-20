from collections import defaultdict
from os import name

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from .model import WuPhysarum
from .lib.setting import MODEL_PARAM


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Color": "red",
        "Filled": "true",
        "Layer": 0,
        "r": 0.5
    }
    return portrayal


class CustomCanvasGrid(CanvasGrid):
    # CHANGED: render関数の動作を軽量化した
    def render(self, model):
        grid_state = defaultdict(list)
        for agt in model.schedule.agents():
            portrayal = self.portrayal_method(agt)
            if portrayal:
                portrayal["x"] = agt.pos[0]
                portrayal["y"] = agt.pos[1]
                grid_state[portrayal["Layer"]].append(portrayal)
        return grid_state


grid = CustomCanvasGrid(
    portrayal_method=agent_portrayal,
    grid_width=MODEL_PARAM["width"],
    grid_height=MODEL_PARAM["height"],
    canvas_width=500,
    canvas_height=500
)

server = ModularServer(
    model_cls=WuPhysarum,
    visualization_elements=[grid],
    name="Wu's Physarum Model",
    model_params={"filename": "test.json", "seed": 13573},
)
