from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QSpinBox, QGroupBox
)


def create_apply_lottery_tab(main_window, start_row_default, max_row):
    """
    抽選実行タブのUIを作成

    Args:
        main_window: メインウィンドウのインスタンス
        start_row_default: 開始行のデフォルト値
        max_row: 最大行数

    Returns:
        QWidget: 抽選実行タブのウィジェット
    """
    lottery_widget = QWidget()
    layout = QVBoxLayout()

    # 設定グループ
    settings_group = QGroupBox("実行設定")
    settings_layout = QVBoxLayout()

    # 開始行・終了行
    row_layout = QHBoxLayout()
    row_layout.addWidget(QLabel("開始行:"))
    main_window.lottery_start_row = QSpinBox()
    main_window.lottery_start_row.setRange(start_row_default, max_row)
    main_window.lottery_start_row.setValue(start_row_default)
    row_layout.addWidget(main_window.lottery_start_row)

    row_layout.addWidget(QLabel("終了行:"))
    main_window.lottery_end_row = QSpinBox()
    main_window.lottery_end_row.setRange(start_row_default, max_row)
    main_window.lottery_end_row.setValue(10)
    row_layout.addWidget(main_window.lottery_end_row)
    row_layout.addStretch()
    settings_layout.addLayout(row_layout)

    # 書き込み列
    col_layout = QHBoxLayout()
    col_layout.addWidget(QLabel("抽選申込結果の書き込み先の列番号:"))
    main_window.lottery_write_col = QLineEdit()
    main_window.lottery_write_col.setPlaceholderText("例: AB")
    main_window.lottery_write_col.setMaximumWidth(100)
    col_layout.addWidget(main_window.lottery_write_col)
    col_layout.addStretch()
    settings_layout.addLayout(col_layout)

    # 上位件数
    top_layout = QHBoxLayout()
    top_layout.addWidget(QLabel("抽選申し込み上位件数:"))
    main_window.lottery_top_p = QSpinBox()
    main_window.lottery_top_p.setRange(1, 10)
    main_window.lottery_top_p.setValue(1)
    top_layout.addWidget(main_window.lottery_top_p)
    top_layout.addStretch()
    settings_layout.addLayout(top_layout)

    settings_group.setLayout(settings_layout)
    layout.addWidget(settings_group)

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
    start_button.clicked.connect(main_window.on_lottery_start)
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
    stop_button.clicked.connect(main_window.on_lottery_stop)
    button_layout.addWidget(stop_button)
    button_layout.addStretch()
    layout.addLayout(button_layout)

    # ログ表示エリア
    log_group = QGroupBox("実行ログ")
    log_layout = QVBoxLayout()
    main_window.lottery_log = QTextEdit()
    main_window.lottery_log.setReadOnly(True)
    main_window.lottery_log.setPlaceholderText("実行ログがここに表示されます...")
    log_layout.addWidget(main_window.lottery_log)
    log_group.setLayout(log_layout)
    layout.addWidget(log_group)

    lottery_widget.setLayout(layout)
    return lottery_widget
