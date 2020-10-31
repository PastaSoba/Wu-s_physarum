# 本プログラムについて
このプログラムは以下の論文で紹介されたマルチエージェントシステムを python製ライブラリ mesa を用いて構築したものです。

論文の内容を精査して構築していますが、論文の意に沿っていない動作をする可能性があります。
> Wu Y., Zhang Z., Deng Y., Zhou H., Qian T. (2012) An Enhanced Multi-Agent System with Evolution Mechanism to Approximate Physarum Transport Networks. In: Thielscher M., Zhang D. (eds) AI 2012: Advances in Artificial Intelligence. AI 2012. Lecture Notes in Computer Science, vol 7691. Springer, Berlin, Heidelberg. https://doi.org/10.1007/978-3-642-35101-3_3

## 動作方法
1.  python仮想環境の作成とライブラリのインストール

run.pyが存在するディレクトリで以下のコマンドを入力し、python仮想環境とライブラリをインストールしてください。
なお、python3.7以降を利用してください。
```
// python仮想環境の作成
python3 -m venv venv

// python仮想環境の有効化
venv/Scripts/activate (windows)
source venv/bin/activate (mac/linux)

// 必要なライブラリのインストール
pip install -r requirements.txt
```
2. 動作

run.pyが存在するディレクトリで以下のコマンドを入力することで、プログラムが起動します。
```
python run.py
```

## 動作のカスタマイズ
動作変更とカスタマイズ例は以下の通りです。

### データポイントの変更
1. wu_physarum/resource 内にデータポイントを記録したjsonファイルを作成する
2. wu_physarum/server.py の datapoint_filename を変更する

### ステージ作成条件の変更
wu_physarum/model.py のコンストラクタの self.stage_region, self.datapoint_region を変更することで、餌のないステージや星形のステージ等のステージ作成条件の変更が可能です。

ただし、いずれの変数も (MODEL_PARAM["width"], MODEL_PARAM["height"]) のサイズかつ、有効範囲を1, 無効範囲を0で表現した numpy.ndarray を使ってください。

### エージェント、グリッドの動作変更
wu_physarum/lib/setting.py の中身を変更することで、エージェントの動作や餌の伝達を変更することができます。

## 設計
このプログラムでは、大きく「モジホコリエージェント」で使用される mesa.Agent オブジェクトと「誘因力」「都市判定」などで使用される numpy.ndarrayオブジェクトが共存する形となっています。

実装の詳細はソースコードに任せることにしますが、各オブジェクトがどのように作用しているかの概略を以下に図示します。

### mesaのモジュール使用部
agt |agt |null |agt |null | // エージェント(mesa.Agent)

###|###|###|###|###|     // ステージ(mesa.space.SingleGrid)

### numpyのモジュール使用部
- ステージ領域を表現した行列
- データポイント領域を表現した行列
- 誘因力を表現した行列
- trailを表現した行列