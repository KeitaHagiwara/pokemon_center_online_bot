# WebDriverAgent セットアップガイド

## エラーコード 65 の主な原因と解決方法

### 1. WebDriverAgent の場所を確認

```bash
# AppiumのWebDriverAgentの場所を探す
find ~/.appium -name "WebDriverAgent.xcodeproj" 2>/dev/null
```

通常は以下の場所にあります:

```
~/.appium/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent
```

### 2. WebDriverAgent を手動でビルド（詳細エラー確認）

```bash
cd ~/.appium/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent

# 既存の設定をクリーンアップ
xcodebuild clean -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination 'id=00008030-001818542233402E'

# ビルド実行（エラーメッセージを確認）
xcodebuild build-for-testing \
  -project WebDriverAgent.xcodeproj \
  -scheme WebDriverAgentRunner \
  -destination 'id=00008030-001818542233402E' \
  DEVELOPMENT_TEAM=C685BDU5S2 \
  CODE_SIGN_IDENTITY="Apple Development" \
  PRODUCT_BUNDLE_IDENTIFIER="com.keitahagiwara.WebDriverAgentRunner"
```

### 3. よくあるエラーと解決策

#### A. 証明書エラー

```
error: Signing for "WebDriverAgentRunner" requires a development team.
```

**解決策:**

- Xcode > Settings > Accounts で Apple ID を追加
- 正しい Team ID を確認: `C685BDU5S2`

#### B. Bundle Identifier エラー

```
error: Bundle identifier has illegal characters
```

**解決策:**
Bundle ID を変更（逆ドメイン形式）:

```python
options.update_wda_bundleid = 'com.keitahagiwara.WebDriverAgentRunner'
```

#### C. プロビジョニングプロファイルエラー

```
error: No profiles for 'com.xxx.WebDriverAgentRunner' were found
```

**解決策:**

1. Xcode で `WebDriverAgent.xcodeproj` を開く
2. WebDriverAgentRunner ターゲットを選択
3. Signing & Capabilities タブ
4. "Automatically manage signing" を ON
5. Team を選択

### 4. Xcode で直接設定（推奨）

```bash
# WebDriverAgentプロジェクトを開く
open ~/.appium/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent/WebDriverAgent.xcodeproj
```

**Xcode での設定手順:**

1. **WebDriverAgentLib ターゲット:**

   - Signing & Capabilities
   - ✅ Automatically manage signing
   - Team: Keita Hagiwara (C685BDU5S2)
   - Bundle Identifier: `com.keitahagiwara.WebDriverAgentLib`

2. **WebDriverAgentRunner ターゲット:**

   - Signing & Capabilities
   - ✅ Automatically manage signing
   - Team: Keita Hagiwara (C685BDU5S2)
   - Bundle Identifier: `com.keitahagiwara.WebDriverAgentRunner`

3. **IntegrationApp ターゲット:**
   - Signing & Capabilities
   - ✅ Automatically manage signing
   - Team: Keita Hagiwara (C685BDU5S2)
   - Bundle Identifier: `com.keitahagiwara.IntegrationApp`

### 5. デバイスの設定確認

```bash
# デバイスがロック解除されているか確認
# デバイスで「このコンピュータを信頼」を許可しているか確認

# デバイスのUDIDを確認
idevice_id -l
# 出力: 00008030-000268613A50402E
```

### 6. iOS 18.x の場合の追加設定

iOS 18 以降では、Developer Mode を有効にする必要があります:

**iPhone の設定:**

1. 設定 > プライバシーとセキュリティ
2. デベロッパモード
3. オンに切り替え
4. 再起動

デベロッパモードが表示されない場合、以下の手順を実施してください。
1. デバイスを接続
2. 上部のデバイス選択で「オオタニリョウヘイのiPhone」を選択
3. Product > Run（または ⌘R）を実行
4. アラートが表示される: 「デベロッパーモードを有効にする必要があります」
5. iPhoneでアラートが表示されたら「設定」をタップ
6. 設定 > プライバシーとセキュリティ > デベロッパーモード が表示される

それでもエラーになる場合は、以下を試してください:
`cd ~/.appium/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent`

# デバイスにインストールを試みる
```
xcodebuild test \
  -project WebDriverAgent.xcodeproj \
  -scheme WebDriverAgentRunner \
  -destination "id=00008030-001818542233402E" \
  -allowProvisioningUpdates
```

### 7. ビルド成功後の確認

```bash
# ビルド成功したら、デバイスでアプリを確認
# 設定 > 一般 > VPNとデバイス管理
# "Keita Hagiwara" の証明書を信頼
```

### 8. Python スクリプトの最終設定

```python
options.xcode_org_id = 'C685BDU5S2'
options.xcode_signing_id = 'Apple Development'
options.update_wda_bundleid = 'com.keitahagiwara.WebDriverAgentRunner'
options.show_xcode_log = True  # 初回デバッグ用
```

## トラブルシューティング

### エラーが解決しない場合

1. **Appium サーバーを再起動**

   ```bash
   # Appiumサーバーを停止してから再起動
   appium --log-level debug
   ```

2. **WebDriverAgent を削除して再インストール**

   ```bash
   appium driver uninstall xcuitest
   appium driver install xcuitest
   ```

3. **デバイスを再起動**

4. **Xcode をアップデート**

   ```bash
   # Xcodeのバージョン確認
   xcodebuild -version

   # Command Line Toolsの確認
   xcode-select -p
   ```

## 実行手順

1. 上記の手順 2 で WebDriverAgent を手動ビルド
2. エラーメッセージを確認
3. 該当するエラーの解決策を実行
4. Xcode で設定を確認・修正
5. `python sample.py` を再実行

### Xcodeのセットアップが完了したら
iPhoneで「設定」>「一般」>「VPNとデバイス管理」>「<デバイスアカウント>」の証明書を信頼してください。

また、Safariでリモートオートメーション設定する必要があります。
以下の設定を実施してください:
設定 > Safari > 詳細 >
 - Web Inspector → オン
 - JavaScript → オン
 - リモートオートメーション  → オン
