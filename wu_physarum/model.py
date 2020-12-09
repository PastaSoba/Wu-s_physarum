import sys
from itertools import product

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
import numpy as np
from scipy import signal

from .agent import Physarum
from .lib.jsondeal import jsonreader
from .lib.convex_stage import coords2ndarray
from .lib.setting import MODEL_PARAM, LATTICECELL_PARAM
from .lib.star_stage import StarStage


def all_zero_stage():
    return np.zeros((MODEL_PARAM["width"], MODEL_PARAM["height"]))


def all_one_stage():
    return np.ones((MODEL_PARAM["width"], MODEL_PARAM["height"]))


class WuPhysarum(Model):
    """
    モジホコリエージェントによるTSPソルバのモデル
    """
    def __init__(
        self,
        datapoint_filename,
        seed,
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
        self.__datapoint_pos = jsonreader(datapoint_filename)

        # create masked stage
        # self.star_stage = StarStage(MODEL_PARAM["width"], MODEL_PARAM["height"])
        # pivot = (100, 100)
        # radius = 30
        # branch = 12
        # self.star_stage.draw_circle(pivot[0], pivot[1], radius)
        # for b in range(branch):
        #     self.star_stage.draw_rect(pivot[0], pivot[1], radius, 10, 60, 360 / branch * b)
        # self.stage_region = np.array(self.star_stage.stage_region)

        # create stage including Lattice Cells function
        self.create_physarum_region   = all_one_stage()                                             # モジホコリが生成されうる区域
        self.stage_region             = all_one_stage()                                             # ステージの区域
        self.__chenu_adding_region    = self.__create_chenu_adding_region(self.__datapoint_pos)     # chenuが追加される区域（データポイント周辺）
        self.__chenu_adding_intensity = self.__create_chenu_adding_intensity(self.__datapoint_pos)  # 追加されるchenuの強度マップ
        self.chenu_map                = all_zero_stage()                                            # chenuの強度マップ
        self.trail_map                = all_zero_stage()                                            # trailの強度マップ

        # create physarum agents
        self.torus = False
        self.grid = SingleGrid(
            width=MODEL_PARAM["width"],
            height=MODEL_PARAM["height"],
            torus=self.torus,
        )
        self.schedule = RandomActivation(self)
        for x, _row in enumerate(self.create_physarum_region):
            for y, create_region in enumerate(_row):
                if create_region and self.random.random() < MODEL_PARAM["density"]:
                    phy = Physarum(
                        pos=(x, y),
                        model=self,
                    )
                    self.grid.place_agent(phy, (x, y))
                    self.schedule.add(phy)

        # create adjacent cell map for adjusting the magnification
        boundary = "wrap" if self.torus else "fill"
        cnf_w, cnf_h, trf_w, trf_h = (
            LATTICECELL_PARAM["filterN_width"],
            LATTICECELL_PARAM["filterN_height"],
            LATTICECELL_PARAM["filterT_width"],
            LATTICECELL_PARAM["filterT_height"],
        )

        adjacent_stage_region_cell_num_on_chenu_map = \
            signal.convolve2d(
                self.stage_region, np.ones((cnf_w, cnf_h)), mode="same", boundary=boundary
            )
        self.fixed_adjacent_stage_region_cell_num_on_chenu_map = \
            np.maximum(
                adjacent_stage_region_cell_num_on_chenu_map,
                np.ones((MODEL_PARAM["width"], MODEL_PARAM["height"]))
            )
        adjacent_stage_region_cell_num_on_trail_map = \
            signal.convolve2d(
                self.stage_region, np.ones((trf_w, trf_h)), mode="same", boundary=boundary
            )
        self.fixed_adjacent_stage_region_cell_num_on_trail_map = \
            np.maximum(
                adjacent_stage_region_cell_num_on_trail_map,
                np.ones((MODEL_PARAM["width"], MODEL_PARAM["height"]))
            )

        # start simulation
        print("初期配置エージェント数: {}".format(len(self.schedule.agents)))
        self.running = True

    def __create_chenu_adding_region(self, pos):
        """
        ステップごとにchenuが追加される区域を作成する。
        返り値は追加される座標を1、そうでない座標を0とする2次元配列とする。
        """
        datapoint_pos = []
        for p in pos:
            for i, j in product(range(-1, 2), range(-1, 2)):
                _p = (p[0] + i, p[1] + j)
                if 0 <= _p[0] < MODEL_PARAM["width"] and 0 <= _p[1] < MODEL_PARAM["height"]:
                    datapoint_pos.append(_p)
        datapoint_region = coords2ndarray(tuple(datapoint_pos))
        return datapoint_region

    def __create_chenu_adding_intensity(self, pos):
        """
        ステップごとにどの座標にいくらの強度のchenuが追加されるかのマップを作成する。
        (__create_chenu_adding_regionとは違い、出力されるマップには0, 1以外の値も含む)
        """
        chenu_map = np.zeros((MODEL_PARAM["width"], MODEL_PARAM["height"]))
        is_intensity_settled = len(pos[0]) == 3

        for p in pos:
            if len(p) != 2 + is_intensity_settled:
                print("エラー：座標によってintensityの設定が異なります")
                sys.exit()
            for i, j in product(range(-1, 2), range(-1, 2)):
                _p = (p[0] + i, p[1] + j)
                if 0 <= _p[0] < MODEL_PARAM["width"] and 0 <= _p[1] < MODEL_PARAM["height"]:
                    chenu_map[_p[0]][_p[1]] = p[2] if is_intensity_settled else LATTICECELL_PARAM["CN"]
        return chenu_map

    def __update_map(self, chenu_map, trail_map):
        """
        chenu_map, trail_mapの更新を行う
        """
        boundary = "wrap" if self.torus else "fill"

        """
        Applying average filter
        """
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

        chenu_map = signal.convolve2d(chenu_map, cnf, mode="same", boundary=boundary)
        trail_map = signal.convolve2d(trail_map, trf, mode="same", boundary=boundary)

        """
        Adjust the magnification on trail_map, chenu_map for star_stage
        (trail/chenu_map) .* (周辺セル数) ./ (周辺ステージセル数) .* (self.stage_region)
        """
        chenu_map = chenu_map * (cnf_w * cnf_h)\
            / self.fixed_adjacent_stage_region_cell_num_on_chenu_map
        trail_map = trail_map * (trf_w * trf_h)\
            / self.fixed_adjacent_stage_region_cell_num_on_trail_map

        """
        Exclude overhang trail and chenu
        """
        chenu_map *= self.stage_region
        trail_map *= self.stage_region

        """
        Add chenu on datapoint
        """
        # Exclude filter effect in datapoint region
        chenu_map *= (1 - self.__chenu_adding_region)
        # Add chenu on datapoint
        chenu_map += self.__chenu_adding_intensity

        return [chenu_map, trail_map]

    @property
    def datapoint_region(self):
        return self.__chenu_adding_region

    def step(self):
        # モジホコリエージェントのステップ処理
        self.schedule.step()

        # 格子セルのステップ処理
        self.chenu_map, self.trail_map = self.__update_map(self.chenu_map, self.trail_map)
