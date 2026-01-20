import sys
import subprocess
import select
import os
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QSpinBox,
    QTabWidget, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# from test_function import test
# from initialize_gmail import initialize_gmail_oauth
from test_function import test
from utils.common import get_base_path

START_ROW_DEFAULT = 4
MAX_ROW = 10000
MSG_SHOW_TIME = 5000  # ステータスメッセージ表示時間（ミリ秒）

class ScriptWorker(QThread):
    """スクリプト実行用のワーカースレッド"""
    finished = pyqtSignal(bool, str)  # 成功/失敗, メッセージ
    progress = pyqtSignal(str)  # 進捗メッセージ

    def __init__(self, current_dir):
        super().__init__()
        self.current_dir = current_dir

    def run(self):
        """スレッドで実行される処理"""
        try:
            # startup.sh をバックグラウンドで実行 (Appiumサーバー起動)
            print("[DEBUG] Appiumサーバー起動処理開始")
            self.progress.emit("Appiumサーバーを起動中...")
            startup_script = os.path.join(self.current_dir, "scripts", "startup.sh")
            print(f"[DEBUG] startup_script: {startup_script}")
            # Popenを使ってバックグラウンドで実行（終了を待たない）
            subprocess.Popen(
                ["sh", startup_script],
                cwd=self.current_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Appiumサーバーの起動を少し待つ
            time.sleep(3)
            self.progress.emit("Appiumサーバーを起動しました")

            # xcode_build.sh をバックグラウンドで実行
            print("[DEBUG] xcode_build.sh 実行開始")
            self.progress.emit("iPhoneにプログラム実行環境を構築中...")
            xcode_script = os.path.join(self.current_dir, "scripts", "xcode_build.sh")
            print(f"[DEBUG] xcode_script: {xcode_script}")

            # Popenで標準出力を監視しながら実行
            process = subprocess.Popen(
                ["sh", xcode_script],
                cwd=self.current_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # 「Testing started」メッセージを待つ（タイムアウト: 3分）
            success_message_found = False
            timeout = 180  # 3分（秒）
            start_time = time.time()

            print("[DEBUG] 'Testing started' メッセージを監視中...")

            try:
                while True:
                    # タイムアウトチェック
                    elapsed_time = time.time() - start_time
                    if elapsed_time > timeout:
                        print("[DEBUG] タイムアウト: 3分経過しても 'Testing started' が見つかりませんでした")
                        process.terminate()
                        self.finished.emit(False, "タイムアウト: xcode_build.sh の実行が3分以内に完了しませんでした")
                        return

                    # 非ブロッキングで標準出力をチェック（最大0.5秒待機）
                    remaining_time = timeout - elapsed_time
                    wait_time = min(0.5, remaining_time)

                    # selectを使って非ブロッキングで読み取り可能かチェック
                    ready, _, _ = select.select([process.stdout], [], [], wait_time)

                    if ready:
                        line = process.stdout.readline()
                        if line:
                            print(f"[DEBUG] xcode output: {line.strip()}")

                            # 「Testing started」が見つかったか確認
                            if "Testing started" in line:
                                print("[DEBUG] 'Testing started' メッセージを検出しました！")
                                success_message_found = True
                                break

                    # プロセスが終了していたらチェック
                    if process.poll() is not None:
                        # プロセスは終了したが、メッセージが見つからなかった
                        if not success_message_found:
                            print("[DEBUG] プロセスが終了しましたが 'Testing started' が見つかりませんでした")
                            self.finished.emit(False, "xcode_build.sh が 'Testing started' を出力せずに終了しました")
                            return
                        break

                if success_message_found:
                    print("[DEBUG] xcode_build.sh が正常に開始されました")
                    self.progress.emit("iPhoneとの接続が確立されました")

            except Exception as e:
                print(f"[DEBUG] xcode_build.sh 監視中にエラー: {e}")
                process.terminate()
                self.finished.emit(False, f"iPhoneとの接続環境構築中にエラーが発生しました: {str(e)}")
                return

            print("[DEBUG] iPhone接続処理成功 - finished.emit(True) を呼び出します")
            self.finished.emit(True, "iPhone接続処理が完了しました")
            print("[DEBUG] finished.emit(True) 呼び出し完了")

        except Exception as e:
            error_message = f"iPhone接続処理でエラーが発生しました: {str(e)}"
            print(f"[DEBUG] 例外発生: {error_message}")
            import traceback
            traceback.print_exc()
            self.finished.emit(False, error_message)
            print("[DEBUG] finished.emit(False) 呼び出し完了")

class MainWindow(QMainWindow):
    """メインウィンドウ"""

    def __init__(self):
        super().__init__()
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
        status_layout = QHBoxLayout()
        status_layout.addStretch()
        self.iphone_status_label = QLabel()
        self.iphone_status_label.setStyleSheet("font-size: 14px; padding: 2px;")
        self.update_iphone_status(0)  # 初期状態は未接続
        status_layout.addWidget(self.iphone_status_label)
        main_layout.addLayout(status_layout)

        # タイトル
        title_label = QLabel("ポケモンセンターオンライン 自動化ツール")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # iPhone接続ボタン
        iphone_button_layout = QHBoxLayout()
        iphone_button_layout.addStretch()
        self.iphone_connect_button = QPushButton("iPhone接続")
        self.iphone_connect_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 25px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.iphone_connect_button.clicked.connect(self.on_iphone_connect)
        iphone_button_layout.addWidget(self.iphone_connect_button)
        iphone_button_layout.addStretch()
        main_layout.addLayout(iphone_button_layout)

        # iPhone接続の注意書き
        note_label = QLabel("セットアップ済みのiPhoneをPCに繋いでから「iPhone接続」ボタンを押下することで、接続を確立してください。")
        note_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 0px 20px 5px 20px;")
        note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note_label.setWordWrap(True)
        main_layout.addWidget(note_label)

        # タブウィジェット作成
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # 各タブを作成
        self.create_lottery_tab()
        self.create_result_tab()
        self.create_payment_tab()
        self.create_account_tab()
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

    def update_iphone_status(self, connected_no):
        """iPhone接続ステータスを更新"""
        print(f"[DEBUG] update_iphone_status called: connected={connected_no}")
        if connected_no == 0:
            self.iphone_status_label.setText('<span style="color: #e74c3c; font-size: 18px;">●</span> <span>iPhone未接続</span>')
        elif connected_no == 1:
            self.iphone_status_label.setText('<span style="color: #f39c12; font-size: 18px;">●</span> <span>iPhone接続確認中</span>')
        else:
            self.iphone_status_label.setText('<span style="color: #27ae60; font-size: 18px;">●</span> <span>iPhone接続完了</span>')


    def create_lottery_tab(self):
        """1. 抽選実行タブ"""
        lottery_widget = QWidget()
        layout = QVBoxLayout()

        # 設定グループ
        settings_group = QGroupBox("実行設定")
        settings_layout = QVBoxLayout()

        # 開始行・終了行
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("開始行:"))
        self.lottery_start_row = QSpinBox()
        self.lottery_start_row.setRange(START_ROW_DEFAULT, MAX_ROW)
        self.lottery_start_row.setValue(START_ROW_DEFAULT)
        row_layout.addWidget(self.lottery_start_row)

        row_layout.addWidget(QLabel("終了行:"))
        self.lottery_end_row = QSpinBox()
        self.lottery_end_row.setRange(START_ROW_DEFAULT, MAX_ROW)
        self.lottery_end_row.setValue(10)
        row_layout.addWidget(self.lottery_end_row)
        row_layout.addStretch()
        settings_layout.addLayout(row_layout)

        # 書き込み列
        col_layout = QHBoxLayout()
        col_layout.addWidget(QLabel("抽選申込結果の書き込み先の列番号:"))
        self.lottery_write_col = QLineEdit()
        self.lottery_write_col.setPlaceholderText("例: AB")
        self.lottery_write_col.setMaximumWidth(100)
        col_layout.addWidget(self.lottery_write_col)
        col_layout.addStretch()
        settings_layout.addLayout(col_layout)

        # 上位件数
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("抽選申し込み上位件数:"))
        self.lottery_top_p = QSpinBox()
        self.lottery_top_p.setRange(1, 10)
        self.lottery_top_p.setValue(1)
        top_layout.addWidget(self.lottery_top_p)
        top_layout.addStretch()
        settings_layout.addLayout(top_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # ログ表示エリア
        log_group = QGroupBox("実行ログ")
        log_layout = QVBoxLayout()
        self.lottery_log = QTextEdit()
        self.lottery_log.setReadOnly(True)
        self.lottery_log.setPlaceholderText("実行ログがここに表示されます...")
        log_layout.addWidget(self.lottery_log)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # 実行ボタン
        button_layout = QHBoxLayout()
        start_button = QPushButton("抽選実行開始")
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        start_button.clicked.connect(self.on_lottery_start)
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

        lottery_widget.setLayout(layout)
        self.tabs.addTab(lottery_widget, "抽選実行")

    def create_result_tab(self):
        """2. 抽選結果取得タブ"""
        result_widget = QWidget()
        layout = QVBoxLayout()

        # 設定グループ
        settings_group = QGroupBox("実行設定")
        settings_layout = QVBoxLayout()

        # 開始行・終了行
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("開始行:"))
        self.result_start_row = QSpinBox()
        self.result_start_row.setRange(START_ROW_DEFAULT, MAX_ROW)
        self.result_start_row.setValue(START_ROW_DEFAULT)
        row_layout.addWidget(self.result_start_row)

        row_layout.addWidget(QLabel("終了行:"))
        self.result_end_row = QSpinBox()
        self.result_end_row.setRange(START_ROW_DEFAULT, MAX_ROW)
        self.result_end_row.setValue(10)
        row_layout.addWidget(self.result_end_row)
        row_layout.addStretch()
        settings_layout.addLayout(row_layout)

        # 書き込み列
        col_layout = QHBoxLayout()
        col_layout.addWidget(QLabel("結果取得の書き込み先の列番号:"))
        self.result_write_col = QLineEdit()
        self.result_write_col.setPlaceholderText("例: AB")
        self.result_write_col.setMaximumWidth(100)
        col_layout.addWidget(self.result_write_col)
        col_layout.addStretch()
        settings_layout.addLayout(col_layout)

        # 上位件数
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("結果取得上位件数:"))
        self.result_top_p = QSpinBox()
        self.result_top_p.setRange(1, 10)
        self.result_top_p.setValue(1)
        top_layout.addWidget(self.result_top_p)
        top_layout.addStretch()
        settings_layout.addLayout(top_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # ログ表示エリア
        log_group = QGroupBox("実行ログ")
        log_layout = QVBoxLayout()
        self.result_log = QTextEdit()
        self.result_log.setReadOnly(True)
        self.result_log.setPlaceholderText("実行ログがここに表示されます...")
        log_layout.addWidget(self.result_log)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # 実行ボタン
        button_layout = QHBoxLayout()
        start_button = QPushButton("結果取得開始")
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        start_button.clicked.connect(self.on_result_start)
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

        result_widget.setLayout(layout)
        self.tabs.addTab(result_widget, "結果取得")

    def create_payment_tab(self):
        """3. 決済処理タブ"""
        payment_widget = QWidget()
        layout = QVBoxLayout()

        # 設定グループ
        settings_group = QGroupBox("実行設定")
        settings_layout = QVBoxLayout()

        # 開始行・終了行
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("開始行:"))
        self.payment_start_row = QSpinBox()
        self.payment_start_row.setRange(START_ROW_DEFAULT, MAX_ROW)
        self.payment_start_row.setValue(START_ROW_DEFAULT)
        row_layout.addWidget(self.payment_start_row)

        row_layout.addWidget(QLabel("終了行:"))
        self.payment_end_row = QSpinBox()
        self.payment_end_row.setRange(START_ROW_DEFAULT, MAX_ROW)
        self.payment_end_row.setValue(10)
        row_layout.addWidget(self.payment_end_row)
        row_layout.addStretch()
        settings_layout.addLayout(row_layout)

        # 書き込み列
        col_layout = QHBoxLayout()
        col_layout.addWidget(QLabel("決済処理の書き込み先の列番号:"))
        self.payment_write_col = QLineEdit()
        self.payment_write_col.setPlaceholderText("例: AB")
        self.payment_write_col.setMaximumWidth(100)
        col_layout.addWidget(self.payment_write_col)
        col_layout.addStretch()
        settings_layout.addLayout(col_layout)

        # 上位件数
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("決済対象上位件数:"))
        self.payment_top_p = QSpinBox()
        self.payment_top_p.setRange(1, 10)
        self.payment_top_p.setValue(1)
        top_layout.addWidget(self.payment_top_p)
        top_layout.addStretch()
        settings_layout.addLayout(top_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # ログ表示エリア
        log_group = QGroupBox("実行ログ")
        log_layout = QVBoxLayout()
        self.payment_log = QTextEdit()
        self.payment_log.setReadOnly(True)
        self.payment_log.setPlaceholderText("実行ログがここに表示されます...")
        log_layout.addWidget(self.payment_log)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # 実行ボタン
        button_layout = QHBoxLayout()
        start_button = QPushButton("決済処理開始")
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        start_button.clicked.connect(self.on_payment_start)
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

        payment_widget.setLayout(layout)
        self.tabs.addTab(payment_widget, "決済処理")

    def create_account_tab(self):
        """4. アカウント作成タブ"""
        account_widget = QWidget()
        layout = QVBoxLayout()

        # 設定グループ
        settings_group = QGroupBox("実行設定")
        settings_layout = QVBoxLayout()

        # 開始行・終了行
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("開始行:"))
        self.account_start_row = QSpinBox()
        self.account_start_row.setRange(START_ROW_DEFAULT, MAX_ROW)
        self.account_start_row.setValue(START_ROW_DEFAULT)
        row_layout.addWidget(self.account_start_row)

        row_layout.addWidget(QLabel("終了行:"))
        self.account_end_row = QSpinBox()
        self.account_end_row.setRange(START_ROW_DEFAULT, MAX_ROW)
        self.account_end_row.setValue(10)
        row_layout.addWidget(self.account_end_row)
        row_layout.addStretch()
        settings_layout.addLayout(row_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # ログ表示エリア
        log_group = QGroupBox("実行ログ")
        log_layout = QVBoxLayout()
        self.account_log = QTextEdit()
        self.account_log.setReadOnly(True)
        self.account_log.setPlaceholderText("実行ログがここに表示されます...")
        log_layout.addWidget(self.account_log)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # 実行ボタン
        button_layout = QHBoxLayout()
        start_button = QPushButton("アカウント作成開始")
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        start_button.clicked.connect(self.on_account_start)
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

        account_widget.setLayout(layout)
        self.tabs.addTab(account_widget, "アカウント作成")

    def create_settings_tab(self):
        """5. 設定関連タブ"""
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
        """iPhone接続処理"""
        print("[DEBUG] on_iphone_connect() 呼び出し")
        # ボタンを無効化
        self.iphone_connect_button.setEnabled(False)
        self.statusBar().showMessage("iPhoneにプログラム実行環境を構築を構築します...")

        # 現在のディレクトリを取得
        current_dir = get_base_path()
        print(f"[DEBUG] current_dir: {current_dir}")

        # ワーカースレッドを作成して実行
        self.script_worker = ScriptWorker(current_dir)
        self.script_worker.progress.connect(self.on_script_progress)
        self.script_worker.finished.connect(self.on_script_finished)
        self.script_worker.start()
        print("[DEBUG] ScriptWorker.start() 呼び出し完了")

    def on_script_progress(self, message):
        """スクリプト実行の進捗を表示"""
        self.statusBar().showMessage(message, MSG_SHOW_TIME)
        self.update_iphone_status(1)  # 接続確認中

    def on_script_finished(self, success, message):
        """スクリプト実行完了時の処理"""
        print(f"[DEBUG] on_script_finished called: success={success}, message={message}")

        # ボタンを有効化
        self.iphone_connect_button.setEnabled(True)

        if success:
            print("[DEBUG] 接続成功 - ステータスを更新します")
            self.statusBar().showMessage("iPhoneとの接続を確立しました")
            # 接続成功時にステータスを更新
            self.update_iphone_status(2)
        else:
            print("[DEBUG] 接続失敗 - ステータスは未接続のまま")
            self.statusBar().showMessage("エラー: iPhone接続処理に失敗", MSG_SHOW_TIME)
            print(message)
            # エラーポップアップを表示
            QMessageBox.critical(self, "エラー", "iPhone接続処理に失敗しました。\niPhoneがケーブルで接続されているか、セットアップが完了していることを確認してください。")
            # 接続失敗時は未接続のまま
            self.update_iphone_status(0)

    def on_gmail_login(self):
        """Gmailログイン処理"""
        self.settings_log.append("Gmailログイン処理を開始します...\n")
        self.statusBar().showMessage("Gmailログイン処理中...", MSG_SHOW_TIME)
        # initialize_gmail_oauth(self.settings_log)
        self.statusBar().showMessage("Gmailログイン処理完了", MSG_SHOW_TIME)

    def on_lottery_start(self):
        """抽選実行開始"""
        start_row = self.lottery_start_row.value()
        end_row = self.lottery_end_row.value()
        write_col = self.lottery_write_col.text().strip()
        top_p = self.lottery_top_p.value()

        # 入力検証
        if not write_col:
            self.lottery_log.append("エラー: 書き込み列を入力してください\n")
            self.statusBar().showMessage("エラー: 書き込み列が未入力です", MSG_SHOW_TIME)
            return

        if start_row > end_row:
            self.lottery_log.append("エラー: 開始行は終了行以下にしてください\n")
            self.statusBar().showMessage("エラー: 行の範囲が不正です", MSG_SHOW_TIME)
            return

        message = f"抽選実行を開始します\n開始行: {start_row}\n終了行: {end_row}\n上位件数: {top_p}\n書き込み列: {write_col}\n"
        self.lottery_log.append(message)
        self.statusBar().showMessage("抽選実行中...", MSG_SHOW_TIME)

        try:
            user_info_list = test(start_row, end_row, write_col, top_p)
            self.lottery_log.append(f"✅ 抽選実行が完了しました。処理したユーザー数: {len(user_info_list)}\n")
            self.lottery_log.append("処理が完了しました\n")
            self.statusBar().showMessage("処理完了", MSG_SHOW_TIME)
        except Exception as e:
            error_message = f"エラーが発生しました: {str(e)}\n"
            self.lottery_log.append(error_message)
            self.statusBar().showMessage("エラー発生", MSG_SHOW_TIME)

    def on_result_start(self):
        """抽選結果取得開始"""
        start_row = self.result_start_row.value()
        end_row = self.result_end_row.value()
        write_col = self.result_write_col.text()
        top_p = self.result_top_p.value()

        # 入力検証
        if not write_col:
            self.result_log.append("エラー: 書き込み列を入力してください\n")
            self.statusBar().showMessage("エラー: 書き込み列が未入力です", MSG_SHOW_TIME)
            return

        if start_row > end_row:
            self.result_log.append("エラー: 開始行は終了行以下にしてください\n")
            self.statusBar().showMessage("エラー: 行の範囲が不正です", MSG_SHOW_TIME)
            return

        message = f"抽選結果取得を開始します\n開始行: {start_row}\n終了行: {end_row}\n書き込み列: {write_col}\n"
        self.result_log.append(message)
        self.statusBar().showMessage("抽選結果取得中...", MSG_SHOW_TIME)

    def on_payment_start(self):
        """決済処理開始"""
        start_row = self.payment_start_row.value()
        end_row = self.payment_end_row.value()
        write_col = self.payment_write_col.text()
        top_p = self.payment_top_p.value()

        # 入力検証
        if not write_col:
            self.payment_log.append("エラー: 書き込み列を入力してください\n")
            self.statusBar().showMessage("エラー: 書き込み列が未入力です", MSG_SHOW_TIME)
            return

        if start_row > end_row:
            self.payment_log.append("エラー: 開始行は終了行以下にしてください\n")
            self.statusBar().showMessage("エラー: 行の範囲が不正です", MSG_SHOW_TIME)
            return

        message = f"決済処理を開始します\n開始行: {start_row}\n終了行: {end_row}\n書き込み列: {write_col}\n上位件数: {top_p}\n"
        self.payment_log.append(message)
        self.statusBar().showMessage("決済処理中...", MSG_SHOW_TIME)

    def on_account_start(self):
        """アカウント作成開始"""
        start_row = self.account_start_row.value()
        end_row = self.account_end_row.value()

        # 入力検証
        if start_row > end_row:
            self.payment_log.append("エラー: 開始行は終了行以下にしてください\n")
            self.statusBar().showMessage("エラー: 行の範囲が不正です", MSG_SHOW_TIME)
            return

        message = f"アカウント作成を開始します\n開始行: {start_row}\n終了行: {end_row}\n"
        self.account_log.append(message)
        self.statusBar().showMessage("アカウント作成中...", MSG_SHOW_TIME)

    def on_stop(self):
        """停止"""
        self.statusBar().showMessage("停止しました", MSG_SHOW_TIME)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
