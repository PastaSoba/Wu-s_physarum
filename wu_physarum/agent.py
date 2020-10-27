from mesa import Agent

from .lib.setting import PHYSARUM_PARAM


NINF = -1000000000

__SENSOR_OFFSET = PHYSARUM_PARAM["sensor_arm_length"] // 2
OFFSET = {
    # [offset of x, offset of y]

    # NORTH
    0: {"LSENSOR": [-__SENSOR_OFFSET, -__SENSOR_OFFSET],
        "RSENSOR": [__SENSOR_OFFSET, -__SENSOR_OFFSET],
        "FORWARD": [0, -1]},
    # NORTH_EAST
    1: {"LSENSOR": [0, -__SENSOR_OFFSET],
        "RSENSOR": [__SENSOR_OFFSET, 0],
        "FORWARD": [1, -1]},
    # EAST
    2: {"LSENSOR": [__SENSOR_OFFSET, -__SENSOR_OFFSET],
        "RSENSOR": [__SENSOR_OFFSET, __SENSOR_OFFSET],
        "FORWARD": [1, 0]},
    # SOUTH_EAST
    3: {"LSENSOR": [__SENSOR_OFFSET, 0],
        "RSENSOR": [0, __SENSOR_OFFSET],
        "FORWARD": [1, 1]},
    # SOUTH
    4: {"LSENSOR": [__SENSOR_OFFSET, __SENSOR_OFFSET],
        "RSENSOR": [-__SENSOR_OFFSET, __SENSOR_OFFSET],
        "FORWARD": [0, 1]},
    # SOUTH_WEST
    5: {"LSENSOR": [0, __SENSOR_OFFSET],
        "RSENSOR": [-__SENSOR_OFFSET, 0],
        "FORWARD": [-1, 1]},
    # WEST
    6: {"LSENSOR": [-__SENSOR_OFFSET, __SENSOR_OFFSET],
        "RSENSOR": [-__SENSOR_OFFSET, -__SENSOR_OFFSET],
        "FORWARD": [-1, 0]},
    # NORTH_WEST
    7: {"LSENSOR": [-__SENSOR_OFFSET, 0],
        "RSENSOR": [0, -__SENSOR_OFFSET],
        "FORWARD": [-1, -1]},
}


class Physarum(Agent):
    """
    モジホコリエージェント
    """
    unique_id = 1

    def __init__(self, pos, model):
        super().__init__(Physarum.unique_id, model)
        Physarum.unique_id += 1
        self.pos = pos
        self.dir_id = self.random.randint(0, 7)
        self.motion_counter = 0

        self.__is_successfully_moved = False

    def __get_weighted_value(self, sensor):
        sensing_pos = (
            self.pos[0] + OFFSET[self.dir_id][sensor][0],
            self.pos[1] + OFFSET[self.dir_id][sensor][1]
        )
        if self.model.grid.out_of_bounds(sensing_pos) or self.model.stage_region[sensing_pos] is False:
            return NINF
        else:
            sensing_cell_trail = self.model.trail_map[sensing_pos]
            sensing_cell_chenu = self.model.chenu_map[sensing_pos]

            weighted_value = sensing_cell_trail * PHYSARUM_PARAM["WT"]
            + sensing_cell_chenu * PHYSARUM_PARAM["WN"]
            return weighted_value

    def __move_forward(self):
        forward_pos = (
            self.pos[0] + OFFSET[self.dir_id]["FORWARD"][0],
            self.pos[1] + OFFSET[self.dir_id]["FORWARD"][1]
        )
        if not self.model.grid.out_of_bounds(forward_pos) and self.model.grid.is_cell_empty(forward_pos) and self.model.stage_region[forward_pos]:
            # If agent CAN move forward successfully,
            # 1. deposit trail on now position
            self.model.trail_map[self.pos] += PHYSARUM_PARAM["depT"]
            # 2. agent moves forward
            self.model.grid.move_agent(self, forward_pos)
            # add 1 to self motion counter.
            self.motion_counter += 1
            self.__is_successfully_moved = True
        else:
            # If agent CANNOT move forward successfully,
            # subtract 1 from self motion counter.
            self.motion_counter -= 1
            self.__is_successfully_moved = False

    @property
    def is_successfully_moved(self):
        return self.__is_successfully_moved

    def __get_new_dir_id(self, Lweighted_value, Rweighted_value, is_successfully_moved):
        if is_successfully_moved is False:
            return self.random.randint(0, 7)        # ランダムな方向を向く
        elif Lweighted_value is NINF and Rweighted_value is NINF:
            return (self.dir_id + 4) % 8            # 真後ろを向く
        elif Lweighted_value < Rweighted_value:
            return (self.dir_id + 1) % 8            # 右に曲がる
        elif Lweighted_value > Rweighted_value:
            return (self.dir_id - 1) % 8            # 左に曲がる
        else:
            # if Lweighted_value == Rweighted_value
            return self.dir_id                      # 直進する

    def step(self):
        # Memory self position for reproduction step before move or rotate
        __reproduction_pos = self.pos

        """ Sensing Step """
        Lweighted_value = self.__get_weighted_value("LSENSOR")
        Rweighted_value = self.__get_weighted_value("RSENSOR")

        """ Moving Step """
        self.__move_forward()
        is_successfully_moved = self.is_successfully_moved

        """ Turning Step """
        new_dir_id = self.__get_new_dir_id(Lweighted_value, Rweighted_value, is_successfully_moved)
        self.dir_id = new_dir_id

        """ Reproduct/Elimination Step"""
        # Reproduct
        if self.motion_counter > PHYSARUM_PARAM["RT"] and is_successfully_moved:
            chrone = Physarum(pos=__reproduction_pos, model=self.model)
            self.model.grid.place_agent(chrone, __reproduction_pos)
            self.model.schedule.add(chrone)
        # Elimination
        if self.motion_counter < PHYSARUM_PARAM["ET"]:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
