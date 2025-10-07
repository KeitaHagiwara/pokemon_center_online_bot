import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# 環境変数から設定を取得
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")
