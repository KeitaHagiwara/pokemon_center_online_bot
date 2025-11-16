import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# 環境変数から設定を取得
CREDENTIALS_FILE_NAME = os.getenv("CREDENTIALS_FILE_NAME")
OAUTH_FILE_NAME = os.getenv("OAUTH_FILE_NAME")
OAUTH_TOKEN_FILE_NAME = os.getenv("OAUTH_TOKEN_FILE_NAME")

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")
