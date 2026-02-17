"""
アカウント作成のワーカー
"""
from PySide6.QtCore import QThread, Signal
from create_user import exec_create_new_accounts

class CreateUserWorker(QThread):
    """アカウント作成を実行するワーカー"""
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, start_row, end_row):
        """
        Args:
            start_row: 開始行
            end_row: 終了行
        """
        super().__init__()
        self.start_row = start_row
        self.end_row = end_row
        self._is_stopped = False

    def stop(self):
        """ワーカーを停止"""
        self._is_stopped = True

    def run(self):
        """ワーカーのメイン処理"""
        try:
            # exec_create_new_accounts関数を呼び出し
            exec_create_new_accounts(
                start_row=self.start_row,
                end_row=self.end_row,
                log_callback=lambda msg: self.progress.emit(msg)
            )
            if not self._is_stopped:
                self.finished.emit(True, "アカウント作成が完了しました")
        except Exception as e:
            if not self._is_stopped:
                error_message = f"エラーが発生しました: {str(e)}"
                self.finished.emit(False, error_message)