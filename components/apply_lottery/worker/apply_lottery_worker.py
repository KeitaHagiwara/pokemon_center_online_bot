from PySide6.QtCore import QThread, Signal
from apply_lottery import exec_apply_lottery


class ApplyLotteryWorker(QThread):
    """抽選実行処理を行うワーカースレッド"""

    progress = Signal(str)  # 進捗メッセージを送信
    finished = Signal(bool, str)  # 完了時に成功/失敗とメッセージを送信

    def __init__(self, start_row, end_row, write_col, top_p):
        super().__init__()
        self.start_row = start_row
        self.end_row = end_row
        self.write_col = write_col
        self.top_p = top_p
        self._is_stopped = False

    def stop(self):
        """ワーカーを停止"""
        self._is_stopped = True

    def run(self):
        """スレッドで実行される処理"""
        try:
            # ログ用のカスタムコールバック関数
            def log_callback(message):
                self.progress.emit(message)

            # 抽選実行を実行
            exec_apply_lottery(
                self.start_row,
                self.end_row,
                self.write_col,
                self.top_p,
                log_callback
            )
            self.finished.emit(True, "抽選実行が完了しました")
        except Exception as e:
            error_message = f"エラーが発生しました: {str(e)}"
            self.finished.emit(False, error_message)