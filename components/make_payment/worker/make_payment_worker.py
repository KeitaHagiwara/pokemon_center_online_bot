"""
決済処理のワーカー
"""
from PySide6.QtCore import QThread, Signal
from make_payment import exec_make_payment

class MakePaymentWorker(QThread):
    """決済処理を実行するワーカー"""
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, start_row, end_row, write_col, top_p, stop_check_callback):
        """
        Args:
            start_row: 開始行
            end_row: 終了行
            write_col: 書き込み列
            top_p: 上位件数
            stop_check_callback: 停止チェック用のコールバック
        """
        super().__init__()
        self.start_row = start_row
        self.end_row = end_row
        self.write_col = write_col
        self.top_p = top_p
        self.stop_check_callback = stop_check_callback

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
            self.finished.emit(True, "決済処理が完了しました")
        except Exception as e:
            self.finished.emit(False, f"エラーが発生しました: {str(e)}")
