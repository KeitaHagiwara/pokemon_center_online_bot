import time, random, subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.gmail import get_latest_passcode

MAX_RETRY = 10

class SafariOperator:
    def __init__(self):
        pass

    def delete_browser_cache(self):
        subprocess.run(["rm", "-rf", "~/Library/Caches/com.apple.Safari/*"])
        time.sleep(2)

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

    def destroy_driver(self, driver):
        if driver:
            print("Safari WebDriverを終了中...")
            driver.quit()
            print("Safari WebDriverが正常に終了しました")

    def operate_elemenet(self, driver, by, element, action, value=None, click_type=1):
        """要素を操作"""
        try:
            element = driver.find_element(by, element)
            if action == "click":
                element.click()
                # element.send_keys(Keys.ENTER)
                # if click_type == 1:
                #     element.click()
                # elif click_type == 2:
                #     element.send_keys(Keys.ENTER)
                time.sleep(random.uniform(5.0, 10.0))
            elif action == "check":
                element.send_keys(Keys.SPACE)
                time.sleep(random.uniform(2.0, 5.0))
            elif action == "send_keys":
                element.clear()
                element.send_keys(value)
                time.sleep(random.uniform(2.0, 5.0))
        except NoSuchElementException as e:
            print(f"要素が見つかりません: {e}")
        except Exception as e:
            print(f"要素の操作中にエラーが発生しました: {e}")

    def goto_login_page(self, driver):
        """ログインページに移動"""
        driver.get("https://www.pokemoncenter-online.com/login/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("ログインページに移動しました")


    def lognin_pokemon_center(self, driver, email, password):
        # ログイン情報を入力
        print("~~~~~~~~~~Email Input ~~~~~~~~")
        self.operate_elemenet(driver, By.ID, "login-form-email", "send_keys", email)

        print("~~~~~~~~~~Password Input ~~~~~~~~")
        self.operate_elemenet(driver, By.ID, "current-password", "send_keys", password)

        # ログインボタンをクリック
        print("~~~~~~~~~~Login Button Click ~~~~~~~~")
        self.operate_elemenet(driver, By.XPATH, "//*[@id='form1Button']", "click")
        print("~~~~~~~~~~Login Button Clicked ~~~~~~~~")


    def two_step_verification(self, driver, auth_code):
        # パスコードを入力
        print("~~~~~~~~~~Auth Code Input ~~~~~~~~")
        self.operate_elemenet(driver, By.ID, "authCode", "send_keys", auth_code)

        # 認証ボタンをクリック
        print("~~~~~~~~~~Auth Button Clicked ~~~~~~~~")
        self.operate_elemenet(driver, By.ID, "authBtn", "click", click_type=2)

    # def login_pokemon_center(self, email, password):
    #     """Pokemon Center Onlineにログイン"""
    #     try:
    #         if "ログイン" in self.driver.page_source and "login" in self.driver.current_url:
    #             # ログイン情報を入力
    #             print("~~~~~~~~~~Email Input ~~~~~~~~")
    #             self.operate_elemenet(By.ID, "login-form-email", "send_keys", email)

    #             print("~~~~~~~~~~Password Input ~~~~~~~~")
    #             self.operate_elemenet(By.ID, "current-password", "send_keys", password)

    #             # ログインボタンをクリック
    #             print("~~~~~~~~~~Login Button Click ~~~~~~~~")
    #             self.operate_elemenet(By.XPATH, "//*[@id='form1Button']", "click")
    #             print("~~~~~~~~~~Login Button Clicked ~~~~~~~~")

    #             # 2段階認証画面に遷移したか確認
    #             if "パスコード入力" in self.driver.page_source and "login-mfa" in self.driver.current_url:
    #                 return True
    #             else:
    #                 return False
    #         else:
    #             print("ログイン画面が表示されていません")
    #             return True  # 既にログインしている場合も成功とみなす

    #     except Exception as e:
    #         print(f"エラーが発生しました: {e}")
    #         print("注意: Safariでエラーが発生した場合は以下を確認してください:")
    #         print("1. Safari > 開発 > 「リモートオートメーションを許可」が有効になっているか")
    #         print("2. Safariが最新版になっているか")
    #         print("3. macOSとSeleniumのバージョンが互換性があるか")
    #         return False

    # def two_step_verification(self, auth_code):
    #     """二段階認証コードの入力"""
    #     try:
    #         if "パスコード入力" in self.driver.page_source and "login-mfa" in self.driver.current_url:
    #             # パスコードを入力
    #             print("~~~~~~~~~~Auth Code Input ~~~~~~~~")
    #             self.operate_elemenet(By.ID, "authCode", "send_keys", auth_code)

    #             # 認証ボタンをクリック
    #             print("~~~~~~~~~~Auth Button Clicked ~~~~~~~~")
    #             self.operate_elemenet(By.ID, "authBtn", "click")
    #             print("~~~~~~~~~~Auth Button Clicked ~~~~~~~~")
    #             return True
    #         else:
    #             print("二段階認証画面が表示されていません")
    #             return True  # 二段階認証が不要な場合も成功とみなす

    #     except NoSuchElementException as e:
    #         print(f"二段階認証の要素が見つかりません: {e}")
    #         return False
    #     except Exception as e:
    #         print(f"二段階認証中にエラーが発生しました: {e}")
    #         return False

    def agree_terms(self, driver):
        """利用規約に同意"""
        print("~~~~~~~~~~Agree Terms ~~~~~~~~")
        self.operate_elemenet(driver,By.ID, "terms", "check")
        self.operate_elemenet(driver, By.ID, "terms_button", "click")
        print("~~~~~~~~~~Agreed to Terms ~~~~~~~~")


    def apply_lottery(self, driver, index=0):
        """抽選申し込み"""
        # 抽選応募ページに移動
        driver.get("https://www.pokemoncenter-online.com/lottery/apply.html")
        time.sleep(10)

        # 抽選情報を取得
        lottery_fields = driver.find_elements(By.CLASS_NAME, "subDl")
        lottery_field = lottery_fields[index]

        # 詳細を開く
        lottery_field.click()
        time.sleep(random.uniform(1.0, 3.0))

        # 商品にチェックを入れる
        item_checkboxes = driver.find_elements(By.CLASS_NAME, "radio")
        item_checkboxes[index].click()
        time.sleep(random.uniform(1.0, 3.0))

        # 募集要項に同意する
        agree_checkboxes = driver.find_elements(By.CLASS_NAME, "checkboxWrapper")
        agree_checkboxes[index].click()
        time.sleep(random.uniform(1.0, 3.0))

        # 抽選申し込み処理(モーダル起動)
        open_modal_buttons = driver.find_elements(By.CLASS_NAME, "popup-modal")
        open_modal_buttons[index].click()
        time.sleep(random.uniform(1.0, 3.0))

        # モーダル内の申し込みボタンをクリック
        apply_button = driver.find_element(By.ID, "applyBtn")
        apply_button.click()
        time.sleep(random.uniform(5))


# if __name__ == "__main__":

#     email = ""
#     password = ""

#     so = SafariOperator()
#     if so.login_pokemon_center(email, password):
#         print("ログイン成功")
#     else:
#         print("ログイン失敗")
