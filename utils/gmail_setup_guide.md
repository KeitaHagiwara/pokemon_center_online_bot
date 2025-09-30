# Gmail API セットアップガイド

## 1. Google Cloud Console 設定

### プロジェクト作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成または既存のプロジェクトを選択
3. プロジェクト名: `pokemon-center-bot` (任意)

### Gmail API 有効化

1. 左側メニュー > 「API とサービス」 > 「ライブラリ」
2. 「Gmail API」を検索
3. 「Gmail API」をクリック > 「有効にする」

### OAuth 2.0 認証情報作成

1. 左側メニュー > 「API とサービス」 > 「認証情報」
2. 「+ 認証情報を作成」 > 「OAuth クライアント ID」
3. アプリケーションの種類: 「デスクトップ アプリケーション」
4. 名前: 「Pokemon Center Gmail Bot」(任意)
5. 「作成」をクリック

### credentials.json ダウンロード

1. 作成した OAuth 2.0 クライアント ID の右側にある ⬇️ アイコンをクリック
2. `credentials.json` ファイルをダウンロード
3. このファイルを `/Users/keita/Desktop/Develop_Apps/pokemon_center_online_bot/utils/` ディレクトリに配置

## 2. Python 環境セットアップ

### 依存関係のインストール

```bash
cd /Users/keita/Desktop/Develop_Apps/pokemon_center_online_bot
pip install -r requirements.txt
```

### 必要なライブラリ

- google-auth
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client

## 3. 初回認証

### 認証プロセス

1. `python utils/gmail.py` を実行
2. ブラウザが自動的に開きます
3. Google アカウントでログイン
4. アプリケーションの権限を許可
5. `token.json` ファイルが自動的に生成されます

### 注意事項

- `credentials.json`: GitHub 等にコミットしないでください
- `token.json`: 認証トークンファイル（自動生成）
- 初回のみブラウザでの認証が必要です

## 4. 使用方法

### 基本的な使用例

```python
from utils.gmail import get_latest_emails, search_emails

# 最新の5件のメールを取得
emails = get_latest_emails(5)

# Pokemon関連のメールを検索
pokemon_emails = search_emails("pokemon OR ポケモン", 3)

# 特定の送信者からのメールを検索
sender_emails = search_emails("from:noreply@pokemoncenter-online.com", 10)
```

### 検索クエリの例

- `from:example@gmail.com` - 特定の送信者
- `subject:重要` - 件名に「重要」を含む
- `has:attachment` - 添付ファイルあり
- `is:unread` - 未読メール
- `newer_than:7d` - 7 日以内
- `pokemon OR ポケモン` - OR 検索

## 5. ファイル構成

```
pokemon_center_online_bot/
├── utils/
│   ├── gmail.py                 # Gmail API メインファイル
│   ├── credentials.json         # OAuth認証情報（要配置）
│   ├── token.json              # 認証トークン（自動生成）
│   └── gmail_setup_guide.md    # このガイド
├── requirements.txt            # 依存関係
└── ...
```

## 6. トラブルシューティング

### よくあるエラー

**認証エラー**

```
google.auth.exceptions.RefreshError
```

解決策: `token.json` を削除して再認証

**API 無効エラー**

```
Gmail API has not been enabled
```

解決策: Google Cloud Console で Gmail API が有効になっているか確認

**権限エラー**

```
insufficient permission
```

解決策: OAuth 同意画面でスコープを確認

### セキュリティ設定

- Google アカウントの 2 段階認証を有効にすることを推奨
- アプリパスワードは不要（OAuth2.0 使用のため）
