import time
from utils.gmail import get_latest_passcode
from utils.spreadsheet import SpreadsheetApiClient
from scraping.pokemon_safari_login import SafariOperator
import random

from config import SPREADSHEET_ID, SHEET_NAME

MAX_RETRY = 3

# スプレッドシートからユーザー情報を取得する
# spreadsheet_service = SpreadsheetApiClient()
# # スプレッドシートの全データをDataFrame形式で取得
# df = spreadsheet_service.get_all_records_by_df(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)
# user_info_list = spreadsheet_service.get_user_info(df)

# ユーザー情報を表示する
# for user in user_info_list:
    # print(f"ID: {user['ID']}, PW: {user['PW']}")
    # id = user['ID']
    # pw = user['PW']


so = SafariOperator()
# ブラウザキャッシュを削除
so.delete_browser_cache()
try:

    for retry_i in range(MAX_RETRY):

        try:
            driver = so.create_driver()

            # ログイン画面に遷移
            so.goto_login_page(driver)
            time.sleep(5)

            # ログイン処理
            so.lognin_pokemon_center(driver, email, password)
            time.sleep(10)

            # 画面遷移していない場合は再試行
            if ("ログイン" in driver.page_source and "/login/" in driver.current_url):
                raise Exception("ログインに失敗しました")

            # 2段階認証処理
            time.sleep(15)
            # auth_code = get_latest_passcode(to_email=email)
            for retry_j in range(MAX_RETRY):
                auth_code = get_latest_passcode(to_email=email)
                if auth_code:
                    break
                time.sleep(30)

            so.two_step_verification(driver, auth_code)
            time.sleep(10)

            # 画面遷移していない場合は再試行
            if ("パスコード入力" in driver.page_source and "/login-mfa/" in driver.current_url):
                raise Exception("2段階認証に失敗しました")

            # ここまで終わったらリトライループを抜ける
            break

        except Exception as e:
            print(f"ログイン失敗、再試行します... {e}")
            so.destroy_driver(driver)
            time.sleep(random.uniform(10, 20))
            continue

    # 利用規約同意画面が表示されたら、同意して次に進む
    if "利用規約再同意" in driver.page_source and "re-agree-to-terms" in driver.current_url:
        so.agree_terms(driver)
        time.sleep(random.uniform(10.0, 15.0))

    # 抽選申し込み処理
    for i in range(2):
        so.apply_lottery(driver, index=i)

except Exception as e:
    print(f"エラーが発生しました: {e}")

finally:
    so.destroy_driver(driver)