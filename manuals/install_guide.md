# セットアップ手順

## 【アプリケーションのインストール】
- Github Desktop
- Visual Studio Code
- Google chrome
- Team Viewer

## 【AppStoreからのインストール】
- Xcode

## 【nodejsのインストール】
- Homebrewのインストール
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
※ターミナルは再起動する
```

## nvmをダウンロードしてインストールする
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# シェルを再起動する代わりに実行する
\. "$HOME/.nvm/nvm.sh"

# Node.jsをダウンロードしてインストールする：
nvm install 24

# Node.jsのバージョンを確認する：
node -v # "v24.13.0"が表示される。

# npmのバージョンを確認する：
npm -v # "11.6.2"が表示される。
```

## 【Xcode Commandline Toolsのインストール】
```
sudo xcode-select —install
```

## 【pyenvのインストール】
```
brew install pyenv
```

https://zenn.dev/kenghaya/articles/9f07914156fab5

```
pyenv install 3.12.2
```

## 【appiumのインストール】
```
npm install -g appium appium-doctor appium-webdriveragent
※動作確認
Appium -p <port>
```

セットアップ方法についてはREADME.mdを参照
