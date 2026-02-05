import os
import json
from dotenv import load_dotenv
from utils.common import get_base_path

# .envファイルを読み込み（パスを明示的に指定）
env_path = os.path.join(get_base_path(), '.env')
load_dotenv(env_path)

# 環境変数から設定を取得
CREDENTIALS_FILE_NAME = os.getenv("CREDENTIALS_FILE_NAME")
OAUTH_FILE_NAME = os.getenv("OAUTH_FILE_NAME")
OAUTH_TOKEN_FILE_NAME = os.getenv("OAUTH_TOKEN_FILE_NAME")

# sheet_info.jsonから設定を取得
sheet_info_path = os.path.join(get_base_path(), 'credentials', 'service_account', 'sheet_info.json')
try:
    with open(sheet_info_path, 'r', encoding='utf-8') as f:
        sheet_info = json.load(f)
        SPREADSHEET_ID = sheet_info.get("sheet_id")
        SHEET_NAME = sheet_info.get("sheet_name")
except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    print(f"Warning: sheet_info.json読み込みエラー: {e}")
    SPREADSHEET_ID = None
    SHEET_NAME = None

PLATFORM_VERSION = os.getenv("PLATFROM_VERSION")
DEVICE_NAME = os.getenv("DEVICE_NAME")
UDID = os.getenv("UDID")
XCODE_ORG_ID = os.getenv("XCODE_ORG_ID")
XCODE_BUNDLE_ID = os.getenv("XCODE_BUNDLE_ID")