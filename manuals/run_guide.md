# 実行ガイド

## 前提条件

1. ✅ WebDriverAgentのビルドが成功していること
2. ✅ iPhoneで証明書を信頼済みであること（設定 > 一般 > VPNとデバイス管理）
3. ✅ iPhoneがMacに接続されていること
4. ✅ iPhoneがロック解除されていること

## 実行手順

### ステップ1: Appiumサーバーを起動

**別のターミナルウィンドウ**で以下のコマンドを実行してください:

```bash
appium --log-level debug
```

デバッグログが不要な場合は:

```bash
appium
```

✅ 以下のようなメッセージが表示されればOK:

```
[Appium] Welcome to Appium v2.x.x
[Appium] Appium REST http interface listener started on http://0.0.0.0:4723
```

### ステップ2: Pythonスクリプトを実行

**元のターミナルウィンドウ**で以下のコマンドを実行:

```bash
cd /Users/keita/Desktop/Develop_Apps/pokemon_center_online_bot
python sample.py
```

## トラブルシューティング

### エラー: Connection refused

```
ConnectionRefusedError: [Errno 61] Connection refused
```

**原因:** Appiumサーバーが起動していない

**解決策:** ステップ1のAppiumサーバー起動コマンドを実行してください

### エラー: WebDriverAgent failed with code 65

**原因:** 証明書の信頼設定が未完了

**解決策:**

1. iPhoneで「設定」を開く
2. 一般 > VPNとデバイス管理
3. 「Keita Hagiwara」の証明書を信頼

### エラー: Device is locked

**原因:** iPhoneがロックされている

**解決策:** iPhoneのロックを解除してください

### エラー: Could not find a connected device

**原因:** iPhoneが接続されていない、または認識されていない

**解決策:**

1. iPhoneをMacに再接続
2. iPhoneで「このコンピュータを信頼」をタップ
3. デバイスUDIDを確認:

```bash
idevice_id -l
```

出力が `00008030-000268613A50402E` であることを確認

## Appiumのインストール（初回のみ）

Appiumがインストールされていない場合:

```bash
# Node.jsがインストールされていることを確認
node --version

# Appiumをグローバルインストール
npm install -g appium

# XCUITestドライバーをインストール
appium driver install xcuitest

# インストール確認
appium --version
appium driver list
```

## 実行の流れ

```
┌─────────────────────────┐
│ ターミナル1             │
│ appium --log-level debug│ ← Appiumサーバー起動
└─────────────────────────┘
           ↓
    サーバー起動完了
           ↓
┌─────────────────────────┐
│ ターミナル2             │
│ python sample.py        │ ← Pythonスクリプト実行
└─────────────────────────┘
           ↓
    Appiumサーバーに接続
           ↓
    WebDriverAgentを起動
           ↓
    iPhoneのSafariが起動
           ↓
    スクレイピング実行
```

## 注意事項

- Appiumサーバーは**常に起動したまま**にしておく
- Pythonスクリプトを実行するたびに、Appiumサーバーを再起動する必要はない
- iPhoneは**ロック解除状態**を保つ
- 初回実行時はWebDriverAgentのビルドに時間がかかる（1-2分程度）

## Team IDを確認する
```bash
cd ~/.appium/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent

xcodebuild -showBuildSettings -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner | grep DEVELOPMENT_TEAM
```

## 証明書の設定
```bash
cd ~/.appium/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent

# 証明書を初期化したい場合
xcodebuild clean \
  -project WebDriverAgent.xcodeproj \
  -scheme WebDriverAgentRunner \
  -destination "id=00008030-001818542233402E"

xcodebuild test-without-building \
  -xctestrun $(find . -name "*.xctestrun" | head -1) \
  -destination 'id=00008030-001818542233402E' \
  -allowProvisioningUpdates

xcodebuild test \
  -project WebDriverAgent.xcodeproj \
  -scheme WebDriverAgentRunner \
  -destination 'id=00008030-001818542233402E' \
  DEVELOPMENT_TEAM=LYJMR4D7JA \
  CODE_SIGN_IDENTITY="Apple Development" \
  PRODUCT_BUNDLE_IDENTIFIER="com.ootaniryouhei.WebDriverAgentRunner" \
```