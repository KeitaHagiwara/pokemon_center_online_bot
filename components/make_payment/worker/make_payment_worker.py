"""
決済処理のワーカー
"""
from PySide6.QtCore import QThread, Signal
from make_payment import exec_make_payment

class MakePaymentWorker(QThread):
    """決済処理を実行するワーカー"""
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, start_row, end_row, write_col, top_p):
        """
        Args:
            start_row: 開始行
            end_row: 終了行
            write_col: 書き込み列
            top_p: 上位件数
        """
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
        """ワーカーのメイン処理"""
        try:
            # exec_make_payment関数を呼び出し
            exec_make_payment(
                start_row=self.start_row,
                end_row=self.end_row,
                write_col=self.write_col,
                top_p=self.top_p,
                log_callback=lambda msg: self.progress.emit(msg)
            )
            if not self._is_stopped:
                self.finished.emit(True, "決済処理が完了しました")
        except Exception as e:
            if not self._is_stopped:
                error_message = f"エラーが発生しました: {str(e)}"
                self.finished.emit(False, error_message)