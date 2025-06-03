# 日経クロストレンド RSS自動生成ツール

このリポジトリは、日経クロストレンドの記事を自動的に取得し、RSSフィードを生成するためのツールです。GitHub Actionsを使用して毎日自動的に実行され、最新の記事を取得してRSSフィードを更新します。

## 機能

- 日経クロストレンドのトップページから最新記事を自動取得
- 「続き」ボタンを自動的にクリックして記事全文を取得
- 記事内の画像も自動的にダウンロード
- Markdown形式で記事を保存
- RSSフィードを自動生成
- GitHub Pagesを使用してRSSフィードを公開
- GitHub Actionsによる毎日の自動実行

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/YOUR_USERNAME/nikkei-xt-rss.git
cd nikkei-xt-rss
```

### 2. 必要なPythonパッケージのインストール

```bash
pip install selenium webdriver-manager beautifulsoup4 requests
```

### 3. GitHub Secretsの設定

1. GitHubリポジトリのページで「Settings」タブをクリック
2. 左側のメニューから「Secrets and variables」→「Actions」を選択
3. 「New repository secret」ボタンをクリック
4. 以下の2つのシークレットを追加:
   - `NIKKEI_USERNAME`: 日経クロストレンドのログインID（メールアドレス）
   - `NIKKEI_PASSWORD`: 日経クロストレンドのパスワード

### 4. GitHub Pagesの有効化

1. GitHubリポジトリのページで「Settings」タブをクリック
2. 左側のメニューから「Pages」を選択
3. 「Source」セクションで「Deploy from a branch」を選択
4. 「Branch」ドロップダウンから「gh-pages」を選択し、「/(root)」を選択
5. 「Save」ボタンをクリック

### 5. 手動実行（オプション）

初回のRSSフィード生成を手動で実行する場合:

1. GitHubリポジトリのページで「Actions」タブをクリック
2. 左側のワークフローリストから「Daily Article Fetch」を選択
3. 「Run workflow」ボタンをクリック
4. 「Run workflow」ボタンを再度クリックして実行開始

## ディレクトリ構成

```
nikkei-xt-rss/
├── .github/
│   └── workflows/
│       └── daily-fetch.yml  # GitHub Actions ワークフロー設定
├── scripts/
│   ├── fetch_articles.py    # 記事取得スクリプト
│   ├── generate_rss.py      # RSSフィード生成スクリプト
│   └── utils.py             # ユーティリティ関数（必要に応じて）
├── data/
│   ├── articles/            # 記事本文（Markdown形式）
│   ├── images/              # 記事内の画像
│   └── articles_data.json   # 記事メタデータ
└── docs/
    ├── index.html           # シンプルなウェブページ
    └── feed.xml             # 生成されたRSSフィード
```

## RSSフィードの購読方法

GitHub Pagesが有効化されると、以下のURLでRSSフィードが公開されます:

```
https://YOUR_USERNAME.github.io/nikkei-xt-rss/feed.xml
```

このURLをお好みのRSSリーダー（Readwise Readerなど）に登録することで、最新記事を自動的に受信できます。

## 注意事項

- このツールは個人的な利用を目的としています
- 過度なアクセスを行わないよう、実行頻度は1日1回に制限しています
- 日経クロストレンドの利用規約に従って使用してください
- コンテンツの著作権は日経BP社に帰属します

## カスタマイズ

### 実行スケジュールの変更

`.github/workflows/daily-fetch.yml`ファイル内の`cron`式を変更することで、実行スケジュールを調整できます:

```yaml
on:
  schedule:
    - cron: '0 21 * * *'  # 毎日UTC 21:00（日本時間朝6:00頃）に実行
```

### 取得する記事の条件変更

`scripts/fetch_articles.py`内の`get_yesterday_articles`メソッドを修正することで、取得する記事の条件を変更できます。

## トラブルシューティング

### GitHub Actionsが失敗する場合

1. Actionsタブでエラーログを確認
2. 最も多い原因はログイン情報の誤りです。Secretsの設定を確認してください
3. 日経クロストレンドのサイト構造が変更された場合は、スクリプトの更新が必要になる場合があります

### RSSフィードが更新されない場合

1. 手動実行を試して、エラーログを確認
2. 前日に新しい記事が公開されていない可能性があります
3. GitHub Pagesの設定が正しいか確認してください

## ライセンス

MITライセンス
