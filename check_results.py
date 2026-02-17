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

# スプレッドシートの全データをDataFrame形式で取得
ss = SpreadsheetApiClient()

def main(driver, appium_utils, user_info, log_callback=None):
    """メイン処理"""

    row_number = user_info["row_number"]
    email = user_info["email"]
    password = user_info["password"]
    target_product_name_dict = user_info.get("target_product_dict", {})

    display_logs(log_callback, f"===== ユーザー情報 =====")
    display_logs(log_callback, f"行番号: {row_number}")
    display_logs(log_callback, f"email: {email}")
    display_logs(log_callback, f"password: {password}")
    display_logs(log_callback, f"target_product_name_dict: {target_product_name_dict}")

    # # IPアドレスの確認
    # driver.get("https://www.cman.jp/network/support/go_access.cgi")
    # time.sleep(3)

    try:

        # ログイン処理
        is_logged_in = login_pokemon_center_online(driver, appium_utils, email, password)
        if not is_logged_in:
            raise Exception("ログインに失敗しました")

        driver.get("https://www.pokemoncenter-online.com/lottery-history/")
        time.sleep(random.uniform(5, 10))

        target_lottery_result = None

        for target_product_name, target_product_column in target_product_name_dict.items():
            display_logs(log_callback, f"\n=== 抽選結果確認対象商品: {target_product_name} ===")

            for index in range(5):
                display_logs(log_callback, f"抽選結果を取得します (index={index})")

                try:
                    # 対象の商品かをチェックする
                    product_names = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'ttl', attempt=index)
                    product_name = product_names[index]
                    display_logs(log_callback, product_name.get_attribute("innerText"))
                    if target_product_name not in product_name.get_attribute("innerText"):
                        display_logs(log_callback, f"❌ {index+1}個目の商品は、今回の結果取得対象の抽選ではありません")
                        continue
                    else:
                        display_logs(log_callback, f"✅ {index+1}個目の商品は、今回の結果取得対象の抽選です")
                        # 抽選結果を安全に取得
                        lottery_results = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'txtBox01', attempt=index)
                        target_lottery_result = lottery_results[index].get_attribute('innerText')
                        target_lottery_result = "応募済み" if target_lottery_result == "応募中" else target_lottery_result

                        display_logs(log_callback, f"抽選結果: {target_lottery_result}")
                        # 抽選結果が「当選」の場合のみスプレッドシートに書き込む
                        # if check_result == "当選":
                        ss.write_to_cell(
                            spreadsheet_id=SPREADSHEET_ID,
                            sheet_name=SHEET_NAME,
                            row=row_number,
                            column=target_product_column,
                            value=target_lottery_result
                        )
                        display_logs(log_callback, f"✅ 抽選結果を書き込みました: {target_lottery_result}")
                        break

                except ValueError as ve:
                    display_logs(log_callback, f"❌ {ve}")
                except Exception as e:
                    display_logs(log_callback, f"❌ 抽選申し込み {index + 1} でエラーが発生: {e}")

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

def exec_check_results(start_row, end_row, write_col, top_p, log_callback=None):
    """UIから呼び出す用のラッパー関数"""

    display_logs(log_callback, "Appiumドライバーを初期化中...")
    appium_utils = AppiumUtilities()
    display_logs(log_callback, "Safariを起動しました")
    driver = appium_utils.driver

    for loop in range(RETRY_LOOP):
        display_logs(log_callback, f"{loop+1}回目の処理を開始します")

        # スプレッドシートの全データをDataFrame形式で取得
        all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)

        user_info_list = ss.extract_apply_lottery_user_info(all_data, start_row, end_row, write_col, top_p, 'check_results')
        display_logs(log_callback=None, msg=json.dumps(user_info_list, indent=2, ensure_ascii=False))
        display_logs(log_callback, "---------------")
        display_logs(log_callback, f"合計ユーザー数: {len(user_info_list)}")
        display_logs(log_callback, "---------------")
        if not user_info_list:
            display_logs(log_callback, "決済対象ユーザーが存在しないため、処理を終了します。")
            break

        for user_info in user_info_list:
            display_logs(log_callback, msg=f"ラベル: {user_info.get('label')}のユーザー情報の処理を開始します。")
            if not user_info.get("email") or not user_info.get("password"):
                display_logs(log_callback, f"❌ emailまたはpasswordが未設定のためスキップします: {user_info}")
                continue

            main(driver, appium_utils, user_info, log_callback)

        # 最低3分の待機時間を確保する
        display_logs(log_callback, "次のループまで3分間待機します...")
        time.sleep(180)

if __name__ == '__main__':

    WRITE_COL = 'Z'  # 抽選申し込み結果を書き込む列
    TOP_P = 2 # 抽選申し込みを行う上位件件数

    START_ROW = 4
    END_ROW = 87

    print("Appiumドライバーを初期化中...")
    appium_utils = AppiumUtilities()
    print("Safariを起動しました")
    driver = appium_utils.driver

    for loop in range(RETRY_LOOP):
        print(f"{loop+1}回目の処理を開始します")

        # スプレッドシートの全データをDataFrame形式で取得
        all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)

        user_info_list = ss.extract_apply_lottery_user_info(all_data, START_ROW, END_ROW, WRITE_COL, TOP_P, 'check_results')
        print(json.dumps(user_info_list, indent=2, ensure_ascii=False))
        print("---------------")
        print(f"合計ユーザー数: {len(user_info_list)}")
        print("---------------")
        if not user_info_list:
            print("決済対象ユーザーが存在しないため、処理を終了します。")
            break

        for user_info in user_info_list:
            if not user_info.get("email") or not user_info.get("password"):
                print(f"❌ emailまたはpasswordが未設定のためスキップします: {user_info}")
                continue

            main(driver, appium_utils, user_info)

        # 最低3分の待機時間を確保する
        print("次のループまで3分間待機します...")
        time.sleep(180)
