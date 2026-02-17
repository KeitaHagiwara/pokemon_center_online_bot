from PySide6.QtCore import QThread, Signal
from check_shipping_status import exec_check_shipping_status


class ShippingStatusWorker(QThread):
    """発送ステータス確認用のワーカースレッド"""
    finished = Signal(bool, str)  # 成功/失敗, メッセージ
    progress = Signal(str)  # 進捗メッセージ

    def __init__(self, start_row, end_row, write_col, top_p):
        super().__init__()
        self.start_row = start_row
        self.end_row = end_row
        self.write_col = write_col
        self.top_p = top_p
        self._is_stopped = False  # 停止フラグ

    def stop(self):
        """ワーカーを停止"""
        self._is_stopped = True

    def run(self):
        """スレッドで実行される処理"""
        try:
            # 発送ステータス確認を実行
            exec_check_shipping_status(
                self.start_row,
                self.end_row,
                self.write_col,
                self.top_p,
                log_callback=lambda msg: self.progress.emit(msg)
            )
            if not self._is_stopped:
                self.finished.emit(True, "発送ステータス確認が完了しました")
        except Exception as e:
            if not self._is_stopped:
                error_message = f"エラーが発生しました: {str(e)}"
                self.finished.emit(False, error_message)