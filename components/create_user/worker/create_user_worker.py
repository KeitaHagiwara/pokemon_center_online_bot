"""
アカウント作成のワーカー
"""
from PySide6.QtCore import QThread, Signal
from create_user import exec_create_new_accounts

class CreateUserWorker(QThread):
    """アカウント作成を実行するワーカー"""
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, start_row, end_row, stop_check_callback):
        """
        Args:
            start_row: 開始行
            end_row: 終了行
            stop_check_callback: 停止チェック用のコールバック
        """
        super().__init__()
        self.start_row = start_row
        self.end_row = end_row
        self.stop_check_callback = stop_check_callback

    def run(self):
        """ワーカーのメイン処理"""
        try:
            # exec_create_new_accounts関数を呼び出し
            exec_create_new_accounts(
                start_row=self.start_row,
                end_row=self.end_row,
                log_callback=lambda msg: self.progress.emit(msg)
            )
            self.finished.emit(True, "アカウント作成が完了しました")
        except Exception as e:
            self.finished.emit(False, f"エラーが発生しました: {str(e)}")
