from itertools import product

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
import numpy as np
from scipy import signal

from .agent import Physarum
from .lib.jsondeal import jsonreader
from .lib.convex import coords2ndarray
from .lib.setting import MODEL_PARAM, LATTICECELL_PARAM
from .lib.star_stage import StarStage


class WuPhysarum(Model):
    """
    モジホコリエージェントによるTSPソルバのモデル
    """
    def __init__(
        self,
        datapoint_filename,
        seed=MODEL_PARAM["seed"],
    ):
        """
        新しいTSPソルバを作る

        Args:
            height, width: 空間のサイズ(pixel)
            density: モジホコリエージェントの発生密度(0~1.0)
            datapoint_filename: データポイントを表したファイル
            seed: 乱数のシード値
        """
        # read datapoint position
        self._datapoint_pos = jsonreader(datapoint_filename)

        # create masked stage
        self.star_stage = StarStage(MODEL_PARAM["width"], MODEL_PARAM["height"])
        pivot = (100, 100)
        radius = 30
        branch = 12
        self.star_stage.draw_circle(pivot[0], pivot[1], radius)
        for b in range(branch):
            self.star_stage.draw_rect(pivot[0], pivot[1], radius, 10, 60, 360 / branch * b)

        # create stage including Lattice Cells function
        self.stage_region = coords2ndarray(self.star_stage.stage_region)
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
            for y, stage_region in enumerate(_row):
                if stage_region and self.random.random() < MODEL_PARAM["density"]:
                    phy = Physarum(
                        pos=(x, y),
                        model=self,
                    )
                    self.grid.place_agent(phy, (x, y))
                    self.schedule.add(phy)

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

    def __update_map(self, chenu_map, trail_map):
        # chenu_map, trail_mapの更新を行う

        # create filter
        cnf_w, cnf_h, dampN = (
            LATTICECELL_PARAM["filterN_width"],
            LATTICECELL_PARAM["filterN_height"],
            LATTICECELL_PARAM["dampN"])
        cnf = np.full((cnf_w, cnf_h), (1 - dampN) / (cnf_w * cnf_h))

        trf_w, trf_h, dampT = (
            LATTICECELL_PARAM["filterT_width"],
            LATTICECELL_PARAM["filterT_height"],
            LATTICECELL_PARAM["dampT"])
        trf = np.full((trf_w, trf_h), (1 - dampT) / (trf_w * trf_h))

        # TODO: chenu, trailともにstage_region内のみでフィルターを
        # かけたい
        # Applying average filter on trail_map
        trail_map = signal.convolve2d(trail_map, trf, mode="same")
        # Applying average filter on whole chenu_map
        chenu_map = signal.convolve2d(chenu_map, cnf, mode="same")
        # Exclude filter effect in datapoint region
        chenu_map *= 1 - self.datapoint_region
        # Add chenu (timed by steps) on datapoint
        chenu_map += LATTICECELL_PARAM["CN"] * self.datapoint_region * self.schedule.steps

        return [chenu_map, trail_map]

    def step(self):
        # モジホコリエージェントのステップ処理
        self.schedule.step()

        # 格子セルのステップ処理
        self.chenu_map, self.trail_map = self.__update_map(self.chenu_map, self.trail_map)
