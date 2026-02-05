"""
サービス設定関連のワーカースレッド
Gmailログイン処理を非同期で実行
"""
from PySide6.QtCore import QThread, Signal
from utils.gmail import AuthenticationService


class GmailLoginWorker(QThread):
    """Gmailログイン用のワーカースレッド"""
    finished = Signal(bool, str)  # 成功/失敗, メッセージ
    progress = Signal(str)  # 進捗メッセージ

    def __init__(self):
        super().__init__()

    def run(self):
        """スレッドで実行される処理"""
        try:
            self.progress.emit("🗑️ 過去のログイン情報を削除しています...\n")

            gmail_client = AuthenticationService()

            # 過去のトークンを削除する
            gmail_client.delete_token()
            self.progress.emit("🗑️ 過去のログイン情報を削除しました。\n")

            self.progress.emit("🔐 Gmail認証を開始しています...\n")

            # Gmail認証をやり直す
            gmail_client.authenticate()

            self.progress.emit("✅ Gmailログイン処理が完了しました。\n")
            self.finished.emit(True, "Gmailログイン処理が完了しました")

        except Exception as e:
            error_msg = f"❌ Gmailログイン処理中にエラーが発生しました: {e}\n"
            self.progress.emit(error_msg)
            self.finished.emit(False, str(e))
