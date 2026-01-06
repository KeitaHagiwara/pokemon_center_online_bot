import time, random, json

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 自作モジュール
from scraping.ios.appium_utilities import AppiumUtilities
from utils.spreadsheet import SpreadsheetApiClient
from utils.gmail import get_latest_passcode
from utils.common import get_column_number_by_alphabet
from config import SPREADSHEET_ID, SHEET_NAME

MAX_RETRY_LOGIN = 3
MAX_RETRY_PASSCODE = 10


def main(driver, appium_utils, user_info, top_p=1, write_col='AA'):
    """抽選応募処理"""

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

        for retry_i in range(MAX_RETRY_LOGIN):

            try:
                # ログイン画面に遷移
                driver.get("https://www.pokemoncenter-online.com/login/")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.TAG_NAME, "body")))
                print("ログインページに移動しました")

                time.sleep(random.uniform(3, 5))

                print("IDを入力中...")
                email_form = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((AppiumBy.ID, 'login-form-email'))
                )
                email_form.send_keys(email)

                time.sleep(random.uniform(3, 5))

                print("パスワードを入力中...")
                password_form = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((AppiumBy.ID, 'current-password'))
                )
                password_form.send_keys(password)

                time.sleep(random.uniform(3, 5))

                print("ログインボタンをクリック中...")
                login_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((AppiumBy.XPATH, "//*[@id='form1Button']"))
                )
                login_button.click()

                time.sleep(15)
                if ("ログイン" in driver.page_source and "/login/" in driver.current_url):
                    raise Exception("ログインに失敗しました")

                # 2段階認証処理
                for retry_j in range(MAX_RETRY_PASSCODE):
                    auth_code = get_latest_passcode(to_email=email)
                    if auth_code:
                        break
                    time.sleep(15)

                print("パスコードを入力中...")
                passcode_form = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((AppiumBy.ID, 'authCode'))
                )
                passcode_form.send_keys(auth_code)

                time.sleep(random.uniform(3, 5))

                print("認証ボタンをクリック中...")
                auth_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((AppiumBy.ID, 'authBtn'))
                )
                auth_button.click()

                time.sleep(10)
                if ("パスコード入力" in driver.page_source and "/login-mfa/" in driver.current_url):
                    raise Exception("2段階認証に失敗しました")

                # ここまで終わったらリトライループを抜ける
                break

            except Exception as e:
                print(f"ログイン失敗、再試行します... {e}")
                appium_utils.delete_browser_page()
                time.sleep(10)
                continue

        driver.get("https://www.pokemoncenter-online.com/lottery/apply.html")
        time.sleep(random.uniform(5, 10))

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

                # スプレッドシートに結果を書き込む
                ss = SpreadsheetApiClient()
                write_col_number = get_column_number_by_alphabet(write_col) + index
                ss.write_to_cell(
                    spreadsheet_id=SPREADSHEET_ID,
                    sheet_name=SHEET_NAME,
                    row=row_number,
                    column=write_col_number,
                    value="応募済み"
                )

                time.sleep(random.uniform(10, 15))
                print(f"🎉 抽選申し込み {index + 1} 完了!")

            except ValueError as ve:
                print(f"❌ {ve}")

            except Exception as e:
                print(f"❌ 抽選申し込み {index + 1} でエラーが発生: {e}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        # driver.save_screenshot('error_screenshot.png')

    finally:
        # # ポケセンオンラインからログアウトする
        # print("マイページに移動中...")
        # driver.get("https://www.pokemoncenter-online.com/mypage/")
        # time.sleep(5)

        # print("ログアウト中...")
        # logout_buttons = appium_utils.safe_find_elements(AppiumBy.CLASS_NAME, 'logout')
        # # if logout_buttons[0].get_attribute("innerText") == "ログアウト":
        # if not appium_utils.safe_click(logout_buttons, 0, "ログアウト"):
        #     print("❌ ログアウトボタンのクリックに失敗しました")
        # time.sleep(10)

        # ドライバーを終了
        print("\nドライバーを終了中...")
        appium_utils.delete_browser_page()
        time.sleep(random.uniform(10, 15))
        print("完了しました")

if __name__ == '__main__':
    TOP_P = 2 # 抽選申し込みを行う上位件件数
    WRITE_COL = 'AA'  # 抽選申し込み結果を書き込む列

    START_ROW = 27
    END_ROW = 75

    # スプレッドシートからユーザー情報を取得する
    ss = SpreadsheetApiClient()
    # スプレッドシートの全データをDataFrame形式で取得
    all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)
    user_info_list = ss.extract_apply_lottery_user_info(all_data, START_ROW, END_ROW, WRITE_COL)
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
        main(driver, appium_utils, user_info, TOP_P, WRITE_COL)
