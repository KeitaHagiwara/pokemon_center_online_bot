"""
アカウント作成の機能関数
"""
from components.create_user.worker.create_user_worker import CreateUserWorker

def on_account_start(main_window, msg_show_time):
    """
    アカウント作成開始

    Args:
        main_window: MainWindowインスタンス
        msg_show_time: ステータスメッセージの表示時間
    """
    start_row = main_window.account_start_row.value()
    end_row = main_window.account_end_row.value()

    # 入力検証
    if start_row > end_row:
        main_window.account_log.append("エラー: 開始行は終了行以下にしてください\n")
        main_window.statusBar().showMessage("エラー: 行の範囲が不正です", msg_show_time)
        return

    message = f"アカウント作成を開始します\n開始行: {start_row}\n終了行: {end_row}\n"
    main_window.account_log.append(message)
    main_window.statusBar().showMessage("アカウント作成中...", msg_show_time)

    # ワーカー開始
    main_window.account_worker = CreateUserWorker(
        start_row=start_row,
        end_row=end_row,
        stop_check_callback=lambda: getattr(main_window, 'account_stop_flag', False)
    )
    main_window.account_worker.progress.connect(lambda msg: on_account_progress(main_window, msg))
    main_window.account_worker.finished.connect(lambda success, msg: on_account_finished(main_window, success, msg, msg_show_time))
    main_window.account_worker.start()

def on_account_progress(main_window, message):
    """
    アカウント作成の進捗を表示

    Args:
        main_window: MainWindowインスタンス
        message: 進捗メッセージ
    """
    main_window.account_log.append(message)

def on_account_finished(main_window, success, message, msg_show_time):
    """
    アカウント作成完了時の処理

    Args:
        main_window: MainWindowインスタンス
        success: 成功フラグ
        message: 完了メッセージ
        msg_show_time: ステータスメッセージの表示時間
    """
    if success:
        main_window.account_log.append(f"\n✅ {message}\n")
        main_window.statusBar().showMessage("処理完了", msg_show_time)
    else:
        main_window.account_log.append(f"\n❌ {message}\n")
        main_window.statusBar().showMessage("エラー発生", msg_show_time)
    main_window.account_worker = None

def on_account_stop(main_window, msg_show_time):
    """
    アカウント作成停止

    Args:
        main_window: MainWindowインスタンス
        msg_show_time: ステータスメッセージの表示時間
    """
    if main_window.account_worker and main_window.account_worker.isRunning():
        main_window.account_worker.stop()
        main_window.account_worker.quit()
        main_window.account_worker.wait()
        main_window.account_log.append("⚠️ アカウント作成を停止しました\n")
        main_window.statusBar().showMessage("停止しました", msg_show_time)
