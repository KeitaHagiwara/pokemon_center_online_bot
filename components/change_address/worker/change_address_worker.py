from PySide6.QtCore import QThread, Signal
from change_address import exec_change_address


class ChangeAddressWorker(QThread):
    """住所変更処理を実行するワーカースレッド"""

    progress = Signal(str)  # 進捗メッセージを送信
    finished = Signal(bool, str)  # 完了時に成功/失敗とメッセージを送信

    def __init__(self, start_row, end_row):
        super().__init__()
        self.start_row = start_row
        self.end_row = end_row
        self._is_stopped = False

    def stop(self):
        """ワーカーを停止"""
        self._is_stopped = True

    def run(self):
        """スレッドで実行される処理"""
        try:
            # 住所変更処理を実行
            exec_change_address(
                self.start_row,
                self.end_row,
                log_callback=lambda msg: self.progress.emit(msg)
            )

            if not self._is_stopped:
                self.finished.emit(True, "住所変更処理が完了しました")
        except Exception as e:
            if not self._is_stopped:
                error_message = f"エラーが発生しました: {str(e)}"
                self.finished.emit(False, error_message)
