import os
from pathlib import Path
import json


def jsonreader(filename):
    """
    jsonファイルから座標の組を読み込む
    usuage:
        jsonreader("test.json")
        -> ((100, 100), (200, 200), (300, 300))
    """
    path = Path(__file__).parent.parent
    path /= 'resource/'

    try:
        with open(os.path.join(path, filename)) as f:
            datas = json.load(f)

            coords = []
            for data in datas:
                coords.append((data["x"], data["y"]))

            return tuple(coords)
    except Exception as e:
        print("### Error occured while reading json file ###")
        print(e)
