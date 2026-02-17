import sys
import subprocess
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QSpinBox,
    QTabWidget, QGroupBox, QMessageBox, QFileDialog
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
from components.change_address.ui.change_address_tab import create_change_address_tab
from components.service_settings.ui.service_settings_tab import create_service_settings_tab

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
from components.change_address.function.change_address_function import (
    on_change_address_start,
    on_change_address_progress,
    on_change_address_finished,
    on_change_address_stop
)
from components.service_settings.function.service_settings_function import (
    on_upload_json,
    on_upload_credentials,
    on_save_sheet_id,
    on_test_spreadsheet_connection,
    on_gmail_login,
    on_gmail_progress,
    on_gmail_finished
)

# from test_function import test
# from test_function import test
from utils.common import get_base_path
from config import (
    CREDENTIALS_FILE_NAME,
    OAUTH_FILE_NAME
)

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
        self.change_address_worker = None  # 住所変更ワーカー
        self.gmail_worker = None  # Gmailログインワーカー
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
        # 住所変更タブを追加
        change_address_tab = create_change_address_tab(self, START_ROW_DEFAULT, MAX_ROW)
        self.tabs.addTab(change_address_tab, "住所変更")
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


    def create_settings_tab(self):
        """6. 設定関連タブ - 外部関数を呼び出し"""
        settings_tab = create_service_settings_tab(self)
        self.tabs.addTab(settings_tab, "設定関連")

    def on_iphone_connect(self):
        """iPhone接続処理 - 外部関数を呼び出し"""
        on_iphone_connect(self)

    def on_script_progress(self, message):
        """スクリプト実行の進捗を表示 - 外部関数を呼び出し"""
        on_script_progress(self, message)

    def on_script_finished(self, success, message):
        """スクリプト実行完了時の処理 - 外部関数を呼び出し"""
        on_script_finished(self, success, message)

    def on_upload_json(self):
        """JSON設定ファイルのアップロード処理 - 外部関数を呼び出し"""
        on_upload_json(self, MSG_SHOW_TIME)

    def on_upload_credentials(self):
        """Credentialsファイルのアップロード処理 - 外部関数を呼び出し"""
        on_upload_credentials(self, MSG_SHOW_TIME)

    def on_save_sheet_id(self):
        """Sheet IDをJSONファイルに保存する処理 - 外部関数を呼び出し"""
        on_save_sheet_id(self, MSG_SHOW_TIME)

    def on_test_spreadsheet_connection(self):
        """スプレッドシート接続確認処理 - 外部関数を呼び出し"""
        on_test_spreadsheet_connection(self, MSG_SHOW_TIME)

    def on_gmail_login(self):
        """Gmailログイン処理 - 外部関数を呼び出し"""
        on_gmail_login(self, MSG_SHOW_TIME)

    def on_gmail_progress(self, message):
        """Gmailログイン処理の進捗を表示 - 外部関数を呼び出し"""
        on_gmail_progress(self, message)

    def on_gmail_finished(self, success, message):
        """Gmailログイン処理完了時の処理 - 外部関数を呼び出し"""
        on_gmail_finished(self, success, message, MSG_SHOW_TIME)

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

    def on_change_address_start(self):
        """住所変更処理開始 - 外部関数を呼び出し"""
        on_change_address_start(self, MSG_SHOW_TIME)

    def on_change_address_progress(self, message):
        """住所変更処理の進捗を表示 - 外部関数を呼び出し"""
        on_change_address_progress(self, message)

    def on_change_address_finished(self, success, message):
        """住所変更処理完了時の処理 - 外部関数を呼び出し"""
        on_change_address_finished(self, success, message, MSG_SHOW_TIME)

    def on_change_address_stop(self):
        """住所変更処理停止 - 外部関数を呼び出し"""
        on_change_address_stop(self, MSG_SHOW_TIME)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
