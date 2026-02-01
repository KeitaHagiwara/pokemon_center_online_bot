import sys
import subprocess
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QSpinBox,
    QTabWidget, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt

# iPhone接続UIと機能のインポート
from components.setup_script.ui.iphone_connect_btn import (
    create_iphone_status_label,
    create_iphone_connect_button,
    update_iphone_status
)
from components.setup_script.function.iphone_connect_function import (
    on_iphone_connect,
    on_script_progress,
    on_script_finished
)

# タブUIのインポート
from components.apply_lottery.ui.apply_lottery_tab import create_apply_lottery_tab
from components.check_results.ui.check_results_tab import create_check_results_tab
from components.make_payment.ui.make_payment_tab import create_make_payment_tab
from components.shipping_status.ui.shipping_status_tab import create_shipping_status_tab
from components.create_user.ui.create_user_tab import create_create_user_tab

# 機能関数のインポート
from components.apply_lottery.function.apply_lottery_function import (
    on_lottery_start,
    on_lottery_progress,
    on_lottery_finished,
    on_lottery_stop
)
from components.check_results.function.check_results_function import (
    on_result_start,
    on_result_progress,
    on_result_finished,
    on_result_stop
)
from components.make_payment.function.make_payment_function import (
    on_payment_start,
    on_payment_progress,
    on_payment_finished,
    on_payment_stop
)
from components.shipping_status.function.shipping_status_functions import (
    on_shipping_status_start,
    on_shipping_progress,
    on_shipping_finished,
    on_shipping_stop
)
from components.create_user.function.create_user_function import (
    on_account_start,
    on_account_progress,
    on_account_finished,
    on_account_stop
)

# from test_function import test
from initialize_gmail import initialize_gmail_oauth
from test_function import test
from utils.common import get_base_path

START_ROW_DEFAULT = 4
MAX_ROW = 10000
MSG_SHOW_TIME = 5000  # ステータスメッセージ表示時間（ミリ秒）

class MainWindow(QMainWindow):
    """メインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.lottery_worker = None  # 抽選実行ワーカー
        self.result_worker = None  # 抽選結果取得ワーカー
        self.payment_worker = None  # 決済処理ワーカー
        self.shipping_worker = None  # 発送ステータス確認ワーカー
        self.account_worker = None  # アカウント作成ワーカー
        self.init_ui()

    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle("ポケモンセンターオンライン 自動化ツール")
        self.setGeometry(100, 100, 900, 700)

        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # メインレイアウト
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # iPhone接続ステータス（タイトルの上、右寄せ）
        status_layout = create_iphone_status_label(self)
        main_layout.addLayout(status_layout)

        # タイトル
        title_label = QLabel("ポケモンセンターオンライン 自動化ツール")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # iPhone接続ボタンと注意書き
        iphone_button_layout, note_label = create_iphone_connect_button(self)
        main_layout.addLayout(iphone_button_layout)
        main_layout.addWidget(note_label)

        # タブウィジェット作成
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # 各タブを作成
        lottery_tab = create_apply_lottery_tab(self, START_ROW_DEFAULT, MAX_ROW)
        self.tabs.addTab(lottery_tab, "抽選実行")
        result_tab = create_check_results_tab(self, START_ROW_DEFAULT, MAX_ROW)
        self.tabs.addTab(result_tab, "結果取得")
        payment_tab = create_make_payment_tab(self, START_ROW_DEFAULT, MAX_ROW)
        self.tabs.addTab(payment_tab, "決済処理")
        # 発送ステータス確認タブを追加
        shipping_tab = create_shipping_status_tab(self, START_ROW_DEFAULT, MAX_ROW)
        self.tabs.addTab(shipping_tab, "発送ステータス確認")
        account_tab = create_create_user_tab(self, START_ROW_DEFAULT, MAX_ROW)
        self.tabs.addTab(account_tab, "アカウント作成")
        self.create_settings_tab()

        # ステータスバー
        self.statusBar().showMessage("準備完了")

    def closeEvent(self, event):
        """アプリケーション終了時の処理"""
        try:
            # terminate.shを実行してappiumを停止
            current_dir = get_base_path()
            terminate_script = os.path.join(current_dir, "scripts", "terminate.sh")
            subprocess.run(
                ["sh", terminate_script],
                cwd=current_dir,
                capture_output=True,
                text=True
            )
            print("Appiumサーバーを停止しました")
        except Exception as e:
            print(f"Appium停止時にエラーが発生しました: {str(e)}")
        finally:
            # イベントを受け入れてアプリケーションを終了
            event.accept()

    def create_shipping_status_tab(self):
        """4. 発送ステータス確認タブ"""
        shipping_widget = QWidget()
        layout = QVBoxLayout()

        # 設定グループ
        settings_group = QGroupBox("実行設定")
        settings_layout = QVBoxLayout()

        # 開始行・終了行
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("開始行:"))
        self.shipping_start_row = QSpinBox()
        self.shipping_start_row.setRange(START_ROW_DEFAULT, MAX_ROW)
        self.shipping_start_row.setValue(START_ROW_DEFAULT)
        row_layout.addWidget(self.shipping_start_row)

        row_layout.addWidget(QLabel("終了行:"))
        self.shipping_end_row = QSpinBox()
        self.shipping_end_row.setRange(START_ROW_DEFAULT, MAX_ROW)
        self.shipping_end_row.setValue(10)
        row_layout.addWidget(self.shipping_end_row)
        row_layout.addStretch()
        settings_layout.addLayout(row_layout)

        # 書き込み列
        col_layout = QHBoxLayout()
        col_layout.addWidget(QLabel("発送ステータスの書き込み先の列番号:"))
        self.shipping_write_col = QLineEdit()
        self.shipping_write_col.setPlaceholderText("例: AB")
        self.shipping_write_col.setMaximumWidth(100)
        col_layout.addWidget(self.shipping_write_col)
        col_layout.addStretch()
        settings_layout.addLayout(col_layout)

        # 上位件数
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("確認対象上位件数:"))
        self.shipping_top_p = QSpinBox()
        self.shipping_top_p.setRange(1, 10)
        self.shipping_top_p.setValue(1)
        top_layout.addWidget(self.shipping_top_p)
        top_layout.addStretch()
        settings_layout.addLayout(top_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # ログ表示エリア
        log_group = QGroupBox("実行ログ")
        log_layout = QVBoxLayout()
        self.shipping_log = QTextEdit()
        self.shipping_log.setReadOnly(True)
        self.shipping_log.setPlaceholderText("実行ログがここに表示されます...")
        log_layout.addWidget(self.shipping_log)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # 実行ボタン
        button_layout = QHBoxLayout()
        start_button = QPushButton("発送ステータス確認開始")
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #f1c40f;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f39c12;
            }
        """)
        start_button.clicked.connect(self.on_shipping_status_start)
        button_layout.addWidget(start_button)

        stop_button = QPushButton("停止")
        stop_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        stop_button.clicked.connect(self.on_stop)
        button_layout.addWidget(stop_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        shipping_widget.setLayout(layout)
        self.tabs.addTab(shipping_widget, "発送ステータス確認")

    def create_settings_tab(self):
        """6. 設定関連タブ"""
        settings_widget = QWidget()
        layout = QVBoxLayout()

        # 設定グループ
        settings_group = QGroupBox("Gmail設定")
        settings_layout = QVBoxLayout()

        # Gmailログインボタン
        button_layout = QHBoxLayout()
        gmail_login_button = QPushButton("Gmailログイン")
        gmail_login_button.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
        """)
        gmail_login_button.clicked.connect(self.on_gmail_login)
        button_layout.addWidget(gmail_login_button)
        button_layout.addStretch()
        settings_layout.addLayout(button_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # ログ表示エリア
        log_group = QGroupBox("実行ログ")
        log_layout = QVBoxLayout()
        self.settings_log = QTextEdit()
        self.settings_log.setReadOnly(True)
        self.settings_log.setPlaceholderText("実行ログがここに表示されます...")
        log_layout.addWidget(self.settings_log)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        layout.addStretch()
        settings_widget.setLayout(layout)
        self.tabs.addTab(settings_widget, "設定関連")

    def on_iphone_connect(self):
        """iPhone接続処理 - 外部関数を呼び出し"""
        on_iphone_connect(self)

    def on_script_progress(self, message):
        """スクリプト実行の進捗を表示 - 外部関数を呼び出し"""
        on_script_progress(self, message)

    def on_script_finished(self, success, message):
        """スクリプト実行完了時の処理 - 外部関数を呼び出し"""
        on_script_finished(self, success, message)

    def on_gmail_login(self):
        """Gmailログイン処理"""
        self.settings_log.append("Gmailログイン処理を開始します...\n")
        self.statusBar().showMessage("Gmailログイン処理中...", MSG_SHOW_TIME)
        initialize_gmail_oauth(self.settings_log)
        self.statusBar().showMessage("Gmailログイン処理完了", MSG_SHOW_TIME)

    def on_lottery_start(self):
        """抽選実行開始 - 外部関数を呼び出し"""
        on_lottery_start(self, MSG_SHOW_TIME)

    def on_lottery_progress(self, message):
        """抽選実行の進捗を表示 - 外部関数を呼び出し"""
        on_lottery_progress(self, message)

    def on_lottery_finished(self, success, message):
        """抽選実行完了時の処理 - 外部関数を呼び出し"""
        on_lottery_finished(self, success, message, MSG_SHOW_TIME)

    def on_lottery_stop(self):
        """抽選実行停止 - 外部関数を呼び出し"""
        on_lottery_stop(self, MSG_SHOW_TIME)

    def on_result_start(self):
        """抽選結果取得開始 - 外部関数を呼び出し"""
        on_result_start(self, MSG_SHOW_TIME)

    def on_result_progress(self, message):
        """抽選結果取得の進捗を表示 - 外部関数を呼び出し"""
        on_result_progress(self, message)

    def on_result_finished(self, success, message):
        """抽選結果取得完了時の処理 - 外部関数を呼び出し"""
        on_result_finished(self, success, message, MSG_SHOW_TIME)

    def on_result_stop(self):
        """抽選結果取得停止 - 外部関数を呼び出し"""
        on_result_stop(self, MSG_SHOW_TIME)

    def on_payment_start(self):
        """決済処理開始 - 外部関数を呼び出し"""
        on_payment_start(self, MSG_SHOW_TIME)

    def on_payment_progress(self, message):
        """決済処理の進捗を表示 - 外部関数を呼び出し"""
        on_payment_progress(self, message)

    def on_payment_finished(self, success, message):
        """決済処理完了時の処理 - 外部関数を呼び出し"""
        on_payment_finished(self, success, message, MSG_SHOW_TIME)

    def on_payment_stop(self):
        """決済処理停止 - 外部関数を呼び出し"""
        on_payment_stop(self, MSG_SHOW_TIME)

    def on_shipping_status_start(self):
        """発送ステータス確認開始 - 外部関数を呼び出し"""
        on_shipping_status_start(self, MSG_SHOW_TIME)

    def on_shipping_progress(self, message):
        """発送ステータス確認の進捗を表示 - 外部関数を呼び出し"""
        on_shipping_progress(self, message)

    def on_shipping_finished(self, success, message):
        """発送ステータス確認完了時の処理 - 外部関数を呼び出し"""
        on_shipping_finished(self, success, message, MSG_SHOW_TIME)

    def on_shipping_stop(self):
        """発送ステータス確認停止 - 外部関数を呼び出し"""
        on_shipping_stop(self, MSG_SHOW_TIME)

    def on_account_start(self):
        """アカウント作成開始 - 外部関数を呼び出し"""
        on_account_start(self, MSG_SHOW_TIME)

    def on_account_progress(self, message):
        """アカウント作成の進捗を表示 - 外部関数を呼び出し"""
        on_account_progress(self, message)

    def on_account_finished(self, success, message):
        """アカウント作成完了時の処理 - 外部関数を呼び出し"""
        on_account_finished(self, success, message, MSG_SHOW_TIME)

    def on_account_stop(self):
        """アカウント作成停止 - 外部関数を呼び出し"""
        on_account_stop(self, MSG_SHOW_TIME)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
