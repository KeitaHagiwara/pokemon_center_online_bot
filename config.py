import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# Pokemon Center Online ログイン情報
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
