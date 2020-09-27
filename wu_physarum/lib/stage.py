from operator import add
from math import sin, cos, radians

from .convex import (
    convex_hull_vertex,
    convex_hull_edge,
    convex_hull_inner
)


class Stage:
    """
    スター型のステージを作るための自作ライブラリ
    Stage(10, 3) =
    [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    """
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.stage = [[0 for i in range(width)] for j in range(height)]

    def select(self, x: int, y: int) -> None:
        """
        turn to self.stage[y][x] == 1
        """
        self.stage[y][x] = 1

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
        vertex = convex_hull_vertex(vertex)
        edge_point = convex_hull_edge(vertex)
        inner_point = convex_hull_inner(edge_point)
        for i, j in inner_point:
            self.select(i, j)

    def __str__(self):
        return "\n".join(map(str, self.stage))

    def get(self):
        return self.stage


if __name__ == "__main__":
    import seaborn as sns
    import matplotlib.pyplot as plt

    pivot = (100, 100)
    radius = 30
    branch = 12

    # スター型のステージを作成するデモ
    stage1 = Stage(200, 200)
    stage1.draw_circle(pivot[0], pivot[1], radius)
    for b in range(branch):
        stage1.draw_rect(pivot[0], pivot[1], radius, 10, 60, 360 / branch * b)

    plt.figure()
    sns.heatmap(stage1.get())
    plt.show()
