import time, random, json
from datetime import datetime

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 自作モジュール
from scraping.ios.appium_utilities import AppiumUtilities
from utils.spreadsheet import SpreadsheetApiClient
from utils.login import login_pokemon_center_online
from config import SPREADSHEET_ID, SHEET_NAME

DEBUG_MODE = False
RETRY_LOOP = 3
MAX_RETRY_PASSCODE = 20


def main(driver, appium_utils, user_info, target_product_name_dict):
    """メイン処理"""

    row_number = user_info["row_number"]
    email = user_info["email"]
    password = user_info["password"]
    print(f"email: {email}")
    print(f"password: {password}")

    # IPアドレスの確認
    driver.get("https://www.cman.jp/network/support/go_access.cgi")
    time.sleep(3)

    try:

        # ログイン処理
        is_logged_in = login_pokemon_center_online(driver, email, password)
        if not is_logged_in:
            raise Exception("ログインに失敗しました")

        driver.get("https://www.pokemoncenter-online.com/lottery-history/")
        time.sleep(random.uniform(5, 10))

        target_lottery_result = None

        for target_product_name, target_product_column in target_product_name_dict.items():
            print(f"\n=== 抽選結果確認対象商品: {target_product_name} ===")

            for index in range(5):
                print(f"抽選結果を取得します (index={index})")

                try:
                    # 対象の商品かをチェックする
                    product_names = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'ttl', attempt=index)
                    product_name = product_names[index]
                    print(product_name.get_attribute("innerText"))
                    if target_product_name not in product_name.get_attribute("innerText"):
                        print(f"❌ {index+1}個目の商品は、今回の結果取得対象の抽選ではありません")
                        continue
                    else:
                        print(f"✅ {index+1}個目の商品は、今回の結果取得対象の抽選です")
                        # 抽選結果を安全に取得
                        lottery_results = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'txtBox01', attempt=index)
                        target_lottery_result = lottery_results[index].get_attribute('innerText')

                        print(f"抽選結果: {target_lottery_result}")
                        # 抽選結果が「当選」の場合のみスプレッドシートに書き込む
                        # if check_result == "当選":
                        ss.write_to_cell(
                            spreadsheet_id=SPREADSHEET_ID,
                            sheet_name=SHEET_NAME,
                            row=row_number,
                            column=target_product_column,
                            value=target_lottery_result
                        )
                        break

                except ValueError as ve:
                    print(f"❌ {ve}")

                except Exception as e:
                    print(f"❌ 抽選申し込み {index + 1} でエラーが発生: {e}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    finally:
        # ドライバーを終了
        if not DEBUG_MODE:
            print("\nドライバーを終了中...")
            appium_utils.delete_browser_page()
            time.sleep(5)
            print("完了しました")
        else:
            pass

if __name__ == '__main__':

    WRITE_COL = 'Z'  # 抽選申し込み結果を書き込む列
    TOP_P = 2 # 抽選申し込みを行う上位件件数

    START_ROW = 4
    END_ROW = 87

    # スプレッドシートからユーザー情報を取得する
    ss = SpreadsheetApiClient()

    for loop in range(RETRY_LOOP):
        print(f"{loop}回目の処理を開始します")

        # スプレッドシートの全データをDataFrame形式で取得
        all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)

        user_info_list = ss.extract_apply_lottery_user_info(all_data, START_ROW, END_ROW, WRITE_COL, TOP_P, 'check_results')
        print(json.dumps(user_info_list, indent=2, ensure_ascii=False))
        print("---------------")
        print(f"合計ユーザー数: {len(user_info_list)}")
        print("---------------")

        print("Appiumドライバーを初期化中...")
        appium_utils = AppiumUtilities()

        print("Safariを起動しました")

        driver = appium_utils.driver


        target_product_name_dict = ss.get_check_target_product_name_dict(all_data, WRITE_COL, TOP_P)
        print(f"確認対象商品名: {target_product_name_dict}")
        if not target_product_name_dict:
            raise Exception("確認対象商品名が取得できなかったため、処理を中止します。")


        for user_info in user_info_list:
            if not user_info.get("email") or not user_info.get("password"):
                print(f"❌ emailまたはpasswordが未設定のためスキップします: {user_info}")
                continue

            main(driver, appium_utils, user_info, target_product_name_dict)

        # 最低3分の待機時間を確保する
        print("次のループまで3分間待機します...")
        time.sleep(180)
