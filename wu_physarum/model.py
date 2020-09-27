from itertools import product

from mesa import Model
from mesa.time import RandomActivation, SimultaneousActivation
from mesa.space import SingleGrid

from .agent import LatticeCell, Physarum
from .lib.jsondeal import jsonreader
from .lib.convex import convex_hull_inner
from .lib.setting import MODEL_PARAM


class WuPhysarum(Model):
    """
    モジホコリエージェントによるTSPソルバのモデル
    """
    def __init__(
        self,
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
        # create stage
        datapoint = jsonreader(MODEL_PARAM["filename"])
        stage_region = convex_hull_inner(datapoint)

        # create physarum agents
        self.phy_grid = SingleGrid(
            width=MODEL_PARAM["width"],
            height=MODEL_PARAM["height"],
            torus=False)
        self.phy_schedule = RandomActivation(self)
        for (_x, _y) in stage_region:
            if self.random.random() < MODEL_PARAM["density"]:
                phy = Physarum(
                    pos=(_x, _y),
                    model=self,)
                self.phy_grid.place_agent(phy, (_x, _y))
                self.phy_schedule.add(phy)

        # create lattice cell agents
        self.ltc_grid = SingleGrid(
            width=MODEL_PARAM["width"],
            height=MODEL_PARAM["height"],
            torus=False)
        self.ltc_schedule = SimultaneousActivation(self)
        for _x, _y in product(
            range(MODEL_PARAM["width"]),
            range(MODEL_PARAM["height"])
        ):
            ltc = LatticeCell(
                pos=(_x, _y),
                in_stage=(_x, _y) in stage_region,
                is_datapoint=(_x, _y) in datapoint,
                model=self,)
            self.ltc_grid.place_agent(ltc, (_x, _y))
            self.ltc_schedule.add(ltc)

        # start simulation
        self.running = True

    def step(self):
        self.phy_schedule.step()
        self.ltc_schedule.step()
