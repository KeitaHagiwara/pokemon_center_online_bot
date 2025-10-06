import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 認証情報の設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_name('./credentials/pokemon-center-online-bot-afbfddf3c771.json', scope)

# クライアントの作成
client = gspread.authorize(creds)

# スプレッドシートIDを指定してスプレッドシートを開く
spreadsheet_id = '1Df1ztQAaYKCu8t51VbYMP3JCy2ppcg_LLEe4RxOyT9o'
spreadsheet = client.open_by_key(spreadsheet_id)

# ワークシートの取得
worksheet = spreadsheet.sheet1

# データの読み取り例
print("スプレッドシートのタイトル:", spreadsheet.title)
print("ワークシートのタイトル:", worksheet.title)

# 全てのデータを取得してDataFrame形式に変換
all_data = worksheet.get_all_values()

# DataFrameに変換（最初の行をヘッダーとして使用）
if all_data:
    df = pd.DataFrame(all_data[1:], columns=all_data[0])
    print("\nDataFrame形式で取得したデータ:")
    print(df)
    print(f"\nDataFrameのサイズ: {df.shape}")
    print(f"カラム名: {list(df.columns)}")
else:
    print("データが見つかりません")

# 特定の範囲をDataFrame形式で取得する例
range_data = worksheet.get('A1:B10')
if range_data:
    df_range = pd.DataFrame(range_data[1:], columns=range_data[0])
    print(f"\n指定範囲(A1:B10)のDataFrame:")
    print(df_range)