### 使用手順

1. OCRツールのインストール  
OCRツールとして、Tesseractを使用します。
https://github.com/tesseract-ocr/tesseract を参照してTesseractのインストールを行います。  
※ 言語ファイルは https://github.com/tesseract-ocr/tessdata_fast のjpn.traineddataを使用しています。

2. Pythonのライブラリのインストール  
パッケージ管理に[Pipenv](https://pipenv-ja.readthedocs.io/ja/translate-ja/)を利用しています。
PipfileおよびPipfile.lockから環境を再現します。
Pipenvのセットアップ後、使用するライブラリのインストールを行います。

```
$ pipenv sync
```

3. レシートの画像の設置  
レシートの画像を img/unprocessed に置きます。  
※ 現状対応しているのはjpgのみです。

4. 実行
以下を実行します。  

```
$ pipenv shell  # 仮想環境を起動
$ python household_account
```

#### 詳細設定
- GUI画面でプルダウンになっている購入場所および品目の分類は household_accounts/config.py で設定を変えることができます。
- 品目の分類の選択および品目名のOCR結果に対する修正については、以下の場所に履歴を残しています。次回同じ項目があった時には、この履歴を参照して変換した内容が当初から表示されます。
  - 品目の分類： csv/learning_file/category_fix.csv
  - 品目名のOCR結果の修正： csv/learning_file/item_ocr_fix.csv
