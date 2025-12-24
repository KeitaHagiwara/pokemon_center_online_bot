from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

# デバイス情報の設定
options = XCUITestOptions()
options.platform_name = 'iOS'
options.platform_version = '18.6.2'  # iOSバージョンに合わせて変更
options.device_name = 'KeitaのiPhone'  # デバイス名
options.udid = '00008030-000268613A50402E'  # `idevice_id -l` で確認
options.automation_name = 'XCUITest'

# Safariブラウザを使う場合
options.browser_name = 'Safari'

# アプリを使う場合（バンドルIDを指定）
# options.bundle_id = 'com.example.app'
# options.app = '/path/to/your/app.ipa'  # IPAファイルのパス

# WebDriverAgent設定（実機の場合必須）
options.xcode_org_id = 'C685BDU5S2'  # あなたのTeam ID
options.xcode_signing_id = 'Apple Development'  # Apple Developmentに変更
options.update_wda_bundleid = 'com.keitahagiwara.WebDriverAgentRunner'  # 一意なBundle ID

# 【重要】実機用の追加設定
options.allow_provisioning_device_registration = True  # デバイス登録を許可
options.webdriver_agent_url = None  # 自動検出させる
options.clear_system_files = True  # システムファイルをクリア

# デバッグ用の追加設定
options.show_xcode_log = False  # Xcodeのビルドログを非表示（見やすくするため）
options.use_prebuilt_wda = True  # ビルド済みWDAを使用（高速化）
options.use_new_wda = False  # 既存のWDAセッションを再利用
options.wda_launch_timeout = 120000  # WDA起動タイムアウト(ms)を延長
options.wda_local_port = 8100  # WDAのローカルポート
options.wda_connection_timeout = 60000  # WDA接続タイムアウト(ms)

# iOS 18対応の設定
options.should_use_compact_responses = False  # コンパクトレスポンスを無効化
options.element_response_attributes = 'type,label'  # 必要な属性のみ取得

# Appiumサーバーに接続
print("Appiumサーバーへの接続を試みています...")
print("WebDriverAgentをビルド・起動しています（初回は2-3分かかります）...")
try:
    driver = webdriver.Remote('http://localhost:4723', options=options)
    print("✅ Appiumサーバーへの接続に成功しました")
    print("✅ WebDriverAgentが起動しました")
except Exception as e:
    print("\n❌ Appiumサーバーへの接続に失敗しました")
    print("\n【考えられる原因】")
    print("1. Appiumサーバーが起動していない")
    print("2. WebDriverAgentのビルドに失敗")
    print("3. デバイスの証明書が信頼されていない")
    print("\n【解決方法】")
    print("1. 別のターミナルでAppiumサーバーを起動:")
    print("   appium --log-level debug")
    print("\n2. iPhoneで証明書を信頼:")
    print("   設定 > 一般 > VPNとデバイス管理 > 'Keita Hagiwara' > 信頼")
    print("\n3. デバイスがロック解除されていることを確認")
    print(f"\n【詳細エラー】{e}")
    sys.exit(1)

try:
    print("\nSafariブラウザでWebページにアクセスしています...")
    # Webページにアクセス
    driver.get('https://example.com')
    print("✅ ページの読み込みが完了しました")

    # 要素の取得を待機
    wait = WebDriverWait(driver, 10)

    print("\nページの要素を検索しています...")
    # XPath指定（h1タグを検索）
    try:
        elements = driver.find_elements(AppiumBy.XPATH, '//h1')
        print(f"✅ 見出しを {len(elements)} 個発見しました:")
        for elem in elements:
            print(f"   - {elem.text}")
    except Exception as e:
        print(f"⚠️  見出しの取得に失敗: {e}")

    # CSSセレクタ指定（リンクを検索）
    try:
        links = driver.find_elements(AppiumBy.CSS_SELECTOR, 'a')
        print(f"\n✅ リンクを {len(links)} 個発見しました（最初の5個を表示）:")
        for link in links[:5]:
            href = link.get_attribute('href')
            text = link.text or '(テキストなし)'
            print(f"   - {text}: {href}")
    except Exception as e:
        print(f"⚠️  リンクの取得に失敗: {e}")

    # スクリーンショット
    try:
        screenshot_path = 'screenshot.png'
        driver.save_screenshot(screenshot_path)
        print(f"\n✅ スクリーンショットを保存しました: {screenshot_path}")
    except Exception as e:
        print(f"⚠️  スクリーンショットの保存に失敗: {e}")

    # スクロール
    try:
        print("\nページを下にスクロールしています...")
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(2)
        print("✅ スクロール完了")
    except Exception as e:
        print(f"⚠️  スクロールに失敗: {e}")

    # ページソース全体を取得（先頭500文字のみ表示）
    try:
        page_source = driver.page_source
        print(f"\n✅ ページソースを取得しました（長さ: {len(page_source)} 文字）")
        print(f"   先頭500文字: {page_source[:500]}...")
    except Exception as e:
        print(f"⚠️  ページソースの取得に失敗: {e}")

    print("\n✅ すべての操作が完了しました！")

except Exception as e:
    print(f"\n❌ エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()

finally:
    # セッション終了
    print("\nセッションを終了しています...")
    try:
        driver.quit()
        print("✅ セッションを終了しました")
    except:
        print("⚠️  セッションの終了に失敗しました（既に終了している可能性があります）")