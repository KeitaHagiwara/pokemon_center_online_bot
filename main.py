import time
from utils.gmail import get_latest_passcode
from utils.spreadsheet import SpreadsheetApiClient
from scraping.pokemon_safari_login import SafariOperator

from config import SPREADSHEET_ID, SHEET_NAME

# スプレッドシートからユーザー情報を取得する
spreadsheet_service = SpreadsheetApiClient()
# スプレッドシートの全データをDataFrame形式で取得
df = spreadsheet_service.get_all_records_by_df(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)
user_info_list = spreadsheet_service.get_user_info(df)

# ユーザー情報を表示する
# for user in user_info_list:
    # print(f"ID: {user['ID']}, PW: {user['PW']}")
    # id = user['ID']
    # pw = user['PW']

id = "hagiwara.2016@gmail.com"
pw = "Vaceatker@1"

try:

    safari_operator = SafariOperator()
    # ログイン処理
    if safari_operator.login_pokemon_center(id, pw):
        print("ログイン成功")
    else:
        raise Exception("ログイン失敗")

    time.sleep(5)
    auth_code = get_latest_passcode(to_email=id)

    # 二段階認証コードの取得と入力
    if safari_operator.two_step_verification(auth_code):
        print("二段階認証成功")
    else:
        raise Exception("二段階認証失敗")



except Exception as e:
    print(f"エラーが発生しました: {e}")

finally:
    safari_operator.destroy_driver()
