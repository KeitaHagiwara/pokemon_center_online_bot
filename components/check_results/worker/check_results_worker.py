from PySide6.QtCore import QThread, Signal
from check_results import exec_check_results


class CheckResultsWorker(QThread):
    """抽選結果取得処理を行うワーカースレッド"""

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
        """抽選結果取得処理の本体"""
        try:
            # 抽選結果取得を実行
            exec_check_results(
                self.start_row,
                self.end_row,
                self.write_col,
                self.top_p,
                log_callback=lambda msg: self.progress.emit(msg)
            )
            if not self._is_stopped:
                self.finished.emit(True, "抽選結果取得が完了しました")
        except Exception as e:
            if not self._is_stopped:
                error_msg = f"エラーが発生しました: {str(e)}"
                self.finished.emit(False, error_msg)