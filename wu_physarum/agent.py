from mesa import Agent

from .lib.setting import MODEL_PARAM, PHYSARUM_PARAM, LATTICECELL_PARAM


NINF = 1000000000

_SENSOR_OFFSET = PHYSARUM_PARAM["sensor_arm_length"] // 2
OFFSET = {
    # TODO: 座標の取り方と正負の符号が合致しているか確かめる
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

    def _move_forward(self):
        forward_pos = (
            self.pos[0] + OFFSET[self.dir_id]["FORWARD"][0],
            self.pos[1] + OFFSET[self.dir_id]["FORWARD"][1]
        )
        if self.model.phy_grid.is_cell_empty(self, forward_pos):
            # If agent CAN move forward successfully,
            # 1. deposit trail on now position
            ltc = self.model.ltc_grid.get_cell_list_contents([self.pos])[0]
            ltc.trail += PHYSARUM_PARAM["depT"]
            # 2. agent moves forward
            self.model.phy_grid.move_agent(self, forward_pos)
            return True
        else:
            # If agent CANNOT move forward successfully,
            # subtract 1 from self motion counter.
            self.motion_counter -= 1
            return False

    def _get_weighted_value(self, sensor):
        sensing_pos = (
            self.pos[0] + OFFSET[self.dir_id][sensor][0],
            self.pos[1] + OFFSET[self.dir_id][sensor][1]
        )
        if self.model.phy_grid.out_of_bounds(sensing_pos):
            return NINF
        else:
            sensing_cell = self.model.ltc_grid.get_cell_list_contents(
                sensing_pos)[0]
            weighted_value = sensing_cell.trail * PHYSARUM_PARAM["WT"]
            + sensing_cell.chenu * PHYSARUM_PARAM["WN"]
            return weighted_value

    def _turn(self, Lweighted_value, Rweighted_value, successfully_moved):
        if successfully_moved is False:
            self.dir_id = self.model.random.randint(0, 7)
        elif Lweighted_value is NINF and Rweighted_value is NINF:
            self.dir_id = (self.dir_id + 4) % 8
        elif Lweighted_value < Rweighted_value:
            self.dir_id = (self.dir_id + 1) % 8
        elif Lweighted_value > Rweighted_value:
            self.dir_id = (self.dir_id - 1) % 8

    def step(self):
        """ Moving Step """
        successfully_moved = self._move_forward()

        """ Sensing Step """
        Lweighted_value = self._get_weighted_value("LSENSOR")
        Rweighted_value = self._get_weighted_value("RSENSOR")

        """ Turning Step """
        self._turn(Lweighted_value, Rweighted_value, successfully_moved)

        """ Reproduct/Elimination Step"""
        # Reproduct
        if self.motion_counter > PHYSARUM_PARAM["RT"]:
            reproduction_pos = (
                self.pos[0] - OFFSET[self.dir_id]["FORWARD"][0],
                self.pos[1] - OFFSET[self.dir_id]["FORWARD"][1])
            self.model.create_new_phy(reproduction_pos)
        # Elimination
        if self.motion_counter < PHYSARUM_PARAM["ET"]:
            self.model.phy_grid.remove_agent(self)


class LatticeCell(Agent):
    def __init__(self):
        super().__init__()

    def step(self):
        pass

    def advance(self):
        pass
