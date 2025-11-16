import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import EMAIL, PASSWORD

nick_name = "フォーク"
name = "萩原　佳太"
name_kana = "ハギワラ　ケイタ"
birth_year = "1991"
birth_month = "07"
birth_day = "09"
gender_id = 1  # 1: 男性, 2: 女性, 3: どちらも選ばない
postcode = "2160022"
street_address = "平6-10-52"
building = "パストラル宮前平202"
tel = "08033452879"
password = "Vaceatker@1"
url = "https://www.pokemoncenter-online.com/new-customer/?token=cQ5bOYk05nH1TA668SsOK%2BKbuOcAuahJaBQbRZRsq0o%3D"

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
        driver = webdriver.Safari()
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)

        print("Safari WebDriverが正常に起動しました")

        # ログインページに移動
        url = "https://www.pokemoncenter-online.com/new-customer/?token=UAoMjpHlJm%2BKcBtxnmwn%2BOhL%2BnwWfl%2BI1Amiqa3wiEE%3D"
        print("URLに接続中...")
        driver.get(url)
        print(f"現在のURL: {driver.current_url}")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("ページの読み込み完了")

        # フォームの要素を検索
        nick_name_field = driver.find_element(By.ID, "registration-form-nname")
        name_field = driver.find_element(By.ID, "registration-form-fname")
        name_kana_field = driver.find_element(By.ID, "registration-form-kana")
        birth_year_field = driver.find_element(By.ID, "registration-form-birthdayyear")
        birth_month_field = driver.find_element(By.ID, "registration-form-birthdaymonth")
        birth_day_field = driver.find_element(By.ID, "registration-form-birthdayday")
        gender_field = driver.find_element(By.NAME, "dwfrm_profile_customer_gender")
        postcode_field = driver.find_element(By.ID, "registration-form-postcode")
        street_address_field = driver.find_element(By.ID, "registration-form-address-line1")
        building_field = driver.find_element(By.ID, "registration-form-address-line2")
        tel_field = driver.find_element(By.NAME, "dwfrm_profile_customer_phone")
        password_field = driver.find_element(By.NAME, "dwfrm_profile_login_password")
        confirm_password_field = driver.find_element(By.NAME, "dwfrm_profile_login_passwordconfirm")

        email_magazine_checkbox = driver.find_elements(By.NAME, "dwfrm_profile_customer_addtoemaillist")

        terms_checkbox = driver.find_element(By.ID, "terms")
        policy_checkbox = driver.find_element(By.ID, "privacyPolicy")

        confirm_button = driver.find_element(By.XPATH, '//*[@id="registration_button"]')

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


# if __name__ == "__main__":
    # if login_pokemon_center(EMAIL, PASSWORD):
    #     print("ログイン成功")
    # else:
    #     print("ログイン失敗")

def input_form(driver, selector_obj, selector_value, input_value, is_selectbox=False):
    try:
        element = driver.find_element(selector_obj, selector_value)
        if not is_selectbox:
            element.clear()
        element.send_keys(input_value)
        time.sleep(2)
    except NoSuchElementException:
        print(f"要素が見つかりません: {selector_obj}")

# Safari WebDriverの初期化
driver = webdriver.Safari()
driver.set_page_load_timeout(30)
driver.implicitly_wait(10)

print("Safari WebDriverが正常に起動しました")

# ログインページに移動
url = "https://www.pokemoncenter-online.com/new-customer/?token=cQ5bOYk05nH1TA668SsOK%2BKbuOcAuahJaBQbRZRsq0o%3D"
print("URLに接続中...")
driver.get(url)
print(f"現在のURL: {driver.current_url}")

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
print("ページの読み込み完了")

# フォームの要素を検索
# nick_name_field = driver.find_element(By.ID, "registration-form-nname")
# name_field = driver.find_element(By.ID, "registration-form-fname")
# name_kana_field = driver.find_element(By.ID, "registration-form-kana")
# birth_year_field = driver.find_element(By.ID, "registration-form-birthdayyear")
# birth_month_field = driver.find_element(By.ID, "registration-form-birthdaymonth")
# birth_day_field = driver.find_element(By.ID, "registration-form-birthdayday")
# gender_field = driver.find_element(By.NAME, "dwfrm_profile_customer_gender")
# postcode_field = driver.find_element(By.ID, "registration-form-postcode")
# street_address_field = driver.find_element(By.ID, "registration-form-address-line1")
# building_field = driver.find_element(By.ID, "registration-form-address-line2")
# tel_field = driver.find_element(By.NAME, "dwfrm_profile_customer_phone")
# password_field = driver.find_element(By.NAME, "dwfrm_profile_login_password")
# confirm_password_field = driver.find_element(By.NAME, "dwfrm_profile_login_passwordconfirm")

email_magazine_checkbox = driver.find_elements(By.NAME, "dwfrm_profile_customer_addtoemaillist")

terms_checkbox = driver.find_element(By.ID, "terms")
policy_checkbox = driver.find_element(By.ID, "privacyPolicy")

confirm_button = driver.find_element(By.XPATH, '//*[@id="registration_button"]')

submit_button = driver.find_elements(By.CLASS_NAME, "submitButton")

# ニックネームを入力
print("~~~~~~~~~~Nick Name Input ~~~~~~~~")
input_form(driver, By.ID, "registration-form-nname", nick_name)
# お名前を入力
print("~~~~~~~~~~Name Input ~~~~~~~~")
input_form(driver, By.ID, "registration-form-fname", name)
# お名前(カナ)を入力
print("~~~~~~~~~~Name Kana Input ~~~~~~~~")
input_form(driver, By.ID, "registration-form-kana", name_kana)
# 生年月日(年)を入力
print("~~~~~~~~~~Birth Year Input ~~~~~~~~")
input_form(driver, By.ID, "registration-form-birthdayyear", birth_year, is_selectbox=True)
# 生年月日(月)を入力
print("~~~~~~~~~~Birth Month Input ~~~~~~~~")
input_form(driver, By.ID, "registration-form-birthdaymonth", birth_month, is_selectbox=True)
# 生年月日(日)を入力
print("~~~~~~~~~~Birth Day Input ~~~~~~~~")
input_form(driver, By.ID, "registration-form-birthdayday", birth_day, is_selectbox=True)
# 性別を選択
print("~~~~~~~~~~Gender Select ~~~~~~~~~")
input_form(driver, By.NAME, "dwfrm_profile_customer_gender", gender_id, is_selectbox=True)
# 郵便番号を入力
print("~~~~~~~~~~Postcode Input ~~~~~~~~")
input_form(driver, By.ID, "registration-form-postcode", postcode)
# 住所(市区町村・番地)を入力
print("~~~~~~~~~~Street Address Input ~~~~~~~~")
input_form(driver, By.ID, "registration-form-address-line1", street_address)
# 住所(建物名・部屋番号)を入力
print("~~~~~~~~~~Building Input ~~~~~~~~")
input_form(driver, By.ID, "registration-form-address-line2", building)
# 電話番号を入力
print("~~~~~~~~~~Telephone Input ~~~~~~~~")
input_form(driver, By.NAME, "dwfrm_profile_customer_phone", tel)
# パスワードを入力
print("~~~~~~~~~~Password Input ~~~~~~~~")
input_form(driver, By.NAME, "dwfrm_profile_login_password", password)
# パスワード(確認)を入力
print("~~~~~~~~~~Confirm Password Input ~~~~~~~~")
input_form(driver, By.NAME, "dwfrm_profile_login_passwordconfirm", password)
# メルマガ受信希望にチェック
# print("~~~~~~~~~~Email Magazine Checkbox Click ~~~~~~~~")
# if not email_magazine_checkbox.is_selected():
#     email_magazine_checkbox.click()
#     time.sleep(2)
# 利用規約に同意にチェック
print("~~~~~~~~~~Terms Checkbox Click ~~~~~~~~")
terms_checkbox.send_keys(Keys.SPACE)
time.sleep(2)
# if not terms_checkbox.is_selected():
#     terms_checkbox.click()
#     time.sleep(2)
# プライバシーポリシーに同意にチェック
print("~~~~~~~~~~Privacy Policy Checkbox Click ~~~~~~~~")
policy_checkbox.send_keys(Keys.SPACE)
# if not policy_checkbox.is_selected():
#     policy_checkbox.click()
#     time.sleep(2)
# 確認ボタンをクリック
print("~~~~~~~~~~Confirm Button Click ~~~~~~~~")
confirm_button.send_keys(Keys.ENTER)
# confirm_button.click()
print("~~~~~~~~~~Confirm Button Clicked ~~~~~~~~")
time.sleep(10)
