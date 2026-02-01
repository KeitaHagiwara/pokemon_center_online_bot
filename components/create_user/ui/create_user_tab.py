"""
アカウント作成タブのUI作成
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QSpinBox, QTextEdit, QPushButton
)

def create_create_user_tab(main_window, start_row_default, max_row):
    """
    アカウント作成タブを作成

    Args:
        main_window: MainWindowインスタンス
        start_row_default: 開始行のデフォルト値
        max_row: 行の最大値

    Returns:
        QWidget: アカウント作成タブウィジェット
    """
    account_widget = QWidget()
    layout = QVBoxLayout()

    # 設定グループ
    settings_group = QGroupBox("実行設定")
    settings_layout = QVBoxLayout()

    # 開始行・終了行
    row_layout = QHBoxLayout()
    row_layout.addWidget(QLabel("開始行:"))
    main_window.account_start_row = QSpinBox()
    main_window.account_start_row.setRange(start_row_default, max_row)
    main_window.account_start_row.setValue(start_row_default)
    row_layout.addWidget(main_window.account_start_row)

    row_layout.addWidget(QLabel("終了行:"))
    main_window.account_end_row = QSpinBox()
    main_window.account_end_row.setRange(start_row_default, max_row)
    main_window.account_end_row.setValue(10)
    row_layout.addWidget(main_window.account_end_row)
    row_layout.addStretch()
    settings_layout.addLayout(row_layout)

    settings_group.setLayout(settings_layout)
    layout.addWidget(settings_group)

    # ログ表示エリア
    log_group = QGroupBox("実行ログ")
    log_layout = QVBoxLayout()
    main_window.account_log = QTextEdit()
    main_window.account_log.setReadOnly(True)
    main_window.account_log.setPlaceholderText("実行ログがここに表示されます...")
    log_layout.addWidget(main_window.account_log)
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
    start_button.clicked.connect(main_window.on_account_start)
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
    stop_button.clicked.connect(main_window.on_account_stop)
    button_layout.addWidget(stop_button)
    button_layout.addStretch()
    layout.addLayout(button_layout)

    account_widget.setLayout(layout)
    return account_widget
