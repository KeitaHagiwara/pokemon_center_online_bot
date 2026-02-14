import time, random, json
from datetime import datetime

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 自作モジュール
from scraping.ios.appium_utilities import AppiumUtilities
from utils.spreadsheet import SpreadsheetApiClient
from utils.login import login_pokemon_center_online
from utils.logger import display_logs
from config import SPREADSHEET_ID, SHEET_NAME

DEBUG_MODE = False
RETRY_LOOP = 3
MAX_RETRY_PASSCODE = 20

# スプレッドシートクライアントを定義する
ss = SpreadsheetApiClient()

def main(driver, appium_utils, user_info, log_callback=None):
    """メイン処理"""

    row_number = user_info["row_number"]
    email = user_info["email"]
    password = user_info["password"]
    target_product_name_dict = user_info.get("target_product_dict", {})

    display_logs(log_callback, f"===== ユーザー情報 =====")
    display_logs(log_callback, f"email: {email}")
    display_logs(log_callback, f"password: {password}")
    display_logs(log_callback, f"target_product_name_dict: {target_product_name_dict}")

    # IPアドレスの確認
    # driver.get("https://www.cman.jp/network/support/go_access.cgi")
    # time.sleep(3)

    try:

        # ログイン処理
        is_logged_in = login_pokemon_center_online(driver, appium_utils, email, password)
        if not is_logged_in:
            raise Exception("ログインに失敗しました")

        driver.get("https://www.pokemoncenter-online.com/order-history/")
        time.sleep(random.uniform(5, 10))

        target_shipping_result = None

        for target_product_name, target_product_column in target_product_name_dict.items():
            display_logs(log_callback, f"\n=== 発送ステータス確認対象商品: {target_product_name} ===")

            for index in range(5):
                display_logs(log_callback, f"ステータスを取得します (index={index})")

                try:
                    # 対象の商品かをチェックする
                    product_names = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'ttl', attempt=index)
                    product_name = product_names[index]
                    display_logs(log_callback, product_name.get_attribute("innerText"))
                    if target_product_name not in product_name.get_attribute("innerText"):
                        display_logs(log_callback, f"❌ {index+1}個目の商品は、今回の結果取得対象の商品ではありません")
                        continue
                    else:
                        display_logs(log_callback, f"✅ {index+1}個目の商品は、今回の結果取得対象の商品です")
                        # キャンセル済みになっているかチェック
                        if "キャンセル済み" in driver.page_source:
                            display_logs(log_callback, f"❌ {index+1}個目の商品はキャンセル済みです。")
                            target_shipping_result = "キャンセル済み"
                        else:
                            # 発送ステータスを安全に取得
                            shipping_status = appium_utils.safe_find_elements(AppiumBy.CSS_SELECTOR, '.comReceiptBox .txtList li.finish', attempt=index)
                            display_logs(log_callback, shipping_status)
                            target_shipping_result = shipping_status[index].get_attribute('innerText')

                        display_logs(log_callback, f"発送ステータス: {target_shipping_result}")
                        # 発送ステータスをスプレッドシートに書き込む
                        ss.write_to_cell(
                            spreadsheet_id=SPREADSHEET_ID,
                            sheet_name=SHEET_NAME,
                            row=row_number,
                            column=target_product_column,
                            value=target_shipping_result
                        )
                        display_logs(log_callback, f"✅ 発送ステータスを書き込みました: {target_shipping_result}")
                        break

                except ValueError as ve:
                    display_logs(log_callback, f"❌ {ve}")

                except Exception as e:
                    display_logs(log_callback, f"❌ 発送ステータス確認 {index + 1} でエラーが発生: {e}")

    except Exception as e:
        display_logs(log_callback, f"エラーが発生しました: {e}")

    finally:
        # ドライバーを終了
        if not DEBUG_MODE:
            display_logs(log_callback, "\nドライバーを終了中...")
            appium_utils.delete_browser_page()
            time.sleep(5)
            display_logs(log_callback, "完了しました")
        else:
            pass

def exec_check_shipping_status(start_row, end_row, write_col, top_p, log_callback=None):
    """UIから呼び出す用のラッパー関数"""

    # スプレッドシートの全データをDataFrame形式で取得
    all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)

    user_info_list = ss.extract_apply_lottery_user_info(all_data, start_row, end_row, write_col, top_p, extract_type='check_shipping_status')
    display_logs(log_callback=None, msg=json.dumps(user_info_list, indent=2, ensure_ascii=False))
    display_logs(log_callback, msg="---------------")
    display_logs(log_callback, msg=f"合計ユーザー数: {len(user_info_list)}")
    display_logs(log_callback, msg="---------------")

    display_logs(log_callback=log_callback, msg="Appiumドライバーを初期化中...")
    appium_utils = AppiumUtilities()

    display_logs(log_callback, msg="Safariを起動しました")
    display_logs(log_callback, msg="")

    driver = appium_utils.driver

    for user_info in user_info_list:
        display_logs(log_callback, msg=f"ラベル: {user_info.get('label')}のユーザー情報の処理を開始します。")
        if not user_info.get("email") or not user_info.get("password"):
            display_logs(log_callback, msg=f"❌ emailまたはpasswordが未設定のためスキップします: {user_info}")
            continue

        main(driver, appium_utils, user_info, log_callback)


if __name__ == '__main__':
    # debug用にテスト実行したい場合にこちらを利用する
    # loggerは使わずにprintで出力する

    WRITE_COL = 'Y'  # 発送ステータスを書き込む列
    TOP_P = 3 # 発送ステータスを確認する上位件数

    START_ROW = 27
    END_ROW = 87

    # for loop in range(RETRY_LOOP):
    #     print(f"{loop+1}回目の処理を開始します")

    # スプレッドシートの全データをDataFrame形式で取得
    all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)

    user_info_list = ss.extract_apply_lottery_user_info(all_data, START_ROW, END_ROW, WRITE_COL, TOP_P, 'check_shipping_status')
    print(json.dumps(user_info_list, indent=2, ensure_ascii=False))
    print("---------------")
    print(f"合計ユーザー数: {len(user_info_list)}")
    print("---------------")

    print("Appiumドライバーを初期化中...")
    appium_utils = AppiumUtilities()

    print("Safariを起動しました")

    driver = appium_utils.driver

    for user_info in user_info_list:
        if not user_info.get("email") or not user_info.get("password"):
            print(f"❌ emailまたはpasswordが未設定のためスキップします: {user_info}")
            continue

        main(driver, appium_utils, user_info)
