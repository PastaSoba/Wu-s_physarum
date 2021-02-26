"""
ModelRecorder

# 役割
ModelRecorderを通してモデルを実行することで、
一定の間隔（ステップ）ごとにシミュレーションの
出力を画像として保存することができる

# 使用例
recorder = ModelRecorder(
    model=WuPhysarum,
    datapoint_filename="twelve_ring.json",
    seed=13647,                                            # モデルに与えるseed値
    figure_foldername="output_fig/twelve_ring/seed_13647",  # 画像を保存するディレクトリ名
    max_iteration=20000,                                   # 最大試行回数
    record_interval=200,                                   # 画像を保存する間隔（ステップ）
)

recorder.start()

"""

import os
import time
import shutil
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from wu_physarum.lib.setting import MODEL_PARAM

path = Path(__file__).parent.parent


class ModelRecorder:
    def __init__(
            self,
            model,
            datapoint_filename,
            seed,
            figure_foldername,
            meta_foldername,
            max_iteration,
            record_interval,
    ):
        self.model = model(
            datapoint_filename=datapoint_filename,
            seed=seed,
        )
        self.datapoint_filename = datapoint_filename
        self.figdir_name = figure_foldername
        self.metadir_name = meta_foldername
        self.max_iter = max_iteration
        self.interval = record_interval
        self.start_time = None

    def __startTimer(self):
        self.start_time = time.time()

    def __makeFigDir(self):
        os.makedirs(self.figdir_name, exist_ok=True)

    def __makeMetaDir(self):
        os.makedirs(self.metadir_name, exist_ok=True)
        os.path.join(path, 'resource', self.datapoint_filename)
        shutil.copy(os.path.join(path, 'resource', self.datapoint_filename), self.metadir_name)  # データポイントファイルの保存
        shutil.copy(os.path.join(path, 'lib', 'setting.py'), self.metadir_name)
        shutil.copy(os.path.join(path, 'agent.py'), self.metadir_name)
        shutil.copy(os.path.join(path, 'model.py'), self.metadir_name)

    def start(self):
        self.__makeFigDir()
        self.__makeMetaDir()
        self.__startTimer()

        for step in range(self.max_iter + 1):
            if step % self.interval == 0:
                """
                arr配列の各値の割り当て

                datapoint       -> 2
                非datapoint     -> 1
                モジホコリセル  -> 0
                """
                arr = np.array(
                    [[self.model.grid.grid[i][j] is None for j in range(MODEL_PARAM["height"])] for i in
                     range(MODEL_PARAM["width"])]
                )
                arr = np.maximum(arr, self.model.datapoint_region * 2)

                fig, ((phys, _), (chenu, trail)) = plt.subplots(2, 2, sharex=True, sharey=True)
                sns.heatmap(
                    arr.T,
                    square=True,
                    cmap="viridis",
                    ax=phys
                ).invert_yaxis()
                sns.heatmap(
                    self.model.chenu_map.T,
                    cbar=True,
                    square=True,
                    cmap="viridis",
                    ax=chenu
                ).invert_yaxis()
                sns.heatmap(
                    self.model.trail_map.T,
                    cbar=True,
                    square=True,
                    cmap="viridis",
                    vmin=0,
                    vmax=12,
                    ax=trail
                ).invert_yaxis()
                phys.set_title("physarum & datapoint map")
                chenu.set_title("chemo nutrient map")
                trail.set_title("trail map")

                fig.savefig("{}/step_{}.png".format(self.figdir_name, self.model.schedule.steps))
                plt.clf()
                plt.close()

            t = time.time() - self.start_time
            print("\r{}/{} step ({:.2f} sec)".format(step, self.max_iter, t), end="")

            self.model.step()
        print("")
