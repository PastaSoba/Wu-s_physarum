import os
import time

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from wu_physarum.model import WuPhysarum
from wu_physarum.lib.setting import MODEL_PARAM


m = WuPhysarum(
    datapoint_filename="demo.json",
    seed=13647
)
max_iter = 10000  # 最大試行回数
interval = 100    # 画像を保存する間隔（ステップ）
folder_name = "output_fig/seed_13647"


os.makedirs(folder_name, exist_ok=True)
start = time.time()
for i in range(max_iter + 1):
    if i % interval == 0:
        arr = np.array([[m.grid.grid[i][j] is None for j in range(MODEL_PARAM["height"])] for i in range(MODEL_PARAM["width"])])

        plt.clf()
        sns.heatmap(
            arr,
            cbar=False,
            square=True,
        ).invert_yaxis()
        plt.savefig("{}/step_{}.png".format(folder_name, i))
    t = time.time() - start
    print("\r{}/{} step ({:.2f} sec)".format(i, max_iter, t), end="")
    m.step()
