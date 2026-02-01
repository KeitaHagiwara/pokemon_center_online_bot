from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QSpinBox, QGroupBox
)


def create_shipping_status_tab(main_window, START_ROW_DEFAULT, MAX_ROW):
    """発送ステータス確認タブのUIを作成"""
    shipping_widget = QWidget()
    layout = QVBoxLayout()

    # 設定グループ
    settings_group = QGroupBox("実行設定")
    settings_layout = QVBoxLayout()

    # 開始行・終了行
    row_layout = QHBoxLayout()
    row_layout.addWidget(QLabel("開始行:"))
    main_window.shipping_start_row = QSpinBox()
    main_window.shipping_start_row.setRange(START_ROW_DEFAULT, MAX_ROW)
    main_window.shipping_start_row.setValue(START_ROW_DEFAULT)
    row_layout.addWidget(main_window.shipping_start_row)

    row_layout.addWidget(QLabel("終了行:"))
    main_window.shipping_end_row = QSpinBox()
    main_window.shipping_end_row.setRange(START_ROW_DEFAULT, MAX_ROW)
    main_window.shipping_end_row.setValue(10)
    row_layout.addWidget(main_window.shipping_end_row)
    row_layout.addStretch()
    settings_layout.addLayout(row_layout)

    # 書き込み列
    col_layout = QHBoxLayout()
    col_layout.addWidget(QLabel("発送ステータスの書き込み先の列番号:"))
    main_window.shipping_write_col = QLineEdit()
    main_window.shipping_write_col.setPlaceholderText("例: AB")
    main_window.shipping_write_col.setMaximumWidth(100)
    col_layout.addWidget(main_window.shipping_write_col)
    col_layout.addStretch()
    settings_layout.addLayout(col_layout)

    # 上位件数
    top_layout = QHBoxLayout()
    top_layout.addWidget(QLabel("確認対象上位件数:"))
    main_window.shipping_top_p = QSpinBox()
    main_window.shipping_top_p.setRange(1, 10)
    main_window.shipping_top_p.setValue(1)
    top_layout.addWidget(main_window.shipping_top_p)
    top_layout.addStretch()
    settings_layout.addLayout(top_layout)

    settings_group.setLayout(settings_layout)
    layout.addWidget(settings_group)

    # ログ表示エリア
    log_group = QGroupBox("実行ログ")
    log_layout = QVBoxLayout()
    main_window.shipping_log = QTextEdit()
    main_window.shipping_log.setReadOnly(True)
    main_window.shipping_log.setPlaceholderText("実行ログがここに表示されます...")
    log_layout.addWidget(main_window.shipping_log)
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
    start_button.clicked.connect(main_window.on_shipping_status_start)
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
    stop_button.clicked.connect(main_window.on_shipping_stop)
    button_layout.addWidget(stop_button)
    button_layout.addStretch()
    layout.addLayout(button_layout)

    shipping_widget.setLayout(layout)
    return shipping_widget
