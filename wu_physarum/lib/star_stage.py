from operator import add
from math import sin, cos, radians

from .convex_stage import convex_hull_inner


class StarStage:
    """
    スター型のステージを作るための自作ライブラリ
    """
    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height
        self.__stage = [[0 for j in range(self.height)] for i in range(self.width)]

    def select(self, x: int, y: int) -> None:
        """
        turn to self.__stage[x][y] == 1
        """
        self.__stage[x][y] = 1

    def draw_circle(self, x: int, y: int, radius: int) -> None:
        """
        (x, y) を中心とした半径 radius の円の領域内の値を1にセットする
        """
        for i in range(self.width):
            for j in range(self.height):
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
        return "\n".join(map(str, self.__stage))

    @property
    def stage_region(self):
        """
        エージェント・誘因力の存在可能部分のみ1にマスクされた
        二次元配列を返す

        return: self.__stage (list[int][int])
        """
        return self.__stage
