"""
二次元配列可視化デバッグ用モジュール

二次元配列をseabornで可視化する
使い方: python visualize.py
"""

import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

from wu_physarum.lib.setting import MODEL_PARAM


def _coords2ndarray(coords):
    """
    model.py内の二次元配列形式
    (プロットされる点の座標のみが入っている二次元配列)を、
    numpy.ndarray形式に変換する

    入力：((0, 0), (1, 1)) ※1に指定されている座標が(0, 0)と(1, 1)だと解釈
    出力：[[1 0]
           [0 1]]
    """
    array = [[(i, j) in coords for j in range(MODEL_PARAM["height"])] for i in range(MODEL_PARAM["width"])]
    return np.array(array)


def visualize(coords, is_plotted_only_True_points):
    """
    二次元配列形式を、seabornで表示する

    入力：((0, 0), (1, 1)) ※1に指定されている座標に色が付けられる
    is_plotted_only_True_points
      -> True: プロットされる点の座標のみが入っている二次元配列
      -> False: 二次元配列内でプロットされる点の要素のみが1となっている二次元配列
    出力：seaborn画像
    """
    arr = _coords2ndarray(coords) if is_plotted_only_True_points else np.array(coords)
    plt.figure()
    ax = sns.heatmap(arr.T, cmap='gnuplot')
    ax.invert_yaxis()
    plt.xlabel("x")
    plt.ylabel("y")
    plt.show()


if __name__ == "__main__":
    from wu_physarum.model import WuPhysarum
    from wu_physarum.lib.star_stage import StarStage

    """ model.pyのstage_region, datapoint_regionの確認 """
    jsonfile = "demo.json"
    wu_physarum = WuPhysarum(datapoint_filename=jsonfile, seed=0)
    visualize(wu_physarum.stage_region, is_plotted_only_True_points=False)
    visualize(wu_physarum.datapoint_region, is_plotted_only_True_points=False)

    """ スター型のステージを作成するデモ """
    pivot = (100, 100)
    radius = 30
    branch = 12
    starstage = StarStage()
    starstage.draw_circle(pivot[0], pivot[1], radius)
    for b in range(branch):
        starstage.draw_rect(pivot[0], pivot[1], radius, 10, 60, 360 / branch * b)
    visualize(starstage.get(), is_plotted_only_True_points=False)
