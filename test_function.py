import json
import time

# 自作モジュール
from scraping.ios.appium_utilities import AppiumUtilities
from utils.spreadsheet import SpreadsheetApiClient
from config import SPREADSHEET_ID, SHEET_NAME

def test(start_row, end_row, write_col, top_p):

    # スプレッドシートからユーザー情報を取得する
    ss = SpreadsheetApiClient()

    # スプレッドシートの全データをDataFrame形式で取得
    all_data = ss.get_all_data(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)

    user_info_list = ss.extract_apply_lottery_user_info(all_data, start_row, end_row, write_col, top_p, 'check_results')
    print(json.dumps(user_info_list, indent=2, ensure_ascii=False))
    print("---------------")
    print(f"合計ユーザー数: {len(user_info_list)}")
    print("---------------")

    # return user_info_list
    print("Appiumドライバーを初期化中...")
    appium_utils = AppiumUtilities()

    print("Safariを起動しました")
    driver = appium_utils.driver

    # pokemon center onlineのログインページに移動
    driver.get("https://www.pokemoncenter-online.com/login/")
    time.sleep(5)