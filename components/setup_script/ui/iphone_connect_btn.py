from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


def create_iphone_status_label(main_window):
    """
    iPhone接続ステータスラベルを作成

    Args:
        main_window: メインウィンドウのインスタンス

    Returns:
        QHBoxLayout: ステータスラベルを含むレイアウト
    """
    status_layout = QHBoxLayout()
    status_layout.addStretch()
    main_window.iphone_status_label = QLabel()
    main_window.iphone_status_label.setStyleSheet("font-size: 14px; padding: 2px;")
    # 初期状態は未接続（0）
    update_iphone_status(main_window, 0)
    status_layout.addWidget(main_window.iphone_status_label)
    return status_layout


def create_iphone_connect_button(main_window):
    """
    iPhone接続ボタンと注意書きを含むレイアウトを作成

    Args:
        main_window: メインウィンドウのインスタンス

    Returns:
        tuple: (ボタンレイアウト, 注意書きラベル)
    """
    # iPhone接続ボタン
    iphone_button_layout = QHBoxLayout()
    iphone_button_layout.addStretch()
    main_window.iphone_connect_button = QPushButton("iPhone接続")
    main_window.iphone_connect_button.setStyleSheet("""
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
    main_window.iphone_connect_button.clicked.connect(main_window.on_iphone_connect)
    iphone_button_layout.addWidget(main_window.iphone_connect_button)
    iphone_button_layout.addStretch()

    # iPhone接続の注意書き
    note_label = QLabel("セットアップ済みのiPhoneをPCに繋いでから「iPhone接続」ボタンを押下することで、接続を確立してください。")
    note_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 0px 20px 5px 20px;")
    note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    note_label.setWordWrap(True)

    return iphone_button_layout, note_label


def update_iphone_status(main_window, connected_no):
    """
    iPhone接続ステータスを更新

    Args:
        main_window: メインウィンドウのインスタンス
        connected_no: 接続状態（0: 未接続, 1: 接続確認中, 2: 接続完了）
    """
    print(f"[DEBUG] update_iphone_status called: connected={connected_no}")
    if connected_no == 0:
        main_window.iphone_status_label.setText('<span style="color: #e74c3c; font-size: 18px;">●</span> <span>iPhone未接続</span>')
    elif connected_no == 1:
        main_window.iphone_status_label.setText('<span style="color: #f39c12; font-size: 18px;">●</span> <span>iPhone接続確認中</span>')
    else:
        main_window.iphone_status_label.setText('<span style="color: #27ae60; font-size: 18px;">●</span> <span>iPhone接続完了</span>')
