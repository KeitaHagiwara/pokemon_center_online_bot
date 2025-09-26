import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import EMAIL, PASSWORD


def build_firefox_driver(firefox_profile_path=None):
    """Firefox WebDriverを構築"""
    options = Options()
    
    # Firefoxのプロファイル設定（3rd party cookie / ETP / FPI 無効化）
    options.set_preference("network.cookie.cookieBehavior", 0)  # 0: すべて許可
    options.set_preference("network.cookie.lifetimePolicy", 0)
    options.set_preference("network.cookie.thirdparty.sessionOnly", False)
    options.set_preference("network.cookie.thirdparty.nonsecureSessionOnly", False)
    options.set_preference("privacy.trackingprotection.enabled", False)
    options.set_preference("privacy.partition.network_state", False)
    options.set_preference("privacy.firstparty.isolate", False)
    options.set_preference("dom.storage.enabled", True)
    options.set_preference("intl.accept_languages", "ja-JP,ja,en-US,en")
    
    # Cookie関連のセキュリティ設定を緩和
    options.set_preference("network.cookie.sameSite.laxByDefault", False)
    options.set_preference("network.cookie.sameSite.noneRequiresSecure", False)
    options.set_preference("network.cookie.leave-secure-alone", True)
    options.set_preference("network.cookie.thirdparty.sessionOnly", False)
    
    # ネットワーク設定を緩和
    options.set_preference("network.http.connection-timeout", 120)
    options.set_preference("network.http.response.timeout", 120)
    options.set_preference("network.dns.timeout", 60)
    
    # WebDriver検出を無効化
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    
    # ドメイン検証とセキュリティ設定を緩和
    options.set_preference("network.IDN_show_punycode", True)
    options.set_preference("network.dns.disablePrefetch", False)
    options.set_preference("security.tls.insecure_fallback_hosts", "pokemoncenter-online.com")
    options.set_preference("security.tls.unrestricted_rc4_fallback", True)
    
    # Content Security Policy (CSP) 設定を緩和
    options.set_preference("security.csp.enable", False)
    options.set_preference("security.csp.reporting.enabled", False)
    options.set_preference("security.csp.reporting.self", False)
    options.set_preference("security.csp.reporting.unsafe-inline", True)
    options.set_preference("security.csp.reporting.unsafe-eval", True)
    
    # フレーム関連の制限を緩和
    options.set_preference("security.mixed_content.block_active_content", False)
    options.set_preference("security.mixed_content.block_display_content", False)
    options.set_preference("security.mixed_content.upgrade_insecure_requests", False)
    
    # JavaScriptエラーを無視
    options.set_preference("javascript.enabled", True)
    options.set_preference("dom.disable_beforeunload", True)
    options.set_preference("browser.tabs.warnOnClose", False)
    options.set_preference("browser.tabs.warnOnCloseOtherTabs", False)
    
    # ネットワークエラーを無視
    options.set_preference("network.http.pipelining", True)
    options.set_preference("network.http.proxy.pipelining", True)
    options.set_preference("network.http.request.max-start-delay", 0)
    
    # プロファイルを指定する場合
    if firefox_profile_path:
        options.add_argument(f"--profile={firefox_profile_path}")
    
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1280, 900)
    driver.set_page_load_timeout(120)
    driver.implicitly_wait(20)
    
    return driver

def wait_and_switch_to_gigya_iframe(driver, timeout=30):
    """GigyaログインUIのiframeに切り替え"""
    try:
        # GigyaログインUIは iframe 内になることが多い
        iframe = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='gigya'], iframe[id*='gigya']"))
        )
        driver.switch_to.frame(iframe)
        print("Gigya iframeに切り替えました")
        return True
    except TimeoutException:
        print("Gigya iframeが見つかりませんでした")
        return False

def login_pokemon_center_firefox(email, password, firefox_profile_path=None):
    """Firefoxブラウザを使用してPokemon Center Onlineにログイン"""
    driver = None
    try:
        driver = build_firefox_driver(firefox_profile_path)
        wait = WebDriverWait(driver, 30)
        
        # ログインページに移動
        print("FirefoxでURLに接続中...")
        driver.get("https://www.pokemoncenter-online.com/login/")
        print(f"現在のURL: {driver.current_url}")
        
        # ページの読み込み完了を待機
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("ページの読み込み完了")
        
        # ログインリンクをクリック（必要に応じて）
        try:
            login_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='Login-Show'], a[href*='login']")))
            login_link.click()
            print("ログインリンクをクリックしました")
            time.sleep(3)
        except TimeoutException:
            print("ログインリンクが見つかりませんでした（直接ログインページの可能性）")
        
        # ログインフォームの要素を検索（正確なセレクターを使用）
        print("ログインフォームを検索中...")
        email_field = driver.find_element(By.ID, "login-form-email")
        password_field = driver.find_element(By.ID, "current-password")
        login_button = driver.find_element(By.XPATH, "//*[@id='form1Button']")
        print("ログインフォームの要素を発見")
        
        # ログイン情報を入力
        print("メールアドレスを入力中...")
        email_field.clear()
        email_field.send_keys(email)
        time.sleep(5)
        
        print("パスワードを入力中...")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(20)
        
        # ログインボタンをクリック
        print("ログインボタンをクリック中...")
        login_button.click()
        print("ログインボタンをクリックしました")
        
        # ログイン結果を待機（JavaScriptエラーを無視して継続）
        print("ログイン処理を待機中...")
        time.sleep(10)
        
        # 複数の方法でログイン成功を確認
        try:
            # 方法1: URLの変更を確認
            current_url = driver.current_url
            if "login" not in current_url.lower():
                print("ログインが成功しました！（URL変更確認）")
                return True
            
            # 方法2: ログアウトリンクの存在を確認
            try:
                logout_element = driver.find_element(By.CSS_SELECTOR, "[href*='Logout'], a[href*='Logout-Show'], .logout, .sign-out")
                if logout_element:
                    print("ログインが成功しました！（ログアウトリンク確認）")
                    return True
            except NoSuchElementException:
                pass
            
            # 方法3: ユーザー名表示の確認
            try:
                user_element = driver.find_element(By.CSS_SELECTOR, ".user-name, .account-name, .header-user, [data-user-state='logged-in']")
                if user_element:
                    print("ログインが成功しました！（ユーザー名表示確認）")
                    return True
            except NoSuchElementException:
                pass
            
            # 方法4: エラーメッセージの確認
            try:
                error_element = driver.find_element(By.CSS_SELECTOR, ".error, .alert-danger, .login-error")
                if error_element and error_element.is_displayed():
                    print(f"ログインエラー: {error_element.text}")
                    return False
            except NoSuchElementException:
                pass
            
            print("ログイン状態を確認できませんでした")
            return False
            
        except Exception as e:
            print(f"ログイン確認中にエラー: {e}")
            return False
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        # デバッグ用スクリーンショット
        try:
            ts = int(time.time())
            driver.save_screenshot(f"poke_login_fail_{ts}.png")
            print(f"スクリーンショット保存: poke_login_fail_{ts}.png")
        except:
            pass
        return False
    finally:
        if driver:
            # ユーザーが手動で操作できるように少し待機
            input("エンターキーを押すとブラウザを閉じます...")
            driver.quit()


def main():
    """メイン関数"""
    print("Pokemon Center Online Firefox ログインスクリプト")
    print("=" * 55)
    
    # Firefoxプロファイルのパス（必要に応じて変更）
    # firefox_profile_path = r"C:\Users\Administrator\AppData\Roaming\Mozilla\Firefox\Profiles\your_profile"
    # firefox_profile_path = r"C:\Users\Administrator\AppData\Roaming\Mozilla\Firefox\Profiles\4igib7q2.default-1758800242596"  # デフォルトプロファイルを使用
    firefox_profile_path = None
    
    # ログイン情報（config.pyから読み込み）
    
    print("Firefoxブラウザでログインを開始します...")
    
    if login_pokemon_center_firefox(EMAIL, PASSWORD, firefox_profile_path):
        print("🎉 ログインが完了しました！")
    else:
        print("💥 ログインに失敗しました")


if __name__ == "__main__":
    main()
