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
    model.py内の二次元配列形式を、numpy.ndarray形式に変換する

    入力：((0, 0), (1, 1)) ※1に指定されている座標が(0, 0)と(1, 1)だと解釈
    出力：[[1 0]
           [0 1]]
    """
    array = [[(i, j) in coords for j in range(MODEL_PARAM["height"])] for i in range(MODEL_PARAM["width"])]
    return np.array(array)


def visualize(coords):
    """
    model.py内の二次元配列形式を、seabornで表示する

    入力：((0, 0), (1, 1)) ※1に指定されている座標に色が付けられる
    出力：seaborn画像
    """
    arr = _coords2ndarray(coords)
    ax = sns.heatmap(arr)
    ax.invert_yaxis()
    plt.show()


if __name__ == "__main__":
    from wu_physarum.model import WuPhysarum

    jsonfile = "test.json"
    wu_physarum = WuPhysarum(filename=jsonfile, seed=0)
    visualize(wu_physarum.stage_region)
    visualize(wu_physarum.datapoint_region)
