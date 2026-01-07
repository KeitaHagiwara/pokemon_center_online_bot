import time, random, json

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.keys import Keys
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

        target_lottery_result = None
        for target_product_name, target_product_column in target_product_name_dict.items():
            print(f"\n=== 抽選結果確認対象商品: {target_product_name} ===")

            driver.get("https://www.pokemoncenter-online.com/lottery-history/")
            time.sleep(random.uniform(3, 5))

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
                        if target_lottery_result.strip() == "落選":
                            break  # 抽選結果ループを抜ける

                        # 抽選結果が「当選」の場合のみ決済を通す
                        if target_lottery_result.strip() == "当選":
                            print("当選したため決済処理を実行します")
                            try:
                                # payment_link = WebDriverWait(driver, 10).until(
                                #     EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, '.comBtn a'))
                                # )
                                # # スクロールして表示
                                # driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", payment_link)
                                # time.sleep(1)
                                # # JavaScriptでクリック
                                # driver.execute_script("arguments[0].click();", payment_link)

                                payment_links = WebDriverWait(driver, 10).until(
                                    EC.presence_of_all_elements_located((AppiumBy.CSS_SELECTOR, '.comBtn a'))
                                )

                                # 当選が複数ある場合は、indexに応じて決済ページに遷移する
                                if payment_links and len(payment_links) >= 2:
                                    # スクロールして表示
                                    payment_link = payment_links[index]
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", payment_link)
                                    time.sleep(1)
                                    # JavaScriptでクリック
                                    driver.execute_script("arguments[0].click();", payment_link)
                                else:
                                    print(f"❌ 決済ボタンが見つかりませんでした (index={index})")
                            except Exception as e:
                                print(f"決済ページへの遷移に失敗: {e}")
                                pass
                            time.sleep(random.uniform(3, 5))

                            # 決済処理を実行 -> カートに追加する
                            print("予約受付に申し込む")
                            try:
                                reservation_link = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, '.add-to-cart-button a'))
                                )
                                # スクロールして表示
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reservation_link)
                                time.sleep(1)
                                # JavaScriptでクリック
                                driver.execute_script("arguments[0].click();", reservation_link)
                            except Exception as e:
                                print(f"予約ボタンのクリックに失敗: {e}")
                                pass
                            time.sleep(random.uniform(3, 5))

                            print("カートページに移動")
                            driver.get("https://www.pokemoncenter-online.com/cart/")
                            time.sleep(random.uniform(3, 5))

                            print("レジに進む")
                            driver.get("https://www.pokemoncenter-online.com/order/")
                            time.sleep(random.uniform(3, 5))

                            print("お支払い方法の選択へ進む")
                            try:
                                payment_method_link = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, '.submit-shipping'))
                                )
                                # スクロールして表示
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", payment_method_link)
                                time.sleep(1)
                                # JavaScriptでクリック
                                driver.execute_script("arguments[0].click();", payment_method_link)
                            except Exception as e:
                                print(f"お支払い方法の選択ボタンのクリックに失敗: {e}")
                                pass
                            time.sleep(random.uniform(3, 5))

                            # クレカ情報の入力
                            registered_card_no_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, '.carTxt.stored-card-number'))
                            )
                            if registered_card_no_element.get_attribute('innerText').strip() == "":
                                print("クレジットカード情報を入力中...")
                                meigi_form = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.ID, 'cardOwner'))
                                )
                                meigi_form.send_keys(user_info["meigi"])
                                time.sleep(random.uniform(1, 2))

                                credit_card_no_form = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.ID, 'cardNumber'))
                                )
                                credit_card_no_form.send_keys(user_info["credit_card_no"])
                                time.sleep(random.uniform(1, 2))

                                day_of_expiry_month_form = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.ID, 'expirationMonth'))
                                )
                                day_of_expiry_month_form.send_keys(user_info["day_of_expiry"].split('/')[0])  # 月
                                time.sleep(random.uniform(1, 2))

                                day_of_expiry_year_form = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.ID, 'expirationYear'))
                                )
                                day_of_expiry_year_form.send_keys(user_info["day_of_expiry"].split('/')[1][2:])  # 年
                                time.sleep(random.uniform(1, 2))

                                security_code_form = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.ID, 'securityCode'))
                                )
                                security_code_form.send_keys(user_info["security_code"])
                                time.sleep(random.uniform(1, 2))

                            # 内容を確認するボタンをクリックする
                            print("内容を確認するボタンをクリック中...")
                            try:
                                payment_method_link = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, '.submit-payment'))
                                )
                                # スクロールして表示
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", payment_method_link)
                                time.sleep(1)
                                # JavaScriptでクリック
                                driver.execute_script("arguments[0].click();", payment_method_link)
                            except Exception as e:
                                print(f"内容を確認するボタンのクリックに失敗: {e}")
                                pass
                            time.sleep(random.uniform(3, 5))

                            print("注文を確定するボタンをクリック中...")
                            try:
                                confirm_order_button = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, '.list02.next-step-button a'))
                                )
                                # スクロールして表示
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_order_button)
                                time.sleep(1)
                                # JavaScriptでクリック
                                driver.execute_script("arguments[0].click();", confirm_order_button)
                            except Exception as e:
                                print(f"注文を確定するボタンのクリックに失敗: {e}")
                                pass
                            # 決済には時間がかかることがあるため、念の為長めに待機
                            time.sleep(20)

                            # ご注文番号を取得
                            order_number = None
                            try:
                                order_number_element = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, '.numberTxt .txt'))
                                )
                                order_number = order_number_element.get_attribute('innerText')
                                print(f"ご注文番号: {order_number}")
                            except Exception as e:
                                print(f"ご注文番号の取得に失敗: {e}")

                            if "ご注文完了" in driver.page_source:
                                print("✅ 決済処理が完了しました")
                                print("=========================")
                                print(f"ご注文番号: {order_number}")
                                print("=========================")

                                # スプレッドシートに「決済」と書き込む
                                ss.write_to_cell(
                                    spreadsheet_id=SPREADSHEET_ID,
                                    sheet_name=SHEET_NAME,
                                    row=row_number,
                                    column=target_product_column,
                                    value="決済"
                                )
                            break  # 抽選結果ループを抜ける

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
        # pass
        print("\nドライバーを終了中...")
        appium_utils.delete_browser_page()
        time.sleep(random.uniform(10, 15))
        print("完了しました")

if __name__ == '__main__':
    WRITE_COL = 'X'  # 抽選申し込み結果を書き込む列
    TOP_P = 2 # 抽選申し込みを行う上位件件数

    START_ROW = 47
    END_ROW = 75

    # スプレッドシートからユーザー情報を取得する
    ss = SpreadsheetApiClient()
    # スプレッドシートの全データをDataFrame形式で取得
    all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)
    user_info_list = ss.extract_payment_user_info(all_data, START_ROW, END_ROW, WRITE_COL, TOP_P)

    print(json.dumps(user_info_list, indent=2, ensure_ascii=False))
    print("---------------")
    print(f"合計ユーザー数: {len(user_info_list)}")
    print("---------------")

    # 抽選結果確認対象商品名の辞書を取得
    target_product_name_dict = ss.get_check_target_product_name_dict(all_data, WRITE_COL, TOP_P)

    print("Appiumドライバーを初期化中...")
    appium_utils = AppiumUtilities()

    print("Safariを起動しました")

    driver = appium_utils.driver


    for user_info in user_info_list:
        if not user_info.get("email") or not user_info.get("password"):
            print(f"❌ emailまたはpasswordが未設定のためスキップします: {user_info}")
            continue
        main(driver, appium_utils, user_info, target_product_name_dict)
