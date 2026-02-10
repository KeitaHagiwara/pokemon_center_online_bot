#!/bin/bash

# .envファイルを「source」や「.」で読み込む
if [ -f .env ]; then
    set -o allexport       # 自動的にエクスポート（全変数を環境変数扱いに）
    source .env
    set +o allexport
fi

# 環境変数の利用例
echo "DEVICE_ID: $UDID"
echo "XCODE_ORG_ID: $XCODE_ORG_ID"
echo "XCODE_BUNDLE_ID: $XCODE_BUNDLE_ID"

cd ~/.appium/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent

xcodebuild test-without-building \
    -xctestrun $(find . -name "*.xctestrun" | head -1) \
    -destination "id=$UDID" \
    -allowProvisioningUpdates

xcodebuild test \
    -project WebDriverAgent.xcodeproj \
    -scheme WebDriverAgentRunner \
    -destination "id=$UDID" \
    DEVELOPMENT_TEAM=$XCODE_ORG_ID \
    CODE_SIGN_IDENTITY="Apple Development" \
    PRODUCT_BUNDLE_IDENTIFIER=$XCODE_BUNDLE_ID \