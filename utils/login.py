import time
import random
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 自作モジュール
from utils.gmail import extract_target_str_from_gmail_text_in_3min

MAX_RETRY_PASSCODE = 10

def login_pokemon_center_online(driver, appium_utils, email, password):

    try:
        # ログイン画面に遷移
        driver.get("https://www.pokemoncenter-online.com/login/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.TAG_NAME, "body")))
        print("ログインページに移動しました")

        time.sleep(random.uniform(1, 3))

        print("IDを入力中...")
        email_form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'login-form-email'))
        )
        email_form.send_keys(email)

        time.sleep(random.uniform(1, 3))

        print("パスワードを入力中...")
        password_form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'current-password'))
        )
        password_form.send_keys(password)

        time.sleep(random.uniform(1, 3))

        print("ログインボタンをクリック中...")
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//*[@id='form1Button']"))
        )
        login_button.click()

        time.sleep(10)
        if ("ログイン" in driver.page_source and "/login/" in driver.current_url):
            raise Exception("ログインページに留まっています")

        # 2段階認証処理
        auth_success = False
        for retry_j in range(MAX_RETRY_PASSCODE):
            auth_code = extract_target_str_from_gmail_text_in_3min(
                to_email=email,
                subject_keyword="[ポケモンセンターオンライン]ログイン用パスコードのお知らせ",
                email_type="passcode"
            )
            if auth_code:
                auth_success = True
                break
            time.sleep(15)

        if not auth_success:
            raise Exception("2段階認証コードの取得に失敗しました")

        print("パスコードを入力中...")
        passcode_form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'authCode'))
        )
        passcode_form.send_keys(auth_code)

        time.sleep(random.uniform(1, 3))

        print("認証ボタンをクリック中...")
        auth_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'authBtn'))
        )
        auth_button.click()

        time.sleep(10)
        if ("パスコード入力" in driver.page_source and "/login-mfa/" in driver.current_url):
            raise Exception("2段階認証に失敗しました")

        if "利用規約再同意" in driver.page_source:
            # 同意チェックボックスを安全に取得してクリック
            terms_checkboxes = appium_utils.safe_find_elements(
                AppiumBy.ID,
                'terms',
                attempt=0
            )
            if not terms_checkboxes or len(terms_checkboxes) == 0:
                raise ValueError("同意チェックボックスが見つかりませんでした")

            terms_checkbox = terms_checkboxes[0]
            terms_checkbox.click()
            time.sleep(random.uniform(1, 3))

            # プライバシーチェックボックスを安全に取得してクリック
            privacy_policy_checkboxes = appium_utils.safe_find_elements(
                AppiumBy.ID,
                'privacyPolicy',
                attempt=0
            )
            if not privacy_policy_checkboxes or len(privacy_policy_checkboxes) == 0:
                raise ValueError("プライバシーチェックボックスが見つかりませんでした")
            privacy_policy_checkbox = privacy_policy_checkboxes[0]
            privacy_policy_checkbox.click()
            time.sleep(random.uniform(1, 3))

            # 次へ進むボタンを安全に取得してクリック
            if appium_utils.wait_and_click_element(AppiumBy.ID, 'terms_button'):
                print("✅ 利用規約同意の次へ進むボタンをクリックしました")
            else:
                print("❌ 利用規約同意の次へ進むボタンのクリックに失敗しました")

            time.sleep(10)


        return True

    except Exception as e:
        print(f"ログイン処理中にエラーが発生しました: {e}")
        return False