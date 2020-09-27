import json


def jsonreader(filename):
    """
    jsonファイルから座標の組を読み込む
    usuage:
        jsonreader("resource/test.json")
        -> ((100, 100), (200, 200), (300, 300))
    """
    try:
        with open(filename) as f:
            datas = json.load(f)

            coords = []
            for data in datas:
                coords.append((data["x"], data["y"]))

            return tuple(coords)
    except Exception as e:
        print("### Error occured while reading json file ###")
        print(e)
