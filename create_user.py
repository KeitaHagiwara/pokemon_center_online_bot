import time, random, json

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 自作モジュール
from scraping.ios.appium_utilities import AppiumUtilities
from utils.spreadsheet import SpreadsheetApiClient
from utils.gmail import extract_target_str_from_gmail_text_in_3min
from utils.common import get_column_number_by_alphabet
from utils.logger import display_logs
from config import SPREADSHEET_ID, SHEET_NAME

DEBUG_MODE = False
RETRY_LOOP = 3
MAX_RETRY_AUTH_LINK = 10
WRITE_COL = 'B'  # アカウント作成結果を書き込む列

ss = SpreadsheetApiClient()

def input_form(driver, selector_obj, selector_value, input_value, is_selectbox=False):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((selector_obj, selector_value))
        )
        # 要素を画面内にスクロール
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)

        if is_selectbox:
            select = Select(element)
            select.select_by_value(input_value)
        else:
            element.clear()
            element.send_keys(input_value)
        time.sleep(2)
    except (NoSuchElementException, TimeoutException) as e:
        print(f"要素が見つかりません: {selector_obj} - {e}")

def main(driver, appium_utils, user_info, log_callback=None):
    """新規ユーザー作成処理"""

    # IPアドレスの確認
    # driver.get("https://www.cman.jp/network/support/go_access.cgi")
    # time.sleep(5)

    try:

        display_logs(log_callback, "新規会員登録ページに移動中...")
        driver.get("https://www.pokemoncenter-online.com/login/")
        time.sleep(random.uniform(5, 10))

        # メールアドレスを入力して仮登録を実施する
        email = user_info["email"]
        display_logs(log_callback, f"メールアドレスを入力中...")
        email_form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'login-form-regist-email'))
        )
        email_form.send_keys(email)
        time.sleep(random.uniform(3, 5))

        display_logs(log_callback, "新規会員登録ボタンをクリック中...")
        user_register_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'form2Button'))
        )
        user_register_button.click()
        time.sleep(random.uniform(3, 5))

        # 仮登録メールを送信するボタンを押下する
        tmp_register_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, 'send-confirmation-email'))
        )
        tmp_register_button.click()
        time.sleep(random.uniform(3, 5))
        display_logs(log_callback, "✅ 仮登録が完了しました。メールを確認してください。")

        # 認証リンク付きメールを取得してクリックする
        for retry_i in range(MAX_RETRY_AUTH_LINK):
            search_keyword ="[ポケモンセンターオンライン]会員登録の手続きへ進む"
            auth_link = extract_target_str_from_gmail_text_in_3min(to_email=email, subject_keyword=search_keyword, email_type="auth_link")
            if auth_link:
                break
            time.sleep(15)

        # auth_link = "https://www.pokemoncenter-online.com/new-customer/?token=Jv8ySXf%2FGsaBOv8fEs7WdkO%2FVbWSVZBvq8aQgmTg9Ck%3D"
        # auth_linkのページへ遷移する
        display_logs(log_callback, "認証リンクのページに移動中...")
        driver.get(auth_link)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.TAG_NAME, "body")))
        display_logs(log_callback, "ページの読み込み完了")

        # お名前を入力
        display_logs(log_callback, "--- Name Input ---")
        input_form(driver, AppiumBy.ID, "registration-form-fname", user_info["name"])
        # お名前(カナ)を入力
        display_logs(log_callback, "--- Name Kana Input ---")
        input_form(driver, AppiumBy.ID, "registration-form-kana", user_info["name_kana"])
        # 生年月日(年)を入力
        display_logs(log_callback, "--- Birth Year Input ---")
        input_form(driver, AppiumBy.ID, "registration-form-birthdayyear", user_info["birth_year"], is_selectbox=True)
        # 生年月日(月)を入力
        display_logs(log_callback, "--- Birth Month Input ---")
        input_form(driver, AppiumBy.ID, "registration-form-birthdaymonth", user_info["birth_month"], is_selectbox=True)
        # 生年月日(日)を入力
        display_logs(log_callback, "--- Birth Day Input ---")
        input_form(driver, AppiumBy.ID, "registration-form-birthdayday", user_info["birth_day"], is_selectbox=True)
        # 郵便番号を入力
        display_logs(log_callback, "--- Postcode Input ---")
        input_form(driver, AppiumBy.ID, "registration-form-postcode", user_info["postcode"])
        # 住所(市区町村・番地)を入力
        display_logs(log_callback, "--- Street Address Input ---")
        input_form(driver, AppiumBy.ID, "registration-form-address-line1", user_info["street_address"])
        # 住所(建物名・部屋番号)を入力
        display_logs(log_callback, "--- Building Input ---")
        input_form(driver, AppiumBy.ID, "registration-form-address-line2", user_info["building"])
        # 電話番号を入力
        display_logs(log_callback, "--- Telephone Input ---")
        input_form(driver, AppiumBy.NAME, "dwfrm_profile_customer_phone", user_info["tel"])
        # パスワードを入力
        display_logs(log_callback, "--- Password Input ---")
        input_form(driver, AppiumBy.NAME, "dwfrm_profile_login_password", user_info["password"])
        # パスワード(確認)を入力
        display_logs(log_callback, "--- Confirm Password Input ---")
        input_form(driver, AppiumBy.NAME, "dwfrm_profile_login_passwordconfirm", user_info["password"])

        # メールマガジン「受け取らない」を選択
        email_magazine_no_radio = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, "input[type='radio'][name='dwfrm_profile_customer_addtoemaillist'][value='false']"))
        )
        # 要素を画面内にスクロール
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_magazine_no_radio)
        time.sleep(1)
        # JavaScriptでクリック
        driver.execute_script("arguments[0].click();", email_magazine_no_radio)
        time.sleep(2)

        # 利用規約に同意にチェック
        display_logs(log_callback, "--- Terms Checkbox Click ---")
        terms_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, "terms"))
        )
        terms_checkbox.send_keys(Keys.SPACE)
        time.sleep(2)

        # プライバシーポリシーに同意にチェック
        display_logs(log_callback, "--- Privacy Policy Checkbox Click ---")
        policy_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, "privacyPolicy"))
        )
        policy_checkbox.send_keys(Keys.SPACE)
        time.sleep(2)

        # 確認ボタンをクリック
        # FIXME: なぜかクリック完了しているのにエラーになることがあるため、try文で囲む
        display_logs(log_callback, "--- Confirm Button Click ---")
        try:
            confirm_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.ID, 'registration_button'))
            )
            confirm_button.send_keys(Keys.ENTER)
        except:
            pass
        time.sleep(5)

        # 登録ボタンをクリック
        display_logs(log_callback, "--- Submit Button Click ---")
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.CLASS_NAME, 'submitButton'))
            )
            submit_button.send_keys(Keys.ENTER)
        except:
            pass
        time.sleep(5)

        # 完了したかどうかをチェックする
        # FIXME: なぜかクリック完了しているのにエラーになることがあるため、try文で囲む
        if "会員登録が完了しました" in driver.page_source:
            display_logs(log_callback, "✅ 会員登録が完了しました。")
        else:
            display_logs(log_callback, "⚠️ 会員登録完了画面が表示されませんでした")
            return False

        write_col_number = get_column_number_by_alphabet(WRITE_COL)
        ss.write_to_cell(
            spreadsheet_id=SPREADSHEET_ID,
            sheet_name=SHEET_NAME,
            row=user_info["row_number"],
            column=write_col_number,
            value="済み"
        )
        return True  # 成功を返す

    except Exception as e:
        display_logs(log_callback, f"❌ エラーが発生しました: {e}")
        return False  # エラー時はFalseを返す

    finally:
        # 各ユーザー処理後に必ずブラウザキャッシュをクリア
        # （成功・失敗に関わらず実行、ドライバーは維持）
        if not DEBUG_MODE:
            try:
                display_logs(log_callback, "🔄 [finally] ブラウザキャッシュをクリア中...")
                appium_utils.delete_browser_page()
                time.sleep(2)
                display_logs(log_callback, "✅ [finally] ブラウザキャッシュをクリアしました")
            except Exception as e:
                display_logs(log_callback, f"⚠️ [finally] ブラウザキャッシュのクリアに失敗: {e}")
                # エラーが出ても処理は継続

def exec_create_new_accounts(start_row, end_row, log_callback=None):
    """UIから呼び出す用のラッパー関数"""

    display_logs(log_callback, "Appiumドライバーを初期化中...")
    appium_utils = AppiumUtilities()
    display_logs(log_callback, "Safariを起動しました")
    driver = appium_utils.driver

    for loop in range(RETRY_LOOP):
        all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)

        registration_user_info_list = ss.extract_registration_user_info(all_data, start_row, end_row)
        display_logs(log_callback=None, msg=json.dumps(registration_user_info_list, indent=2, ensure_ascii=False))
        display_logs(log_callback, "---------------")
        display_logs(log_callback, f"作成するユーザー数: {len(registration_user_info_list)}")
        display_logs(log_callback, "---------------")

        if not registration_user_info_list:
            print("決済対象ユーザーが存在しないため、処理を終了します。")
            break

        # ユーザー登録実行処理
        for user_info in registration_user_info_list:
            display_logs(log_callback, f"\nラベル: {user_info.get('label')}のユーザー情報の処理を開始します。")

            # ユーザー処理を実行（成功/失敗を受け取る）
            success = main(driver, appium_utils, user_info, log_callback)

            if success:
                display_logs(log_callback, f"✅ ユーザー {user_info.get('label')} の処理が完了しました\n")
            else:
                display_logs(log_callback, f"⚠️ ユーザー {user_info.get('label')} の処理に失敗しました。次のユーザーに進みます\n")

            # ユーザー間の待機時間
            time.sleep(random.uniform(3, 5))

        # 最低3分の待機時間を確保する
        if loop < RETRY_LOOP - 1:
            print("次のループまで3分間待機します...")
            time.sleep(180)

if __name__ == '__main__':

    START_ROW = 75
    END_ROW = 165

    print("Appiumドライバーを初期化中...")
    appium_utils = AppiumUtilities()
    print("Safariを起動しました")
    driver = appium_utils.driver

    for loop in range(RETRY_LOOP):
        print(f"{loop+1}回目の処理を開始します")

        # スプレッドシートの全データをDataFrame形式で取得
        all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)
        registration_user_info_list = ss.extract_registration_user_info(all_data, START_ROW, END_ROW)
        print(json.dumps(registration_user_info_list, indent=2, ensure_ascii=False))
        print("---------------")
        print(f"作成するユーザー数: {len(registration_user_info_list)}")
        print("---------------")
        if not registration_user_info_list:
            print("決済対象ユーザーが存在しないため、処理を終了します。")
            break

        # ユーザー登録実行処理
        for user_info in registration_user_info_list:
            main(driver, appium_utils, user_info)

        # 最低3分の待機時間を確保する
        if loop < RETRY_LOOP - 1:
            print("次のループまで3分間待機します...")
            time.sleep(180)