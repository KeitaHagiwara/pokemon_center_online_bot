"""
決済処理タブのUI作成
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QSpinBox, QLineEdit, QTextEdit, QPushButton
)

def create_make_payment_tab(main_window, start_row_default, max_row):
    """
    決済処理タブを作成

    Args:
        main_window: MainWindowインスタンス
        start_row_default: 開始行のデフォルト値
        max_row: 行の最大値

    Returns:
        QWidget: 決済処理タブウィジェット
    """
    payment_widget = QWidget()
    layout = QVBoxLayout()

    # 設定グループ
    settings_group = QGroupBox("実行設定")
    settings_layout = QVBoxLayout()

    # 開始行・終了行
    row_layout = QHBoxLayout()
    row_layout.addWidget(QLabel("開始行:"))
    main_window.payment_start_row = QSpinBox()
    main_window.payment_start_row.setRange(start_row_default, max_row)
    main_window.payment_start_row.setValue(start_row_default)
    row_layout.addWidget(main_window.payment_start_row)

    row_layout.addWidget(QLabel("終了行:"))
    main_window.payment_end_row = QSpinBox()
    main_window.payment_end_row.setRange(start_row_default, max_row)
    main_window.payment_end_row.setValue(10)
    row_layout.addWidget(main_window.payment_end_row)
    row_layout.addStretch()
    settings_layout.addLayout(row_layout)

    # 書き込み列
    col_layout = QHBoxLayout()
    col_layout.addWidget(QLabel("決済処理の書き込み先の列番号:"))
    main_window.payment_write_col = QLineEdit()
    main_window.payment_write_col.setPlaceholderText("例: AB")
    main_window.payment_write_col.setMaximumWidth(100)
    col_layout.addWidget(main_window.payment_write_col)
    col_layout.addStretch()
    settings_layout.addLayout(col_layout)

    # 上位件数
    top_layout = QHBoxLayout()
    top_layout.addWidget(QLabel("決済対象上位件数:"))
    main_window.payment_top_p = QSpinBox()
    main_window.payment_top_p.setRange(1, 10)
    main_window.payment_top_p.setValue(1)
    top_layout.addWidget(main_window.payment_top_p)
    top_layout.addStretch()
    settings_layout.addLayout(top_layout)

    settings_group.setLayout(settings_layout)
    layout.addWidget(settings_group)

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
    start_button.clicked.connect(main_window.on_payment_start)
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
    stop_button.clicked.connect(main_window.on_payment_stop)
    button_layout.addWidget(stop_button)
    button_layout.addStretch()
    layout.addLayout(button_layout)

    # ログ表示エリア
    log_group = QGroupBox("実行ログ")
    log_layout = QVBoxLayout()
    main_window.payment_log = QTextEdit()
    main_window.payment_log.setReadOnly(True)
    main_window.payment_log.setPlaceholderText("実行ログがここに表示されます...")
    log_layout.addWidget(main_window.payment_log)
    log_group.setLayout(log_layout)
    layout.addWidget(log_group)

    payment_widget.setLayout(layout)
    return payment_widget
