import time, random, json

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 自作モジュール
from scraping.ios.appium_utilities import AppiumUtilities
from utils.spreadsheet import SpreadsheetApiClient
from utils.common import get_column_number_by_alphabet
from utils.login import login_pokemon_center_online
from config import SPREADSHEET_ID, SHEET_NAME

DEBUG_MODE = False
RETRY_LOOP = 3
MAX_RETRY_PASSCODE = 10


def main(driver, appium_utils, user_info, top_p=1, write_col='AA'):
    """抽選応募処理"""

    # スプレッドシートクライアントを定義する
    ss = SpreadsheetApiClient()

    row_number = user_info["row_number"]
    email = user_info["email"]
    password = user_info["password"]

    print(f"===== ユーザー情報 =====")
    print(f"行番号: {row_number}")
    print(f"email: {email}")
    print(f"password: {password}")

    # IPアドレスの確認
    # driver.get("https://www.cman.jp/network/support/go_access.cgi")
    # time.sleep(5)

    try:

        # ログイン処理
        is_logged_in = login_pokemon_center_online(driver, email, password)
        if not is_logged_in:
            raise Exception("ログインに失敗しました")

        driver.get("https://www.pokemoncenter-online.com/lottery/apply.html")
        time.sleep(random.uniform(3, 5))

        for index in range(top_p):
            print(f"抽選申し込み処理を開始します (index={index})")

            try:
                # 受付中の抽選かをチェックする
                lottery_labels = lottery_fields = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'ttl', attempt=index)
                lottery_label = lottery_labels[index]
                print(lottery_label.get_attribute("innerText"))
                if lottery_label.get_attribute("innerText") != "受付中":
                    print(f"❌ {index+1}個目の商品は受付中の抽選ではありません")
                    continue

                # 1. lottery_fieldsを安全に取得
                print(f"\n=== lottery_field[{index}]の取得を開始 ===")
                lottery_fields = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'subDl')
                if not lottery_fields or len(lottery_fields) <= index:
                    print(f"lottery_field[{index}]が見つかりませんでした")
                    # 代替セレクタも試す
                    print("代替セレクタで再試行...")
                    lottery_fields = appium_utils.safe_find_elements(AppiumBy.TAG_NAME, 'dl', attempt=index) or appium_utils.safe_find_elements(AppiumBy.XPATH, "//*[contains(@class, 'accordion') or contains(@class, 'toggle') or contains(@class, 'collaps')]", attempt=index)
                    if not lottery_fields or len(lottery_fields) <= index:
                        continue

                print(f"見つかった要素数: {len(lottery_fields)}")
                lottery_field = lottery_fields[index]

                # アコーディオン「詳しく見る」を開く
                print(f"\n=== アコーディオン「詳しく見る」を開く ===")
                if not appium_utils.open_accordion(lottery_field, f"lottery_field[{index}]"):
                    print(f"❌ アコーディオンを開けませんでした。次の抽選へ")
                    continue

                print("✅ アコーディオンを開きました")
                time.sleep(random.uniform(1, 3))  # アニメーション完了まで待機

                # 2. radioボタンを安全に取得してクリック
                print("抽選対象の商品チェックボックスを取得中...")
                item_checkboxes = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'radio', attempt=index)
                if not appium_utils.safe_click(item_checkboxes, 0, "radioボタン"):
                    raise ValueError("商品選択のラジオボタンのクリックに失敗しました")

                time.sleep(random.uniform(1, 3))

                # 3. 同意チェックボックスを安全に取得してクリック
                print("同意チェックボックスを取得中...")
                agree_checkboxes = appium_utils.safe_find_elements(
                    AppiumBy.CSS_SELECTOR,
                    '.agreementArea > .checkboxWrapper > [type="checkbox"]',
                    attempt=index
                )
                if not agree_checkboxes or len(agree_checkboxes) == 0:
                    raise ValueError("同意チェックボックスが見つかりませんでした")

                agree_checkbox = agree_checkboxes[0]
                print(f"同意チェックボックスを発見: {agree_checkbox.get_attribute('id')}")
                agree_checkbox.click()
                time.sleep(random.uniform(1, 3))

                # 4. モーダル開くボタンを安全にクリック
                print("モーダル開くボタンをクリック中...")
                apply_buttons = appium_utils.safe_find_elements(
                    AppiumBy.CSS_SELECTOR,
                    '.popup-modal.on',
                    attempt=index
                )
                if apply_buttons[0].get_attribute("innerText") == "キャンセルする":
                    raise ValueError("既に応募済みの可能性があります")

                print("応募するボタンをクリック中...")
                apply_buttons[0].click()
                print("✅ 応募するボタンをクリックしました")

                time.sleep(random.uniform(1, 3))

                # 5. 申し込みボタンを安全にクリック
                print("申し込みボタンをクリック中...")
                if appium_utils.wait_and_click_element(AppiumBy.ID, 'applyBtn'):
                    print("✅ 申し込みボタンをクリックしました")
                else:
                    print("❌ 申し込みボタンのクリックに失敗しました")
                    continue

                # 6. 受付が完了したかチェックする
                lottery_labels = lottery_fields = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'ttl', attempt=index)
                lottery_label = lottery_labels[index]
                print(lottery_label.get_attribute("innerText"))
                if lottery_label.get_attribute("innerText") != "受付完了":
                    # スプレッドシートに結果を書き込む
                    write_col_number = get_column_number_by_alphabet(write_col) + index
                    ss.write_to_cell(
                        spreadsheet_id=SPREADSHEET_ID,
                        sheet_name=SHEET_NAME,
                        row=row_number,
                        column=write_col_number,
                        value="応募済み"
                    )

                    time.sleep(random.uniform(3, 5))
                    print(f"🎉 抽選申し込み {index + 1} 完了!")

            except ValueError as ve:
                print(f"❌ {ve}")

            except Exception as e:
                print(f"❌ 抽選申し込み {index + 1} でエラーが発生: {e}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    finally:
        if not DEBUG_MODE:
        # ドライバーを終了
            print("\nドライバーを終了中...")
            appium_utils.delete_browser_page()
            time.sleep(5)
            print("完了しました")
        else:
            pass

if __name__ == '__main__':
    TOP_P = 2 # 抽選申し込みを行う上位件件数
    WRITE_COL = 'Z'  # 抽選申し込み結果を書き込む列

    START_ROW = 4
    END_ROW = 87

    # スプレッドシートからユーザー情報を取得する
    ss = SpreadsheetApiClient()

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

        print("Appiumドライバーを初期化中...")
        appium_utils = AppiumUtilities()

        print("Safariを起動しました")

        driver = appium_utils.driver

        for user_info in user_info_list:
            if not user_info.get("email") or not user_info.get("password"):
                print(f"❌ emailまたはpasswordが未設定のためスキップします: {user_info}")
                continue
            main(driver, appium_utils, user_info, TOP_P, WRITE_COL)

        # 最低3分の待機時間を確保する
        print("次のループまで3分間待機します...")
        time.sleep(180)
