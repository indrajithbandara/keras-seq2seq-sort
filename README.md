# seq2seq sort

## 並び順がなくなった文字列から、文字のもとの列を復元します
- seq2seqのタスクの一つであるソートを自然言語に拡張します

- キャラクタレベル（文字粒度）で順序情報を失ったベクトル情報に対してベクトルを入力として、並び順が残っているもとの文章を構築しようと試みます

　もともとの想定していたユースケースとしては、アイディアを出し合うようなブレインストーミングなどで、よく付箋などを使ってキーワードをポスイットなどで張って、それから最終的に言いたいことを構築するようなことを私はよくやるのですが、そういったキーワード群を投入することで、自然に導きたい情報を帰結させることもできるなとか思いました。
 
 　データセットとネットワークサイズの限界で文字の並び替えのタスクを今回は与えてみようと思います。

## 先行研究
- [ORDER MATTERS: SEQUENCE TO SEQUENCE FOR SETS](https://arxiv.org/pdf/1511.06391.pdf)

## 文字列を破壊して並びなおす
- 東洋経済さんのオンラインコンテンツの記事タイトルを利用します
- char粒度で分解してBag of Wordsのようなベクトル表現に変換します
- Encoderの入力を行いベクトル化して、Decoderで元の並びを推定します

## ネットワーク
なんどか試してうまくいったモデルを使用したいと思います
```python
enc = input_tensor
enc = Flatten()(enc)
enc = RepeatVector(30)(enc)
enc = GRU(256, return_sequences=True)(enc)

dec = Bi(GRU(512, dropout=0.30, recurrent_dropout=0.25, return_sequences=True))(enc)
dec = TD(Dense(3000, activation='relu'))(dec)
dec = Dropout(0.5)(dec)
dec = TD(Dense(3000, activation='relu'))(dec)
dec = Dropout(0.1)(dec)
decode  = TD(Dense(3135, activation='softmax'))(dec)

model = Model(inputs=input_tensor, outputs=decode)
model.compile(loss='categorical_crossentropy', optimizer='adam')
```

## 前処理
**東洋経済さんのコンテンツをスクレイピングします**
```console
$ python3 12-scan.py
```

**スクレイピングしたhtml情報を解析してテキスト情報を取り出します**
```console
$ python3 16-parse-html.py
```

**テキスト情報とベクトル情報のペアを作ります**
```console
$ python3 19-make_title_boc_pair.py 
```

**機械学習できる数字のベクトル情報に変換します**
```console
$ python3 23-make_vector.py 
```

## 学習
**学習を行います**
（データサイズが巨大なので、128GByte程度のメインメモリが必要になります）
```console
$ python3 24-train.py --train
...
```
categorical_crossentropyの損失が0.3程度に下がると、ある程度の予想が可能にまります  
GTX1060で三日程度必要でした  

## 評価
入力に用いた順番が崩された情報と、それらを入力に、並び替えてそれらしい文字のペアはこのようになります  
```console
入力 ['､', 'が', 'ル', 'ダ', '子', 'を', '日', '銀', '本', '団', '上', 'メ', '男', '定', '体', '以', '確', '球', '卓']
出力 卓球男子団体､日本が銀メダ以以上を確定<EOS>

入力 ['は', 'い', 'リ', 'た', 'ャ', 'ル', '界', 'し', 'に', 'て', '戦', '由', '表', 'シ', '挑', '自', '限', '現']
出力 シャルリは表現の自由の限界に挑戦していた<EOS>

入力 ['｢', 'は', '｣', 'た', '国', 'と', 'に', 'る', '消', 'え', '攻', '米', '北', '朝', '鮮', '先', 'よ', '撃', '制', '藻', '屑']
出力 米国による｢北朝鮮先制攻撃｣は藻屑と消えた<EOS>

入力 ['､', 'が', '国', '世', '界', '子', '主', '沸', '騰', 'す', '部', 'る', 'マ', 'ス', '業', '中', '品', '電', '救', 'ホ']
出力 中国スマホが救世主､沸騰する電子部品業界<EOS>
```

## 終わりに
