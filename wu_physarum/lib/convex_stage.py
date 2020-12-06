import numpy as np

from .setting import MODEL_PARAM


def __convex_hull_vertex(points):
    """jsonファイルにある2次元座標群で構成できる凸包の頂点群を計算する
    Input: 頂点座標のタプル ((x_1, y_1), (x_2, y_2), ...)
    Output: x座標が最小の頂点から反時計回りにめぐった凸包の頂点
    Implements Andrew's monotone chain algorithm. O(n log n) complexity.
    """
    # https://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/__convex_hull/Monotone_chain#Python
    # より引用

    # Sort the points lexicographically (tuples are compared lexicographically).
    # Remove duplicates to detect the case we have just one unique point.
    points = sorted(set(points))

    # Boring case: no points or a single point, possibly repeated multiple times.
    if len(points) <= 1:
        return points

    # 2D cross product of OA and OB vectors, i.e. z-component of their 3D cross product.
    # Returns a positive value, if OAB makes a counter-clockwise turn,
    # negative for clockwise turn, and zero if the points are collinear.
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Concatenation of the lower and upper hulls gives the convex hull.
    # Last point of each list is omitted because it is repeated at the beginning of the other list.
    return tuple(lower[:-1] + upper[:-1])


def __point_on_edge(p1, p2):
    """
    2点間をつなぐ線分上にある格子点を返す。
    Input: 2点の座標のタプル
            ((x_1, y_1), (x_2, y_2))
    Output: 格子点の座標のリスト
            [(x_1, y_1), (x_2, y_2), ...]
    """
    (x_1, y_1), (x_2, y_2) = p1, p2

    if x_1 > x_2:
        (x_1, y_1), (x_2, y_2) = (x_2, y_2), (x_1, y_1)

    points = []

    # 傾きがy軸と平行になる場合
    if x_1 == x_2:
        for _y in range(y_1, y_2 + 1):
            points.append((x_1, _y))
        return points

    # 傾きが求められるとき
    tilt = (y_2 - y_1) / (x_2 - x_1)
    for _x in range(x_1, x_2 + 1):
        _y = y_1 + tilt * (_x - x_1)
        points.append((_x, int(round(_y, 0))))
    return points


def __convex_hull_edge(points):
    """
    凸包の辺上にある格子点を返す。
    Input: 凸包の頂点座標群（反時計回りにならべてあること）
    Output: 凸包の辺上にある格子点群
    """
    edge_point = []
    for i in range(len(points)):
        edge_point.extend(__point_on_edge(points[i], points[i - 1]))
    return tuple(sorted(set(edge_point)))


def __convex_hull_inner(points):
    """
    凸包の内部（辺上も含む）にある格子点を返す。
    Input: 凸包の辺上にある格子点群
    Output: 凸包の内部にある格子点群
    """
    inner_point = []
    points = sorted(points)

    min_x, max_x = points[0][0], points[-1][0]
    for _x in range(min_x, max_x + 1):
        point_on_same_x = filter((lambda coord: coord[0] == _x), points)
        y_coord_on_same_x = list(
            map((lambda coord: coord[1]), point_on_same_x))

        min_y, max_y = min(y_coord_on_same_x), max(y_coord_on_same_x)
        for _y in range(min_y, max_y + 1):
            inner_point.append((_x, _y))

    return tuple(inner_point)


def convex_hull_inner(points):
    """jsonファイルにある2次元座標群で構成できる凸包の頂点群を計算する
    Input: 頂点座標のタプル ((x_1, y_1), (x_2, y_2), ...)
    Output: 凸包の内部（辺上も含む）にある格子点群
    Implements Andrew's monotone chain algorithm. O(n log n) complexity.
    """
    return __convex_hull_inner(__convex_hull_edge(__convex_hull_vertex(points)))


def coords2ndarray(coords):
    """
    プロットされる点の座標のみが入っている二次元配列を、
    プロットされる点の座標の要素が1となっている二次元配列に変換する

    入力：((0, 0), (1, 1)) ※1に指定されている座標が(0, 0)と(1, 1)だと解釈
    出力：np.array([[1, 0],
                    [0, 1]])
    """
    array = [[(i, j) in coords for j in range(MODEL_PARAM["height"])] for i in range(MODEL_PARAM["width"])]
    return np.array(array)
