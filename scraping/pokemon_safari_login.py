import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SafariOperator:
    def __init__(self):
        self.driver = self.create_driver()

    def create_driver(self):
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
        driver = webdriver.Safari()
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        print("Safari WebDriverが正常に起動しました")

        return driver

    def destroy_driver(self):
        if self.driver:
            print("Safari WebDriverを終了中...")
            self.driver.quit()
            print("Safari WebDriverが正常に終了しました")

    def operate_elemeent(self, by, element, action, value=None):
        """要素を操作"""
        try:
            element = self.driver.find_element(by, element)
            if action == "click":
                element.click()
            elif action == "send_keys":
                element.clear()
                element.send_keys(value)
            time.sleep(5)
        except NoSuchElementException as e:
            print(f"要素が見つかりません: {e}")
        except Exception as e:
            print(f"要素の操作中にエラーが発生しました: {e}")

    def login_pokemon_center(self, email, password):
        """Pokemon Center Onlineにログイン"""
        try:

            # ログインページに移動
            print("URLに接続中...")
            self.driver.get("https://www.pokemoncenter-online.com/login/")
            print(f"現在のURL: {self.driver.current_url}")

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("ページの読み込み完了")

            # ログインフォームの要素を検索
            password_field = self.driver.find_element(By.ID, "current-password")
            login_button = self.driver.find_element(By.XPATH, "//*[@id='form1Button']")

            # ログイン情報を入力
            print("~~~~~~~~~~Email Input ~~~~~~~~")
            self.operate_elemeent(By.ID, "login-form-email", "send_keys", email)

            print("~~~~~~~~~~Password Input ~~~~~~~~")
            self.operate_elemeent(By.ID, "current-password", "send_keys", password)

            # ログインボタンをクリック
            print("~~~~~~~~~~Login Button Click ~~~~~~~~")
            self.operate_elemeent(By.XPATH, "//*[@id='form1Button']", "click")
            print("~~~~~~~~~~Login Button Clicked ~~~~~~~~")
            return True

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            print("注意: Safariでエラーが発生した場合は以下を確認してください:")
            print("1. Safari > 開発 > 「リモートオートメーションを許可」が有効になっているか")
            print("2. Safariが最新版になっているか")
            print("3. macOSとSeleniumのバージョンが互換性があるか")
            return False

    def two_step_verification(self, auth_code):
        """二段階認証コードの入力"""
        try:
            # パスコードを入力
            print("~~~~~~~~~~Auth Code Input ~~~~~~~~")
            self.operate_elemeent(By.ID, "authCode", "send_keys", auth_code)

            # 認証ボタンをクリック
            print("~~~~~~~~~~Auth Button Clicked ~~~~~~~~")
            self.operate_elemeent(By.ID, "authBtn", "click")
            print("~~~~~~~~~~Auth Button Clicked ~~~~~~~~")
            return True

        except NoSuchElementException as e:
            print(f"二段階認証の要素が見つかりません: {e}")
            return False
        except Exception as e:
            print(f"二段階認証中にエラーが発生しました: {e}")
            return False

    def apply_lottery(self):
        """抽選申し込み"""
        try:
            # 抽選応募ページに移動
            self.driver.get("https://www.pokemoncenter-online.com/lottery/apply.html")
            time.sleep(10)

            # 抽選情報を取得
            lottery_fields = self.driver.find_elements(By.CLASS_NAME, "subDl")
            for lottery_field in lottery_fields:
                lottery_field.click()
                time.sleep(2)
                # ------------
                # 抽選申し込み処理
                # ------------

            return True

        except Exception as e:
            print(f"抽選申し込み中にエラーが発生しました: {e}")
            return False

# if __name__ == "__main__":
#     email = ""
#     password = ""
#     driver = create_driver()
#     if login_pokemon_center(driver, email, password):
#         print("ログイン成功")
#     else:
#         print("ログイン失敗")
