# 自作モジュール
from utils.gmail import AuthenticationService

def initialize_gmail_oauth(logger):

    try:
        gmail_client = AuthenticationService()

        # 過去のトークンを削除する
        gmail_client.delete_token()
        logger.append("🗑️ 過去のログイン情報を削除しました。\n")

        # Gmail認証をやり直す
        gmail_client.authenticate()
        logger.append("✅ Gmailログイン処理が完了しました。\n")

    except Exception as e:
        logger.append(f"❌ Gmailログイン処理中にエラーが発生しました: {e}\n")