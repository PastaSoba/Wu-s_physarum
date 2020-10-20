from mesa import Agent

from .lib.setting import PHYSARUM_PARAM


NINF = -1000000000

_SENSOR_OFFSET = PHYSARUM_PARAM["sensor_arm_length"] // 2
OFFSET = {
    # [offset of x, offset of y]

    # NORTH
    0: {"LSENSOR": [-_SENSOR_OFFSET, -_SENSOR_OFFSET],
        "RSENSOR": [_SENSOR_OFFSET, -_SENSOR_OFFSET],
        "FORWARD": [0, -1]},
    # NORTH_EAST
    1: {"LSENSOR": [0, -_SENSOR_OFFSET],
        "RSENSOR": [_SENSOR_OFFSET, 0],
        "FORWARD": [1, -1]},
    # EAST
    2: {"LSENSOR": [_SENSOR_OFFSET, -_SENSOR_OFFSET],
        "RSENSOR": [_SENSOR_OFFSET, _SENSOR_OFFSET],
        "FORWARD": [1, 0]},
    # SOUTH_EAST
    3: {"LSENSOR": [_SENSOR_OFFSET, 0],
        "RSENSOR": [0, _SENSOR_OFFSET],
        "FORWARD": [1, 1]},
    # SOUTH
    4: {"LSENSOR": [_SENSOR_OFFSET, _SENSOR_OFFSET],
        "RSENSOR": [-_SENSOR_OFFSET, _SENSOR_OFFSET],
        "FORWARD": [0, 1]},
    # SOUTH_WEST
    5: {"LSENSOR": [0, _SENSOR_OFFSET],
        "RSENSOR": [-_SENSOR_OFFSET, 0],
        "FORWARD": [-1, 1]},
    # WEST
    6: {"LSENSOR": [-_SENSOR_OFFSET, _SENSOR_OFFSET],
        "RSENSOR": [-_SENSOR_OFFSET, -_SENSOR_OFFSET],
        "FORWARD": [-1, 0]},
    # NORTH_WEST
    7: {"LSENSOR": [-_SENSOR_OFFSET, 0],
        "RSENSOR": [0, -_SENSOR_OFFSET],
        "FORWARD": [-1, -1]},
}


class Physarum(Agent):
    """
    モジホコリエージェント
    """
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.dir_id = self.model.random.randint(0, 7)
        self.motion_counter = 0

        self._is_successfully_moved = False

    def move_forward(self):
        forward_pos = (
            self.pos[0] + OFFSET[self.dir_id]["FORWARD"][0],
            self.pos[1] + OFFSET[self.dir_id]["FORWARD"][1]
        )
        if self.model.phy_grid.is_cell_empty(self, forward_pos) and self.model.stage_region[forward_pos]:
            # If agent CAN move forward successfully,
            # 1. deposit trail on now position
            self.model.trail_map[self.pos] += PHYSARUM_PARAM["depT"]
            # 2. agent moves forward
            self.model.phy_grid.move_agent(self, forward_pos)
            self._is_successfully_moved = True
        else:
            # If agent CANNOT move forward successfully,
            # subtract 1 from self motion counter.
            self.motion_counter -= 1
            self._is_successfully_moved = False

    def _get_is_successfully_moved(self):
        return self._is_successfully_moved

    def _get_weighted_value(self, sensor):
        sensing_pos = (
            self.pos[0] + OFFSET[self.dir_id][sensor][0],
            self.pos[1] + OFFSET[self.dir_id][sensor][1]
        )
        if self.model.phy_grid.out_of_bounds(sensing_pos) or self.model.stage_region[sensing_pos] is False:
            return NINF
        else:
            sensing_cell_trail = self.model.trail_map[sensing_pos]
            sensing_cell_chenu = self.model.chenu_map[sensing_pos]

            weighted_value = sensing_cell_trail * PHYSARUM_PARAM["WT"]
            + sensing_cell_chenu * PHYSARUM_PARAM["WN"]
            return weighted_value

    def _get_new_dir_id(self, Lweighted_value, Rweighted_value, is_successfully_moved):
        if is_successfully_moved is False:
            return self.model.random.randint(0, 7)  # ランダムな方向を向く
        elif Lweighted_value is NINF and Rweighted_value is NINF:
            return (self.dir_id + 4) % 8            # 真後ろを向く
        elif Lweighted_value < Rweighted_value:
            return (self.dir_id + 1) % 8            # 右に曲がる
        elif Lweighted_value > Rweighted_value:
            return (self.dir_id - 1) % 8            # 左に曲がる

    def step(self):
        """ Sensing Step """
        Lweighted_value = self._get_weighted_value("LSENSOR")
        Rweighted_value = self._get_weighted_value("RSENSOR")

        """ Moving Step """
        self.move_forward()
        is_successfully_moved = self._get_is_successfully_moved()

        """ Turning Step """
        new_dir_id = self._get_new_dir_id(Lweighted_value, Rweighted_value, is_successfully_moved)
        self.dir_id = new_dir_id

        """ Reproduct/Elimination Step"""
        # Reproduct
        if self.motion_counter > PHYSARUM_PARAM["RT"]:
            reproduction_pos = (
                self.pos[0] - OFFSET[self.dir_id]["FORWARD"][0],
                self.pos[1] - OFFSET[self.dir_id]["FORWARD"][1]
            )
            self.model.create_new_phy(reproduction_pos)
        # Elimination
        if self.motion_counter < PHYSARUM_PARAM["ET"]:
            self.model.phy_grid.remove_agent(self)
