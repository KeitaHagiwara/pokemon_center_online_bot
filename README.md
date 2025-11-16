# pokemon_center_online_bot
ポケモンセンターオンラインで抽選を自動化するBot

# AppiumによるiOSシミュレータのセットアップ
## 必要なツールのインストール
```
# Appiumのインストール
npm install -g appium

# Appium XCUITest Driverのインストール
appium driver install xcuitest

# Python Appiumクライアントのインストール
pip install Appium-Python-Client selenium
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