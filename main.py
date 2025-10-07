from utils.gmail import GmailApiClient
from utils.spreadsheet import SpreadsheetApiClient

from config import SPREADSHEET_ID, SHEET_NAME

# スプレッドシートからユーザー情報を取得する
spreadsheet_service = SpreadsheetApiClient()
# スプレッドシートの全データをDataFrame形式で取得
df = spreadsheet_service.get_all_records_by_df(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)
user_info_list = spreadsheet_service.get_user_info(df)

# ユーザー情報を表示する
for user in user_info_list:
    print(f"ID: {user['ID']}, PW: {user['PW']}")