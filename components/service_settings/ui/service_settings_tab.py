from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QGroupBox
)


def create_service_settings_tab(parent):
    """
    サービス設定タブを作成する

    Args:
        parent: 親ウィンドウ

    Returns:
        settings_widget: 設定タブのウィジェット
    """
    settings_widget = QWidget()
    layout = QVBoxLayout()

    # Gmail設定グループ
    settings_group = QGroupBox("Gmail設定")
    settings_layout = QVBoxLayout()

    # Gmailログインボタン
    button_layout = QHBoxLayout()

    # JSONファイルアップロードボタン
    upload_json_button = QPushButton("OAUTH設定ファイルのアップロード")
    upload_json_button.clicked.connect(parent.on_upload_json)
    button_layout.addWidget(upload_json_button)

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
    gmail_login_button.clicked.connect(parent.on_gmail_login)
    button_layout.addWidget(gmail_login_button)

    button_layout.addStretch()
    settings_layout.addLayout(button_layout)

    settings_group.setLayout(settings_layout)
    layout.addWidget(settings_group)

    # スプレッドシート設定グループ
    spreadsheet_group = QGroupBox("スプレッドシート設定")
    spreadsheet_layout = QVBoxLayout()

    # Credentialsファイルアップロードボタン
    credentials_layout = QHBoxLayout()
    upload_credentials_button = QPushButton("Credentialsファイルのアップロード")
    upload_credentials_button.clicked.connect(parent.on_upload_credentials)
    credentials_layout.addWidget(upload_credentials_button)
    credentials_layout.addStretch()
    spreadsheet_layout.addLayout(credentials_layout)

    # Sheet ID入力フォーム
    sheet_id_layout = QHBoxLayout()
    sheet_id_layout.addWidget(QLabel("Sheet ID:"))
    parent.sheet_id_input = QLineEdit()
    parent.sheet_id_input.setPlaceholderText("スプレッドシートのIDを入力")
    sheet_id_layout.addWidget(parent.sheet_id_input)

    save_sheet_id_button = QPushButton("保存")
    save_sheet_id_button.clicked.connect(parent.on_save_sheet_id)
    sheet_id_layout.addWidget(save_sheet_id_button)
    spreadsheet_layout.addLayout(sheet_id_layout)

    # 接続確認ボタン
    test_connection_layout = QHBoxLayout()
    test_connection_button = QPushButton("スプレッドシート接続確認")
    test_connection_button.setStyleSheet("""
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
    test_connection_button.clicked.connect(parent.on_test_spreadsheet_connection)
    test_connection_layout.addWidget(test_connection_button)
    test_connection_layout.addStretch()
    spreadsheet_layout.addLayout(test_connection_layout)

    spreadsheet_group.setLayout(spreadsheet_layout)
    layout.addWidget(spreadsheet_group)

    # ログ表示エリア
    log_group = QGroupBox("実行ログ")
    log_layout = QVBoxLayout()
    parent.settings_log = QTextEdit()
    parent.settings_log.setReadOnly(True)
    parent.settings_log.setPlaceholderText("実行ログがここに表示されます...")
    log_layout.addWidget(parent.settings_log)
    log_group.setLayout(log_layout)
    layout.addWidget(log_group)

    layout.addStretch()
    settings_widget.setLayout(layout)

    return settings_widget
