from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QSpinBox, QGroupBox
)
from PySide6.QtCore import Qt


def create_change_address_tab(main_window, start_row_default, max_row):
    """
    住所変更タブを作成

    Args:
        main_window: メインウィンドウのインスタンス
        start_row_default: 開始行のデフォルト値
        max_row: 最大行数

    Returns:
        QWidget: 住所変更タブ
    """
    tab = QWidget()
    layout = QVBoxLayout()
    tab.setLayout(layout)

    # 入力グループ
    input_group = QGroupBox("実行設定")
    input_layout = QVBoxLayout()
    input_group.setLayout(input_layout)

    # 開始行・終了行
    row_layout = QHBoxLayout()
    row_layout.addWidget(QLabel("開始行:"))
    main_window.change_address_start_row = QSpinBox()
    main_window.change_address_start_row.setRange(start_row_default, max_row)
    main_window.change_address_start_row.setValue(start_row_default)
    row_layout.addWidget(main_window.change_address_start_row)

    row_layout.addWidget(QLabel("終了行:"))
    main_window.change_address_end_row = QSpinBox()
    main_window.change_address_end_row.setRange(start_row_default, max_row)
    main_window.change_address_end_row.setValue(start_row_default)
    row_layout.addWidget(main_window.change_address_end_row)
    row_layout.addStretch()

    input_layout.addLayout(row_layout)
    layout.addWidget(input_group)

    # 実行ボタン
    button_layout = QHBoxLayout()
    start_button = QPushButton("住所変更実行開始")
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
    start_button.clicked.connect(main_window.on_change_address_start)
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
    stop_button.clicked.connect(main_window.on_change_address_stop)
    button_layout.addWidget(stop_button)
    button_layout.addStretch()
    layout.addLayout(button_layout)

    # ログ表示エリア
    log_group = QGroupBox("実行ログ")
    log_layout = QVBoxLayout()
    main_window.change_address_log = QTextEdit()
    main_window.change_address_log.setReadOnly(True)
    main_window.change_address_log.setPlaceholderText("実行ログがここに表示されます...")
    log_layout.addWidget(main_window.change_address_log)
    log_group.setLayout(log_layout)
    layout.addWidget(log_group)

    return tab
