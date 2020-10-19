from operator import add
from math import sin, cos, radians

from .convex import convex_hull_inner
from .setting import MODEL_PARAM


class StarStage:
    """
    スター型のステージを作るための自作ライブラリ
    """
    def __init__(self) -> None:
        self.stage = [[0 for j in range(MODEL_PARAM["height"])] for i in range(MODEL_PARAM["width"])]

    def select(self, x: int, y: int) -> None:
        """
        turn to self.stage[x][y] == 1
        """
        self.stage[x][y] = 1

    def draw_circle(self, x: int, y: int, radius: int) -> None:
        """
        (x, y) を中心とした半径 radius の円の領域内の値を1にセットする
        """
        for i in range(MODEL_PARAM["width"]):
            for j in range(MODEL_PARAM["height"]):
                if (i - x)**2 + (j - y)**2 <= radius**2:
                    self.select(i, j)

    def draw_rect(self, x: int, y: int, offset: float, width: float, height: float, degree: float):
        """
        (x, y)を起点とし、そこから(r, θ) = (offset, degree)離れた場所を
        最近接辺の中心とする幅width, 高さheightの長方形を作る
        """

        rad = radians(degree)
        midpoint = (x + offset * cos(rad), y + offset * sin(rad))
        vertex = [
            tuple(map(add, midpoint, (width * sin(rad) / 2, -width * cos(rad) / 2))),
            tuple(map(add, midpoint, (-width * sin(rad) / 2, width * cos(rad) / 2))),
            tuple(map(add, midpoint, (-width * sin(rad) / 2 + height * cos(rad), width * cos(rad) / 2 + height * sin(rad)))),
            tuple(map(add, midpoint, (width * sin(rad) / 2 + height * cos(rad), -width * cos(rad) / 2 + height * sin(rad)))),
        ]
        # 整数化とタプル化
        vertex = tuple([tuple(map(round, v)) for v in vertex])
        # vertexを反時計回りに並べ替える
        inner_point = convex_hull_inner(vertex)
        for i, j in inner_point:
            self.select(i, j)

    def __str__(self):
        print("cells are indexed by [x][y]")
        return "\n".join(map(str, self.stage))

    def get(self):
        return self.stage
