import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import EMAIL, PASSWORD


def login_pokemon_center(email, password):
    """Pokemon Center Onlineにログイン"""
    driver = None
    try:
        # Safari WebDriverのセットアップ
        print("Safari WebDriverを起動中...")

        # 【重要】Safariを使用する前の事前準備:
        # 1. Safariを開く
        # 2. メニューバー > Safari > 設定 (またはSafari > 環境設定)
        # 3. 「詳細」タブをクリック
        # 4. 「メニューバーに"開発"メニューを表示」をチェック
        # 5. Safari > 開発 > 「リモートオートメーションを許可」をチェック
        #
        # SafariDriverはChromeDriverのような詳細なオプション設定はできません

        # Safari WebDriverの初期化
        # driver = webdriver.Safari()
        # driver.set_page_load_timeout(30)
        # driver.implicitly_wait(10)

        print("Safari WebDriverが正常に起動しました")

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

        # # ログインボタンをクリック
        # print("~~~~~~~~~~Login Button Click ~~~~~~~~")
        # login_button.click()
        # print("~~~~~~~~~~Login Button Clicked ~~~~~~~~")
        # time.sleep(540)

        return True

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        print("注意: Safariでエラーが発生した場合は以下を確認してください:")
        print("1. Safari > 開発 > 「リモートオートメーションを許可」が有効になっているか")
        print("2. Safariが最新版になっているか")
        print("3. macOSとSeleniumのバージョンが互換性があるか")
        return False
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    if login_pokemon_center(EMAIL, PASSWORD):
        print("ログイン成功")
    else:
        print("ログイン失敗")
