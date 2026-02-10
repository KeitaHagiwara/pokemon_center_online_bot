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
build-wdaのインストールでエラーが出た場合はiOSシミュレータが利用可能状態ではないため、シミュレータSDKをインストールする
1. Xcodeを起動
2. Xcode > Settings > Components > Platform Support からiOSをGetする
3. ダウンロード後、Xcodeを再起動する
4. simctlの確認
```
sudo xcode-select -s /Applications/Xcode.app
xcode-select -p

xcrun simctl list devicetypes
xcrun simctl list runtimes
xcrun simctl list devices
```
ここで対応するデバイスが出ていればOK。build-wdaのインストールを再実行する

## Appiumサーバーの起動
```
appium
```

## スクリプトの実行
```
python sample.py
```

## PySideアプリの起動方法
```
# 通常の起動
python pyside_app.py

# デバッグモード(ホットリロード)での起動
python pyside_dev_runner.py pyside_app.py
```

## アプリケーションのビルド
```
# 本番用配布ビルド
pyinstaller pyside_app.spec --noconfirm

# 開発用ビルド（コンソールウィンドウを表示）
pyinstaller pyside_app_dev.spec --noconfirm
```