from wu_physarum.model import WuPhysarum
from wu_physarum.lib.record import ModelRecorder

for seed in [2018, 1133, 5201, 8113, 3520, 1811, 335]:
    experiment_name = "knapsack6"

    recorder = ModelRecorder(
        model=WuPhysarum,
        datapoint_filename="knapsack6_R5_center8.json",
        seed=seed,                                            # モデルに与えるseed値
        figure_foldername="experiment/{}/figure/seed_{}".format(experiment_name, seed),  # 画像を保存するディレクトリ名
        meta_foldername="experiment/{}/meta".format(experiment_name),           # データを保存するディレクトリ名
        max_iteration=10000,                                   # 最大試行回数
        record_interval=100,                                   # 画像を保存する間隔（ステップ）
    )

    recorder.start()
