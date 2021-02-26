"""
数理アルゴリズムを用いて01ナップザック問題の厳密解を探す

目的：エージェント数と制限の関係を調べるため
"""

from ortoolpy import knapsack

# 重さ
w = [10, 12, 7, 9, 21, 16]

# 価値
v = [120, 130, 80, 100, 250, 185]

# 制約：74kg
W = 60


result = None
for i in range(76):
    tmp = knapsack(w, v, i)
    if result != tmp:
        result = tmp
        print('容量:{}    最大価値:{} / 組み合わせ:{}'.format(i, result[0], result))
