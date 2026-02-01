"""UI定義を外部ファイルに分離してリロード可能にする例"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import QTimer


class HotReloadWindow(QMainWindow):
    """ホットリロード対応ウィンドウ"""

    def __init__(self):
        super().__init__()
        self.init_ui()

        # 定期的にUIを再構築（開発時のみ）
        self.reload_timer = QTimer()
        self.reload_timer.timeout.connect(self.reload_ui)
        self.reload_timer.start(1000)  # 1秒ごとにチェック

    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle("ホットリロード対応")
        self.setGeometry(100, 100, 400, 300)
        self.build_ui()

    def build_ui(self):
        """UI構築（この部分を動的にリロード）"""
        # 既存のウィジェットをクリア
        if self.centralWidget():
            self.centralWidget().deleteLater()

        # 新しいUIを構築
        from ui_definition import create_ui  # UI定義を外部ファイルから読み込み
        widget = create_ui()
        self.setCentralWidget(widget)

    def reload_ui(self):
        """UIをリロード"""
        try:
            import importlib
            import ui_definition
            importlib.reload(ui_definition)
            self.build_ui()
        except Exception as e:
            print(f"リロードエラー: {e}")


def main():
    app = QApplication(sys.argv)
    window = HotReloadWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
