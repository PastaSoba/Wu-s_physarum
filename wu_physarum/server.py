# from collections import defaultdict

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


# class CustomCanvasGrid(CanvasGrid):
#     # CHANGED: render関数の動作を軽量化した
#     def __init__(
#         self,
#         portrayal_method,
#         grid_width,
#         grid_height,
#         canvas_width=500,
#         canvas_height=500,
#     ):
#         super().__init__(
#             portrayal_method,
#             grid_width,
#             grid_height,
#             canvas_width,
#             canvas_height,
#         )
#         self.colormap = plt.get_cmap('viridis')
#         self.maxiter = 100

#     def get_color(self, chenu):
#         return self.colormap(chenu / self.maxiter * 256)

#     def __test(self, x, y, value):
#         color = self.get_color(value)
#         color_code = '#{}{}{}'.format(
#             hex(int(color[0] + 0.5)),
#             hex(int(color[1] + 0.5)),
#             hex(int(color[2] + 0.5))
#         ).replace('0x', '')
#         return {
#             "Shape": "rect",
#             "w": 1,
#             "h": 1,
#             "x": x,
#             "y": y,
#             "Color": color_code,
#             "Filled": "true",
#         }

#     def create_stage_portrayal(self, chenu_map_list):
#         return [self.__test(i, j, val) for i, row in enumerate(chenu_map_list) for j, val in enumerate(row)]

#     def render(self, model):
#         grid_state = defaultdict(list)
#         chenu_map_list = model.chenu_map.tolist()
#         grid_state[1] = self.create_stage_portrayal(chenu_map_list)

#         return grid_state


# ltc_grid = CustomCanvasGrid(
#     portrayal_method=agent_portrayal,
#     grid_width=MODEL_PARAM["width"],
#     grid_height=MODEL_PARAM["height"],
#     canvas_width=600,
#     canvas_height=600
# )

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
    model_params={"datapoint_filename": "test.json", "seed": 13573},
)
