### 使用手順

1. OCRツールのインストール  
OCRツールとして、Tesseractを使用します。
https://github.com/tesseract-ocr/tesseract を参照してTesseractのインストールを行います。  
※ 言語ファイルは https://github.com/tesseract-ocr/tessdata_fast のjpn.traineddataを使用しています。

2. Pythonのライブラリのインストール  
パッケージ管理に[Poetry](https://python-poetry.org/)を利用しています。
pyproject.tomlから環境を再現します。
Poetryのセットアップ後、使用するライブラリのインストールを行います。

```
$ poetry install
```

3. レシートの画像の設置  
レシートの画像を img/unprocessed に置きます。  
※ 現状対応しているのはjpgのみです。

4. 実行  
以下を実行します。  

```
$ poetry run python household_accounts
```

#### 詳細設定
- GUI画面でプルダウンになっている購入場所および品目の分類は household_accounts/config.py で設定を変えることができます。
- 品目の分類の選択および品目名のOCR結果に対する修正については、以下の場所に履歴を残しています。品目の分類については、次回同じ項目があった時には、この履歴を参照して変換した内容が当初から表示されます。また、品目名のOCR結果については、この履歴に対して類似度が高い品目がある場合は自動で変換を行います。
  - 品目の分類： csv/learning_file/category_fix.csv
  - 品目名のOCR結果の修正： csv/learning_file/item_ocr_fix.csv
