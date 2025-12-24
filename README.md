# pokemon_center_online_bot
ポケモンセンターオンラインで抽選を自動化するBot

# AppiumによるiOSシミュレータのセットアップ
## 必要なツールのインストール
```
# Appiumのインストール
npm install -g appium

# Appium XCUITest Driverのインストール
appium driver install xcuitest

# 追加ツールのインストール
brew install carthage
brew install libimobiledevice
brew install ios-deploy

# Python Appiumクライアントのインストール
pip install Appium-Python-Client selenium
```

## 接続されているiOSデバイスの確認
```
# 接続されているiOSデバイスのUDIDを表示
idevice_id -l
```

## XCodeの設定
```
# Xcode Command Line Toolsのインストール
xcode-select --install

# WebDriverAgentの依存関係をインストール
appium driver run xcuitest build-wda
```

## Appiumサーバーの起動
```
appium
```

## スクリプトの実行
```
python sample.py
```