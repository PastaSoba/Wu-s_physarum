import os
import time

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from wu_physarum.lib.setting import MODEL_PARAM


class ModelRecorder:
    def __init__(
            self,
            model,
            datapoint_filename,
            seed,
            figure_folername,
            max_iteration,
            record_interval,
    ):
        self.model = model(
            datapoint_filename=datapoint_filename,
            seed=seed,
        )
        self.dir_name = figure_folername
        self.max_iter = max_iteration
        self.interval = record_interval
        self.start_time = None

    def __startTimer(self):
        self.start_time = time.time()

    def __makeFigDir(self):
        os.makedirs(self.dir_name, exist_ok=True)

    def start(self):
        self.__makeFigDir()
        self.__startTimer()

        for step in range(self.max_iter+1):
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
                plt.clf()
                sns.heatmap(
                    arr.T,
                    cbar=True,
                    square=True,
                    cmap="viridis",
                ).invert_yaxis()
                plt.savefig("{}/step_{}.png".format(self.dir_name, self.model.schedule.steps))

            t = time.time() - self.start_time
            print("\r{}/{} step ({:.2f} sec)".format(step, self.max_iter, t), end="")

            self.model.step()
