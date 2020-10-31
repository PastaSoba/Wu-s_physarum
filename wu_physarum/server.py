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
        "r": 1
    }
    return portrayal


grid = CanvasGrid(
    portrayal_method=agent_portrayal,
    grid_width=MODEL_PARAM["width"],
    grid_height=MODEL_PARAM["height"],
    canvas_width=600,
    canvas_height=600
)

server = ModularServer(
    model_cls=WuPhysarum,
    visualization_elements=[grid],
    name="Wu's Physarum Model",
    model_params={"datapoint_filename": "demo.json", "seed": MODEL_PARAM["seed"]},
)
