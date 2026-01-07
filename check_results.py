import time, random, json

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 自作モジュール
from scraping.ios.appium_utilities import AppiumUtilities
from utils.spreadsheet import SpreadsheetApiClient
from utils.gmail import extract_target_str_from_gmail_text_in_5min
from utils.common import get_column_number_by_alphabet
from config import SPREADSHEET_ID, SHEET_NAME

MAX_RETRY_LOGIN = 3
MAX_RETRY_PASSCODE = 10


def main(driver, appium_utils, user_info, target_product_name_dict):
    """メイン処理"""

    row_number = user_info["row_number"]
    email = user_info["email"]
    password = user_info["password"]
    print(f"email: {email}")
    print(f"password: {password}")

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
                    auth_code = extract_target_str_from_gmail_text_in_5min(
                        to_email=email,
                        subject_keyword="[ポケモンセンターオンライン]ログイン用パスコードのお知らせ",
                        email_type="passcode"
                    )
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


    START_ROW = 6
    END_ROW = 75

    # スプレッドシートからユーザー情報を取得する
    ss = SpreadsheetApiClient()
    # スプレッドシートの全データをDataFrame形式で取得
    all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)

    user_info_list = ss.extract_apply_lottery_user_info(all_data, START_ROW, END_ROW)
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
