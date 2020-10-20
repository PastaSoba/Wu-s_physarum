from itertools import product

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
import numpy as np
from scipy import signal

from .agent import Physarum
from .lib.jsondeal import jsonreader
from .lib.convex import convex_hull_inner, coords2ndarray
from .lib.setting import MODEL_PARAM, LATTICECELL_PARAM


class WuPhysarum(Model):
    """
    モジホコリエージェントによるTSPソルバのモデル
    """
    def __init__(
        self,
        filename,
        seed=MODEL_PARAM["seed"],
    ):
        """
        新しいTSPソルバを作る

        Args:
            height, width: 空間のサイズ(pixel)
            density: モジホコリエージェントの発生密度(0~1.0)
            filename: データポイントを表したファイル
            seed: 乱数のシード値
        """
        # read datapoint position
        self._datapoint_pos = jsonreader(filename)

        # create stage including Lattice Cells function
        # TODO: 将来的に、stage_regionは_datapoint_posとは独立して
        # 星形のstageとして作ることができるようにする。
        self.stage_region = coords2ndarray(convex_hull_inner(self._datapoint_pos))
        self.datapoint_region = coords2ndarray(self._create_datapoint_region(self._datapoint_pos))
        self.chenu_map = np.zeros((MODEL_PARAM["width"], MODEL_PARAM["height"]))
        self.trail_map = np.zeros((MODEL_PARAM["width"], MODEL_PARAM["height"]))

        # create physarum agents
        self.grid = SingleGrid(
            width=MODEL_PARAM["width"],
            height=MODEL_PARAM["height"],
            torus=False,
        )
        self.schedule = RandomActivation(self)
        for x, _row in enumerate(self.stage_region):
            for y, is_in_stage in enumerate(_row):
                if is_in_stage and self.random.random() < MODEL_PARAM["density"]:
                    phy = Physarum(
                        pos=(x, y),
                        model=self,
                    )
                    self.grid.place_agent(phy, (x, y))
                    self.schedule.add(phy)

        # create filter
        self.cnf_w, self.cnf_h, self.dampN = (
            LATTICECELL_PARAM["filterN_width"],
            LATTICECELL_PARAM["filterN_height"],
            LATTICECELL_PARAM["dampN"])
        self.cnf = np.fill((self.cnf_w, self.cnf_h), (1 - self.dampN) / (self.cnf_w * self.cnf_h))

        self.trf_w, self.trf_h, self.dampT = (
            LATTICECELL_PARAM["filterT_width"],
            LATTICECELL_PARAM["filterT_height"],
            LATTICECELL_PARAM["dampT"])
        self.trf = np.fill((self.trf_w, self.trf_h), (1 - self.dampT) / (self.trf_w * self.trf_h))

        # start simulation
        self.running = True

    def _create_datapoint_region(self, pos):
        datapoint_region = []
        for p in pos:
            for i, j in product(range(-1, 2), range(-1, 2)):
                _p = (p[0] + i, p[1] + j)
                if 0 <= _p[0] < MODEL_PARAM["width"] and 0 <= _p[1] < MODEL_PARAM["height"]:
                    datapoint_region.append(_p)
        return tuple(datapoint_region)

    def create_new_phy(self, pos):
        """
        posで指定された場所に新たにphysarumエージェントを作成する
        """
        phy = Physarum(
            pos=pos,
            model=self,
        )
        self.grid.place_agent(phy, pos)
        self.schedule.add(phy)

    def step(self):
        # モジホコリエージェントのステップ処理
        self.schedule.step()

        # 格子セルのステップ処理
        # Add chenu on datapoint
        self.chenu_map += LATTICECELL_PARAM["CN"] * self.datapoint_region
        # Applying average filter on chenu_map
        self.chenu_map = signal.convolve2d(self.chenu_map, self.cnf)
        # Applying average filter on trail_map
        self.trail_map = signal.convolve2d(self.trail_map, self.trf)
