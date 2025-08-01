
[日本語](README-jp.md) | [العربية](README-ar.md) | [Português](README-pt.md) | [Español](README-es.md) | [English](README-en.md)

# Amazon スクレイピングプロジェクト ドキュメント（日本語）

## プロジェクト概要

このプロジェクトは、Amazon から商品情報をスクレイピングし、データを処理して指定されたサーバーにアップロードするためのものです。Selenium によるウェブ自動化と BeautifulSoup による HTML 解析を活用しています。画像処理、データ抽出、アップロードなどの機能を持つ複数の Python スクリプトで構成されています。

## ファイルの説明

### change.py

- **目的**: 指定された URL から画像をダウンロードし、サーバーにアップロードして JSON ファイルの画像 URL を更新します。
- **主な処理**:
  - 画像を URL からダウンロード
  - サーバーにアップロードして新しい画像 URL を取得
  - JSON ファイルの該当項目を更新
- **依存ライブラリ**: `requests`, `pandas`, `tqdm`, `BeautifulSoup`, `os`

### extract.py

- **目的**: JSON ファイルから画像リンクを抽出してテキストファイルに保存します。
- **主な処理**:
  - 商品情報の JSON ファイルを読み込む
  - 正規表現で画像 URL を抽出
  - 不要なリンクをキーワードで除外
  - 結果をテキストファイルに出力
- **依存ライブラリ**: `json`, `re`, `os`

### product_info.json / updated_product_info.json

- **内容**: 商品情報（価格、名前、画像、説明、属性など）を含む JSON ファイル
- **構造**:
  - `price`: 価格
  - `itm_name`: 商品名
  - `img1` ～ `img8`: 商品画像の URL
  - `itm_dsc`: HTML 形式の商品説明
  - `cat_id`, `s_id`: カテゴリ ID、店舗 ID
  - `attr`: 色やサイズなどの属性

### shop.py

- **目的**: Amazon ベストセラーページから商品詳細をスクレイピング
- **主な処理**:
  - ページをナビゲートし商品リンクや価格、タイトルを取得
  - 販売者情報や評価、説明を収集
  - データを CSV に保存
- **依存ライブラリ**: `selenium`, `webdriver_manager`, `pandas`, `time`, `os`

### upload.py

- **目的**: JSON ファイルから読み取った商品データをサーバーにアップロード
- **主な処理**:
  - JSON データを読み込んで POST リクエストで送信
  - レスポンスの確認とエラー処理
- **依存ライブラリ**: `requests`, `json`, `time`

### その他のスクリプト（size_and_color.py、amazon_item.py、など）

- **目的**: 異なる Amazon 商品ページからデータを抽出
- **主な処理**:
  - 商品タイトル、価格、画像、説明、属性を取得
  - カラーやサイズのバリエーションに対応
  - 結果を JSON に保存
- **依存ライブラリ**: `selenium`, `webdriver_manager`, `lxml`, `BeautifulSoup`, `time`, `os`, `json`, `tqdm`

## 実行およびデプロイ手順

### 環境構築

1. **Python のインストール**: Python 3.x がインストールされていることを確認
2. **必要パッケージのインストール**:
   ```bash
   pip install requests pandas tqdm beautifulsoup4 selenium lxml


3. **WebDriver の準備**: 使用するブラウザ用の WebDriver（例：EdgeDriver）をダウンロードし、PATH を通す

### スクリプトの実行

#### change.py

```bash
python change.py
```

#### extract.py

```bash
python extract.py
```

#### shop.py

```bash
python shop.py
```

#### upload.py

```bash
python upload.py
```

#### その他スクリプト

```bash
python script_name.py
```

## 注意事項

* Amazon の規約および robots.txt に従い、適切な方法でデータ収集を行ってください。
* ハードコードされた URL や XPath がある場合、サイト構造の変更に注意が必要です。
* すべてのデータ処理は法令と利用規約を遵守して行ってください。


