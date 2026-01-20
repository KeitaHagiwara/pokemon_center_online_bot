import time, random, json

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 自作モジュール
from scraping.ios.appium_utilities import AppiumUtilities
from utils.spreadsheet import SpreadsheetApiClient
from utils.login import login_pokemon_center_online
from config import SPREADSHEET_ID, SHEET_NAME

DEBUG_MODE = False
RETRY_LOOP = 3
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

        # ログイン処理
        is_logged_in = login_pokemon_center_online(driver, email, password)
        if not is_logged_in:
            raise Exception("ログインに失敗しました")

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
                                if payment_links:
                                    payment_link = payment_links[0] if len(payment_links) == 1 else payment_links[index]
                                    # スクロールして表示
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
                                # クレジットカード情報を入力する必要があるのに、必要なユーザー情報がスプシに記載されていない場合はエラーとする
                                required_fields = ["meigi", "credit_card_no", "day_of_expiry", "security_code"]
                                for field in required_fields:
                                    if not user_info.get(field):
                                        raise ValueError(f"クレジットカード情報の入力が必要ですが、ユーザー情報に {field} が設定されていません: {user_info}")

                                print("クレジットカード情報を入力中...")
                                print(user_info)
                                print(" - 名義")
                                meigi_form = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.ID, 'cardOwner'))
                                )
                                print(meigi_form)
                                meigi_form.send_keys(user_info["meigi"])
                                time.sleep(random.uniform(1, 2))

                                print(" - クレジットカード番号")
                                credit_card_no_form = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.ID, 'cardNumber'))
                                )
                                print(credit_card_no_form)
                                credit_card_no_form.send_keys(user_info["credit_card_no"])
                                time.sleep(random.uniform(1, 2))

                                print(" - 有効期限(月)")
                                day_of_expiry_month_form = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.ID, 'expirationMonth'))
                                )
                                print(day_of_expiry_month_form)
                                day_of_expiry_month_form.send_keys(user_info["day_of_expiry"].split('/')[0])  # 月
                                time.sleep(random.uniform(1, 2))

                                print(" - 有効期限(年)")
                                day_of_expiry_year_form = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.ID, 'expirationYear'))
                                )
                                print(day_of_expiry_year_form)
                                day_of_expiry_year_form.send_keys(user_info["day_of_expiry"].split('/')[1][2:])  # 年
                                time.sleep(random.uniform(1, 2))

                                print(" - セキュリティコード")
                                security_code_form = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((AppiumBy.ID, 'securityCode'))
                                )
                                print(security_code_form)
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
    WRITE_COL = 'Z'  # 抽選申し込み結果を書き込む列
    TOP_P = 2 # 抽選申し込みを行う上位件件数

    START_ROW = 4
    END_ROW = 87

    # スプレッドシートからユーザー情報を取得する
    ss = SpreadsheetApiClient()

    for loop in range(3):
        print(f"{loop}回目の処理を開始します")

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

        # 最低3分の待機時間を確保する
        print("次のループまで3分間待機します...")
        time.sleep(180)
