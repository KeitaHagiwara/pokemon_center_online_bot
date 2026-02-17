import time, random, json

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 自作モジュール
from scraping.ios.appium_utilities import AppiumUtilities
from utils.spreadsheet import SpreadsheetApiClient
from utils.login import login_pokemon_center_online
from utils.common import get_column_number_by_alphabet
from utils.logger import display_logs
from config import SPREADSHEET_ID, SHEET_NAME

DEBUG_MODE = False
RETRY_LOOP = 3
MAX_RETRY_PASSCODE = 10

# スプレッドシートからユーザー情報を取得する
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
    """クレカ変更処理"""

    row_number = user_info["row_number"]
    email = user_info["email"]
    password = user_info["password"]

    display_logs(log_callback, "===== ユーザー情報 =====")
    display_logs(log_callback, f"行番号: {row_number}")
    display_logs(log_callback, f"email: {email}")
    display_logs(log_callback, f"password: {password}")

    # IPアドレスの確認
    # driver.get("https://www.cman.jp/network/support/go_access.cgi")
    # time.sleep(5)

    try:

        # ログイン処理
        is_logged_in = login_pokemon_center_online(driver, appium_utils, email, password)
        if not is_logged_in:
            raise Exception("ログインに失敗しました")


        # 会員情報変更ページに遷移
        display_logs(log_callback, "--- クレジットカード登録・変更画面へ遷移 ---")
        driver.get("https://www.pokemoncenter-online.com/payment/")
        time.sleep(random.uniform(3, 5))

        # カード名義人を入力
        display_logs(log_callback, "--- Cardholder Name Input ---")
        input_form(driver, AppiumBy.ID, "cardOwner", user_info["meigi"])
        # カード番号を入力
        display_logs(log_callback, "--- Card Number Input ---")
        input_form(driver, AppiumBy.ID, "cardNumber", user_info["credit_card_no"])
        # 有効期限を入力
        display_logs(log_callback, "--- Expiration Date Input ---")
        expiration_month, expiration_year = user_info["day_of_expiry"].split("/")
        input_form(driver, AppiumBy.ID, "expirationMonth", expiration_month) # 月
        input_form(driver, AppiumBy.ID, "expirationYear", expiration_year[2:]) # 年(下2桁)
        # セキュリティコードを入力
        display_logs(log_callback, "--- Security Code Input ---")
        input_form(driver, AppiumBy.ID, "securityCode", user_info["security_code"])

        # 入力内容確認へ進むボタンをクリック
        display_logs(log_callback, "--- Confirm Button Click ---")
        try:
            confirm_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.CLASS_NAME, 'paymentsubmit'))
            )
            confirm_button.send_keys(Keys.ENTER)
        except:
            pass
        time.sleep(5)

        # # 会員情報確認の画面が表示されたら、登録ボタンをクリック
        # if "会員情報確認" in driver.page_source:
        #     # 登録ボタンをクリック
        #     display_logs(log_callback, "--- Submit Button Click ---")
        #     try:
        #         submit_button = WebDriverWait(driver, 10).until(
        #             EC.presence_of_element_located((AppiumBy.CLASS_NAME, 'submitButton'))
        #         )
        #         submit_button.send_keys(Keys.ENTER)
        #     except:
        #         pass
        #     time.sleep(5)

        #     # 変更完了が確定したら、結果をスプレッドシートに書き込む
        #     if "変更完了" in driver.page_source and "/regist-complete/" in driver.current_url:
        #         display_logs(log_callback, "クレカ変更が完了しました")

        #         # E列（クレカ変更済みフラグ）に「済み」と書き込む
        #         write_col_number = get_column_number_by_alphabet("E")
        #         ss.write_to_cell(
        #             spreadsheet_id=SPREADSHEET_ID,
        #             sheet_name=SHEET_NAME,
        #             row=user_info["row_number"],
        #             column=write_col_number,
        #             value="済み"
        #         )

    except Exception as e:
        display_logs(log_callback, f"エラーが発生しました: {e}")

    finally:
        if not DEBUG_MODE:
            # ドライバーを終了
            display_logs(log_callback, "\nドライバーを終了中...")
            appium_utils.delete_browser_page()
            time.sleep(5)
            display_logs(log_callback, "完了しました")
        else:
            pass

def exec_change_payment_info(start_row, end_row, log_callback=None):

    display_logs(log_callback, "Appiumドライバーを初期化中...")
    appium_utils = AppiumUtilities()
    display_logs(log_callback, "Safariを起動しました")
    driver = appium_utils.driver

    for loop in range(RETRY_LOOP):
        # スプレッドシートの全データをDataFrame形式で取得
        all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)
        user_info_list = ss.extract_change_user_info(all_data, start_row, end_row, change_type='payment')

        display_logs(log_callback=None, msg=json.dumps(user_info_list, indent=2, ensure_ascii=False))
        display_logs(log_callback, "---------------")
        display_logs(log_callback, f"合計ユーザー数: {len(user_info_list)}")
        display_logs(log_callback, "---------------")
        if not user_info_list:
            display_logs(log_callback, "クレカ変更対象ユーザーが存在しないため、処理を終了します。")
            return

        for user_info in user_info_list:
            display_logs(log_callback, msg=f"ラベル: {user_info.get('label')}のユーザー情報の処理を開始します。")
            if not user_info.get("email") or not user_info.get("password"):
                display_logs(log_callback, f"❌ emailまたはpasswordが未設定のためスキップします: {user_info}")
                continue
            main(driver, appium_utils, user_info, log_callback)

        # 最低3分の待機時間を確保する
        print("次のループまで3分間待機します...")
        time.sleep(180)


if __name__ == '__main__':

    START_ROW = 4
    END_ROW = 50

    print("Appiumドライバーを初期化中...")
    appium_utils = AppiumUtilities()
    print("Safariを起動しました")
    driver = appium_utils.driver

    for loop in range(RETRY_LOOP):
        print(f"{loop+1}回目の処理を開始します")

        # スプレッドシートの全データをDataFrame形式で取得
        all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)
        user_info_list = ss.extract_change_user_info(all_data, START_ROW, END_ROW, change_type='payment')

        print(json.dumps(user_info_list, indent=2, ensure_ascii=False))
        print("---------------")
        print(f"合計ユーザー数: {len(user_info_list)}")
        print("---------------")
        if not user_info_list:
            print("クレカ変更対象ユーザーが存在しないため、処理を終了します。")
            break

        for user_info in user_info_list:
            if not user_info.get("email") or not user_info.get("password"):
                print(f"❌ emailまたはpasswordが未設定のためスキップします: {user_info}")
                continue
            main(driver, appium_utils, user_info)

        # 最低3分の待機時間を確保する
        print("次のループまで3分間待機します...")
        time.sleep(180)
