from PySide6.QtWidgets import QMessageBox
from components.setup_script.worker.script_worker import ScriptWorker
from components.setup_script.ui.iphone_connect_btn import update_iphone_status
from utils.common import get_base_path


def on_iphone_connect(main_window):
    """
    iPhone接続処理を開始

    Args:
        main_window: メインウィンドウのインスタンス
    """
    print("[DEBUG] on_iphone_connect() 呼び出し")
    # ボタンを無効化
    main_window.iphone_connect_button.setEnabled(False)
    main_window.statusBar().showMessage("iPhoneにプログラム実行環境を構築を構築します...")

    # 現在のディレクトリを取得
    current_dir = get_base_path()
    print(f"[DEBUG] current_dir: {current_dir}")

    # ワーカースレッドを作成して実行
    main_window.script_worker = ScriptWorker(current_dir)
    main_window.script_worker.progress.connect(lambda msg: on_script_progress(main_window, msg))
    main_window.script_worker.finished.connect(lambda success, msg: on_script_finished(main_window, success, msg))
    main_window.script_worker.start()
    print("[DEBUG] ScriptWorker.start() 呼び出し完了")


def on_script_progress(main_window, message):
    """
    スクリプト実行の進捗を表示

    Args:
        main_window: メインウィンドウのインスタンス
        message: 進捗メッセージ
    """
    MSG_SHOW_TIME = 5000  # ステータスメッセージ表示時間（ミリ秒）
    main_window.statusBar().showMessage(message, MSG_SHOW_TIME)
    update_iphone_status(main_window, 1)  # 接続確認中


def on_script_finished(main_window, success, message):
    """
    スクリプト実行完了時の処理

    Args:
        main_window: メインウィンドウのインスタンス
        success: 成功フラグ
        message: 結果メッセージ
    """
    MSG_SHOW_TIME = 5000  # ステータスメッセージ表示時間（ミリ秒）
    print(f"[DEBUG] on_script_finished called: success={success}, message={message}")

    # ボタンを有効化
    main_window.iphone_connect_button.setEnabled(True)

    if success:
        print("[DEBUG] 接続成功 - ステータスを更新します")
        main_window.statusBar().showMessage("iPhoneとの接続を確立しました")
        # 接続成功時にステータスを更新
        update_iphone_status(main_window, 2)
    else:
        print("[DEBUG] 接続失敗 - ステータスは未接続のまま")
        main_window.statusBar().showMessage("エラー: iPhone接続処理に失敗", MSG_SHOW_TIME)
        print(message)
        # エラーポップアップを表示
        QMessageBox.critical(
            main_window,
            "エラー",
            "iPhone接続処理に失敗しました。\niPhoneがケーブルで接続されているか、セットアップが完了していることを確認してください。"
        )
        # 接続失敗時は未接続のまま
        update_iphone_status(main_window, 0)
