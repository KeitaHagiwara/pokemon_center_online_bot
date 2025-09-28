import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import EMAIL, PASSWORD


def login_pokemon_center(email, password):
    """Pokemon Center Onlineにログイン"""
    driver = None
    try:
        # macOS用 Chrome WebDriverのセットアップ
        chrome_options = Options()

        # macOS用のChromeプロファイル設定（必要に応じてコメントアウトを解除）
        # chrome_options.add_argument("--user-data-dir=/Users/{username}/Library/Application Support/Google/Chrome")
        # chrome_options.add_argument("--profile-directory=Default")  # または Profile 1, Profile 2など

        # macOS環境での既存Chromeセッション競合回避
        chrome_options.add_argument("--remote-debugging-port=9225")  # macOS用ポート番号
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")

        # macOS用の安定性向上オプション
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-gpu-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")

        # macOS特有の設定
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        # chrome_options.add_argument("--disable-images")  # 画像読み込みを無効化して高速化（必要に応じて有効化）
        # chrome_options.add_argument("--disable-javascript")  # JavaScriptが必要な場合はコメントアウト

        # 自動化検出回避
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("detach", True)

        # macOS用のUser-Agent設定（必要に応じて）
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # service = Service(ChromeDriverManager().install())
        new_driver = "/Users/keita/.wdm/drivers/chromedriver/mac64/140.0.7339.207/chromedriver-mac-arm64/chromedriver"
        service = Service(executable_path=new_driver)

        # ChromeDriverのタイムアウト設定
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # ログインページに移動
        print("URLに接続中...")
        driver.get("https://www.pokemoncenter-online.com/login/")
        print(f"現在のURL: {driver.current_url}")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("ページの読み込み完了")

        # ログインフォームの要素を検索
        email_field = driver.find_element(By.ID, "login-form-email")
        password_field = driver.find_element(By.ID, "current-password")
        login_button = driver.find_element(By.XPATH, "//*[@id='form1Button']")

        # ログイン情報を入力
        print("~~~~~~~~~~Email Input ~~~~~~~~")
        email_field.clear()
        email_field.send_keys(email)
        time.sleep(3)
        print("~~~~~~~~~~Password Input ~~~~~~~~")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(3)

        # ログインボタンをクリック
        print("~~~~~~~~~~Login Button Click ~~~~~~~~")
        login_button.click()
        print("~~~~~~~~~~Login Button Clicked ~~~~~~~~")
        time.sleep(540)

        return True

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        print("macOS環境でエラーが発生した場合のトラブルシューティング:")
        print("1. Chromeが最新版にアップデートされているか確認")
        print("2. システム環境設定 > セキュリティとプライバシー > プライバシー > オートメーション でChromeの権限を確認")
        print("3. ChromeDriverとChromeのバージョンが互換性があるか確認")
        print("4. 他のChromeプロセスが実行中でないか確認")
        return False
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    if login_pokemon_center(EMAIL, PASSWORD):
        print("ログイン成功")
    else:
        print("ログイン失敗")

