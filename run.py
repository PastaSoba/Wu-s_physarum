from wu_physarum.model import WuPhysarum
from wu_physarum.lib.record import ModelRecorder


recorder = ModelRecorder(
    model=WuPhysarum,
    datapoint_filename="twelve_ring.json",
    seed=13647,                                            # モデルに与えるseed値
    figure_folername="output_fig/twelve_ring/seed_13647",  # 画像を保存するディレクトリ名
    max_iteration=20000,                                   # 最大試行回数
    record_interval=200,                                   # 画像を保存する間隔（ステップ）
)

recorder.start()
