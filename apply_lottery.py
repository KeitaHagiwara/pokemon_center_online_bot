import time, random, json

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 自作モジュール
from scraping.ios.appium_utilities import AppiumUtilities
from utils.spreadsheet import SpreadsheetApiClient
from utils.common import get_column_number_by_alphabet
from utils.login import login_pokemon_center_online
from utils.logger import display_logs
from config import SPREADSHEET_ID, SHEET_NAME

DEBUG_MODE = False
RETRY_LOOP = 3
MAX_RETRY_PASSCODE = 10

# スプレッドシートの全データをDataFrame形式で取得
ss = SpreadsheetApiClient()


def main(driver, appium_utils, user_info, top_p=1, write_col='AA', log_callback=None):
    """抽選応募処理"""

    row_number = user_info["row_number"]
    email = user_info["email"]
    password = user_info["password"]
    target_product_name_dict = user_info.get("target_product_dict", {})

    display_logs(log_callback, f"===== ユーザー情報 =====")
    display_logs(log_callback, f"行番号: {row_number}")
    display_logs(log_callback, f"email: {email}")
    display_logs(log_callback, f"password: {password}")
    display_logs(log_callback, f"target_product_name_dict: {target_product_name_dict}")

    # IPアドレスの確認
    # driver.get("https://www.cman.jp/network/support/go_access.cgi")
    # time.sleep(5)

    try:

        # ログイン処理
        is_logged_in = login_pokemon_center_online(driver, appium_utils, email, password)
        if not is_logged_in:
            raise Exception("ログインに失敗しました")

        driver.get("https://www.pokemoncenter-online.com/lottery/apply.html")
        time.sleep(random.uniform(5, 10))

        for target_product_name, target_product_column in target_product_name_dict.items():
            display_logs(log_callback, f"\n=== 抽選結果確認対象商品: {target_product_name} ===")

            for index in range(5):
                try:
                    # 商品名が一致して、かつ受付中の抽選かをチェックする
                    product_names = appium_utils.safe_find_elements(AppiumBy.CSS_SELECTOR, 'div.lBox > p', attempt=index)
                    lottery_labels = lottery_fields = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'ttl', attempt=index)
                    product_name = product_names[index]
                    lottery_label = lottery_labels[index]

                    display_logs(log_callback, f"対象商品: {product_name.get_attribute('innerText')}")
                    display_logs(log_callback, lottery_label.get_attribute("innerText"))
                    # 該当の商品名で受付中ではない場合はスキップする
                    if lottery_label.get_attribute("innerText") != "受付中" or product_name.get_attribute("innerText") != target_product_name:
                        display_logs(log_callback, f"❌ {index+1}個目の商品は受付中の抽選ではありません")
                        continue

                    else:
                        # 1. lottery_fieldsを安全に取得
                        display_logs(log_callback, f"\n=== lottery_field[{index}]の取得を開始 ===")
                        lottery_fields = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'subDl')
                        if not lottery_fields or len(lottery_fields) <= index:
                            display_logs(log_callback, f"lottery_field[{index}]が見つかりませんでした")
                            # 代替セレクタも試す
                            display_logs(log_callback, "代替セレクタで再試行...")
                            lottery_fields = appium_utils.safe_find_elements(AppiumBy.TAG_NAME, 'dl', attempt=index) or appium_utils.safe_find_elements(AppiumBy.XPATH, "//*[contains(@class, 'accordion') or contains(@class, 'toggle') or contains(@class, 'collaps')]", attempt=index)
                            if not lottery_fields or len(lottery_fields) <= index:
                                continue

                        display_logs(log_callback, f"見つかった要素数: {len(lottery_fields)}")
                        lottery_field = lottery_fields[index]

                        # アコーディオン「詳しく見る」を開く
                        display_logs(log_callback, f"\n=== アコーディオン「詳しく見る」を開く ===")
                        if not appium_utils.open_accordion(lottery_field, f"lottery_field[{index}]"):
                            display_logs(log_callback, f"❌ アコーディオンを開けませんでした。次の抽選へ")
                            continue

                        display_logs(log_callback, "✅ アコーディオンを開きました")
                        time.sleep(random.uniform(1, 3))  # アニメーション完了まで待機

                        # 2. radioボタンを安全に取得してクリック
                        display_logs(log_callback, "抽選対象の商品チェックボックスを取得中...")
                        item_checkboxes = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'radio', attempt=index)
                        if not appium_utils.safe_click(item_checkboxes, 0, "radioボタン"):
                            raise ValueError("商品選択のラジオボタンのクリックに失敗しました")

                        time.sleep(random.uniform(1, 3))

                        # 3. 同意チェックボックスを安全に取得してクリック
                        display_logs(log_callback, "同意チェックボックスを取得中...")
                        agree_checkboxes = appium_utils.safe_find_elements(
                            AppiumBy.CSS_SELECTOR,
                            '.agreementArea > .checkboxWrapper > [type="checkbox"]',
                            attempt=index
                        )
                        if not agree_checkboxes or len(agree_checkboxes) == 0:
                            raise ValueError("同意チェックボックスが見つかりませんでした")

                        agree_checkbox = agree_checkboxes[0]
                        display_logs(log_callback, f"同意チェックボックスを発見: {agree_checkbox.get_attribute('id')}")
                        agree_checkbox.click()
                        time.sleep(random.uniform(1, 3))

                        # 4. モーダル開くボタンを安全にクリック
                        display_logs(log_callback, "モーダル開くボタンをクリック中...")
                        apply_buttons = appium_utils.safe_find_elements(
                            AppiumBy.CSS_SELECTOR,
                            '.popup-modal.on',
                            attempt=index
                        )
                        if apply_buttons[0].get_attribute("innerText") == "キャンセルする":
                            raise ValueError("既に応募済みの可能性があります")

                        display_logs(log_callback, "応募するボタンをクリック中...")
                        apply_buttons[0].click()
                        display_logs(log_callback, "✅ 応募するボタンをクリックしました")

                        time.sleep(random.uniform(1, 3))

                        # 5. 申し込みボタンを安全にクリック
                        display_logs(log_callback, "申し込みボタンをクリック中...")
                        if appium_utils.wait_and_click_element(AppiumBy.ID, 'applyBtn'):
                            display_logs(log_callback, "✅ 申し込みボタンをクリックしました")
                        else:
                            display_logs(log_callback, "❌ 申し込みボタンのクリックに失敗しました")
                            continue

                        # 6. 受付が完了したかチェックする
                        lottery_labels = lottery_fields = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'ttl', attempt=index)
                        lottery_label = lottery_labels[index]
                        display_logs(log_callback, lottery_label.get_attribute("innerText"))
                        if lottery_label.get_attribute("innerText") != "受付完了":
                            # スプレッドシートに結果を書き込む
                            ss.write_to_cell(
                                spreadsheet_id=SPREADSHEET_ID,
                                sheet_name=SHEET_NAME,
                                row=row_number,
                                column=target_product_column,
                                value="応募済み"
                            )

                            time.sleep(random.uniform(3, 5))
                            display_logs(log_callback, f"🎉 抽選申し込み完了!")

                            # 抽選申し込みが完了したら次の抽選へ
                            break

                except ValueError as ve:
                    display_logs(log_callback, f"❌ {ve}")

                except Exception as e:
                    display_logs(log_callback, f"❌ 抽選申し込み「{target_product_name}」でエラーが発生: {e}")

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

def exec_apply_lottery(start_row, end_row, write_col, top_p, log_callback=None):
    """UIから呼び出す用のラッパー関数"""

    display_logs(log_callback, "Appiumドライバーを初期化中...")
    appium_utils = AppiumUtilities()
    display_logs(log_callback, "Safariを起動しました")
    driver = appium_utils.driver

    for loop in range(RETRY_LOOP):
        display_logs(log_callback, f"{loop+1}回目の処理を開始します")

        # スプレッドシートの全データをDataFrame形式で取得
        all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)
        user_info_list = ss.extract_apply_lottery_user_info(all_data, start_row, end_row, write_col, top_p, 'apply_lottery')

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
            main(driver, appium_utils, user_info, top_p, write_col, log_callback)

        # 最低3分の待機時間を確保する
        display_logs(log_callback, "次のループまで3分間待機します...")
        time.sleep(180)


if __name__ == '__main__':
    TOP_P = 1 # 抽選申し込みを行う上位件件数
    WRITE_COL = 'AD'  # 抽選申し込み結果を書き込む列

    START_ROW = 61
    END_ROW = 89

    print("Appiumドライバーを初期化中...")
    appium_utils = AppiumUtilities()
    print("Safariを起動しました")
    driver = appium_utils.driver

    for loop in range(RETRY_LOOP):
        print(f"{loop+1}回目の処理を開始します")

        # スプレッドシートの全データをDataFrame形式で取得
        all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)
        user_info_list = ss.extract_apply_lottery_user_info(all_data, START_ROW, END_ROW, WRITE_COL, TOP_P, 'apply_lottery')
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
            main(driver, appium_utils, user_info, TOP_P, WRITE_COL)

        # 最低3分の待機時間を確保する
        print("次のループまで3分間待機します...")
        time.sleep(180)
