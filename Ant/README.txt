# アリの採餌行動のシミュレーション
アリは複数のフェロモンを使い分けることで仲間とコミュニケーションを取っていると言われている。
餌を集めるために行列をなすのもフェロモンを使った行動の結果である。

このプログラムではアリの行動パターンやフェロモンの機能について単純なモデルを仮定し、
シミュレーションを行う。

## 機能
左ドラッグで壁を生成
右クリックで餌を追加
左上のバーを使ってシミュレーションの速度を変更

## Scene
2つのシーンが用意されている
Scene1では3つの餌が用意されており、アリが餌を食べたタイミングが記録される
Scene2では1つの餌が用意されているが、各自で餌や巣の配置、地形などを変更して観察をするとよい。

## パラメーター
多くのパラメーターはUnity上から変更可能である。
Scene上のオブジェクトを選択しInspectorを開きスクリプトの要素にあるパラメーターが編集ができる。
主なパラメーターは以下の通り

Colonyオブジェクト Ant Generation
 - Span : アリが生成される間隔
 - Sensitive : 敏感アリの上限数
 - Insensitive : 鈍感アリの上限数
 - Sensitivity High,Low : アリの敏感さのパラメーター

ObstacleGeneratorオブジェクト Obstacle Generator
 - Thickness : 生成される壁の厚さ

Antオブジェクト Ant Controller
 - Parameters,Alpha : 内部活性の減衰率
 - Parameters,Threshold : 内部活性の限界値(下回ったアリは活動停止)
 - Pheromone Info, Alpha : フェロモンの減衰率
 - Pheromone Info, R : フェロモンの初期濃度
 - Pheromone Info, Threshold : アリの状態遷移時に必要なフェロモンの数
