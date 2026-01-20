import os
from dotenv import load_dotenv
from utils.common import get_base_path

# .envファイルを読み込み（パスを明示的に指定）
env_path = os.path.join(get_base_path(), '.env')
load_dotenv(env_path)

# 環境変数から設定を取得
CREDENTIALS_FILE_NAME = os.getenv("CREDENTIALS_FILE_NAME")
OAUTH_FILE_NAME = os.getenv("OAUTH_FILE_NAME")
OAUTH_TOKEN_FILE_NAME = os.getenv("OAUTH_TOKEN_FILE_NAME")

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

PLATFORM_VERSION = os.getenv("PLATFROM_VERSION")
DEVICE_NAME = os.getenv("DEVICE_NAME")
UDID = os.getenv("UDID")
XCODE_ORG_ID = os.getenv("XCODE_ORG_ID")
XCODE_BUNDLE_ID = os.getenv("XCODE_BUNDLE_ID")