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


def login_pokemon_center_tor(email, password, tor_browser_path=None):
    """Tor Browserを使用してPokemon Center Onlineにログイン"""
    driver = None
    try:
        # Tor Browserのパスを設定
        if tor_browser_path is None:
            # デフォルトのTor Browserパス（Windows）
            tor_browser_path = r"C:\Users\Administrator\Desktop\Tor Browser\Browser\firefox.exe"
        
        # Firefox WebDriverのセットアップ（Tor BrowserはFirefoxベース）
        firefox_options = Options()
        firefox_options.binary_location = tor_browser_path
        
        # Tor Browserのプロファイルディレクトリを指定
        tor_profile_path = os.path.join(os.path.dirname(tor_browser_path), "..", "Browser", "TorBrowser", "Data", "Browser", "profile.default")
        firefox_options.add_argument(f"--profile={tor_profile_path}")
        
        # その他のオプション
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
        
        # Tor Browserの設定
        firefox_options.set_preference("network.proxy.type", 1)
        firefox_options.set_preference("network.proxy.socks", "127.0.0.1")
        firefox_options.set_preference("network.proxy.socks_port", 9050)
        firefox_options.set_preference("network.proxy.socks_version", 5)
        firefox_options.set_preference("network.proxy.socks_remote_dns", True)
        
        # WebDriverのセットアップ
        service = Service()
        driver = webdriver.Firefox(service=service, options=firefox_options)
        
        # タイムアウト設定
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(15)
        
        # ログインページに移動
        print("Tor BrowserでURLに接続中...")
        driver.get("https://www.pokemoncenter-online.com/login/")
        print(f"現在のURL: {driver.current_url}")
        
        # ページの読み込み完了を待機
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("ページの読み込み完了")
        
        # ログインフォームの要素を検索
        print("ログインフォームを検索中...")
        email_field = driver.find_element(By.ID, "login-form-email")
        password_field = driver.find_element(By.ID, "current-password")
        login_button = driver.find_element(By.XPATH, "//*[@id='form1Button']")
        print("ログインフォームの要素を発見")
        
        # ログイン情報を入力
        print("メールアドレスを入力中...")
        email_field.clear()
        email_field.send_keys(email)
        time.sleep(2)
        
        print("パスワードを入力中...")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(2)
        
        # ログインボタンをクリック
        print("ログインボタンをクリック中...")
        login_button.click()
        print("ログインボタンをクリックしました")
        
        # ログイン結果を待機
        time.sleep(10)
        
        # ログイン成功の確認
        current_url = driver.current_url
        if "login" not in current_url.lower():
            print("ログインが成功しました！")
            return True
        else:
            print("ログインに失敗した可能性があります")
            return False
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False
    finally:
        if driver:
            # ユーザーが手動で操作できるように少し待機
            input("エンターキーを押すとブラウザを閉じます...")
            driver.quit()


def main():
    """メイン関数"""
    print("🎮 Pokemon Center Online Tor Browser ログインスクリプト")
    print("=" * 60)
    
    # Tor Browserのパスを指定（必要に応じて変更）
    tor_browser_path = r"C:\Users\Administrator\Desktop\Tor Browser\Browser\firefox.exe"
    
    # ログイン情報（config.pyから読み込み）
    
    # Tor Browserの存在確認
    if not os.path.exists(tor_browser_path):
        print(f"❌ Tor Browserが見つかりません: {tor_browser_path}")
        print("Tor Browserのパスを正しく設定してください")
        return
    
    print(f"✅ Tor Browserのパス: {tor_browser_path}")
    print("🔒 Tor Browserでログインを開始します...")
    
    if login_pokemon_center_tor(EMAIL, PASSWORD, tor_browser_path):
        print("🎉 ログインが完了しました！")
    else:
        print("💥 ログインに失敗しました")


if __name__ == "__main__":
    main()
