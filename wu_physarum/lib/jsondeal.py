import os
from pathlib import Path
import json


def jsonreader(datapoint_filename):
    """
    jsonファイルから座標の組を読み込む
    usuage:
        jsonreader("demo.json")
        -> ((100, 100), (200, 200), (300, 300))
    """
    path = Path(__file__).parent.parent
    path /= 'resource/'

    try:
        with open(os.path.join(path, datapoint_filename)) as f:
            datas = json.load(f)
            coords = []
            if len(datas[1]) == 2:
                # intensityがセットされていないとき
                for data in datas:
                    coords.append((data["x"], data["y"]))
            elif len(datas[1]) == 3:
                # intensityがセットされているとき
                for data in datas:
                    coords.append((data["x"], data["y"], data["intensity"]))

            return tuple(coords)
    except Exception as e:
        print("### Error occured while reading json file ###")
        print(e)
