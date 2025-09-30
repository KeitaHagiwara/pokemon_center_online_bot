# OAuth 2.0 クライアント作成手順

## 重要な注意事項

現在のクレデンシャルファイルは「サービスアカウント」です。
個人の Gmail アカウントにアクセスするには「OAuth 2.0 クライアント ID」が必要です。

## 新しい OAuth 2.0 クライアント作成手順

### 1. Google Cloud Console にアクセス

https://console.cloud.google.com/

### 2. 既存のプロジェクト「pokemon-center-online-bot」を選択

### 3. OAuth 2.0 クライアント ID を作成

1. 左側メニュー > 「API とサービス」 > 「認証情報」
2. 「+ 認証情報を作成」 > 「OAuth クライアント ID」
3. **アプリケーションの種類: 「デスクトップ アプリケーション」を選択**
4. 名前: 「Pokemon Center OAuth Client」（任意）
5. 「作成」をクリック

### 4. OAuth 同意画面の設定（初回のみ）

1. 「OAuth 同意画面」タブをクリック
2. User Type: 「外部」を選択 > 「作成」
3. アプリ情報を入力:
   - アプリ名: Pokemon Center Bot
   - ユーザーサポートメール: あなたのメールアドレス
   - 開発者の連絡先情報: あなたのメールアドレス
4. 「保存して次へ」
5. スコープは後で設定するので、「保存して次へ」
6. テストユーザーにあなたの Gmail アドレスを追加
7. 「保存して次へ」

### 5. クレデンシャルファイルのダウンロード

1. 作成した OAuth 2.0 クライアント ID の右側の ⬇️ アイコンをクリック
2. JSON ファイルをダウンロード
3. ファイル名を「oauth_credentials.json」に変更
4. このファイルを credentials/ フォルダに配置

### 6. test.py の修正

cred_json のパスを新しい OAuth クレデンシャルファイルに変更:

```python
cred_json = Path("./credentials/oauth_credentials.json")
```

## 正しいクレデンシャルファイルの形式

### OAuth クライアント（個人 Gmail 用）

```json
{
  "installed": {
    "client_id": "xxx.googleusercontent.com",
    "project_id": "pokemon-center-online-bot",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "xxx",
    "redirect_uris": ["http://localhost"]
  }
}
```

### サービスアカウント（企業ドメイン用）

```json
{
  "type": "service_account",
  "project_id": "pokemon-center-online-bot",
  ...
}
```
