import os
import time

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from wu_physarum.model import WuPhysarum
from wu_physarum.lib.setting import MODEL_PARAM


MAX_ITER = 20000  # 最大試行回数
INTERVAL = 200    # 画像を保存する間隔（ステップ）
FOLDER_NAME = "output_fig/twelve_ring/seed_13647"  # 画像を保存するディレクトリ名

m = WuPhysarum(
    datapoint_filename="twelve_ring.json",
    seed=13647
)

# 画像保存用のディレクトリを作成
os.makedirs(FOLDER_NAME, exist_ok=True)

# 処理時間計測用に、プログラム開始時刻を記録する
start = time.time()
for step in range(MAX_ITER + 1):
    # エージェントの配置を画像として保存する
    if step % INTERVAL == 0:
        arr = np.array([[m.grid.grid[i][j] is None for j in range(MODEL_PARAM["height"])] for i in range(MODEL_PARAM["width"])])
        arr = np.maximum(arr, m.datapoint_region * 2)
        plt.clf()
        sns.heatmap(
            arr.T,
            cbar=False,
            square=True,
            cmap="viridis",
        ).invert_yaxis()
        plt.savefig("{}/step_{}.png".format(FOLDER_NAME, step))

    # i Step までに要した処理時間を表示する
    t = time.time() - start
    print("\r{}/{} step ({:.2f} sec)".format(step, MAX_ITER, t), end="")

    # シミュレーションのステップを進める
    m.step()
