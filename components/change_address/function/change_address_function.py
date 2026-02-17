from components.change_address.worker.change_address_worker import ChangeAddressWorker


def on_change_address_start(main_window, msg_show_time):
    """
    住所変更処理開始

    Args:
        main_window: メインウィンドウのインスタンス
        msg_show_time: ステータスメッセージ表示時間（ミリ秒）
    """
    start_row = main_window.change_address_start_row.value()
    end_row = main_window.change_address_end_row.value()

    # 入力検証
    if start_row > end_row:
        main_window.change_address_log.append("エラー: 開始行は終了行以下にしてください\n")
        main_window.statusBar().showMessage("エラー: 行の範囲が不正です", msg_show_time)
        return

    message = f"住所変更処理を開始します\n開始行: {start_row}\n終了行: {end_row}\n"
    main_window.change_address_log.append(message)
    main_window.statusBar().showMessage("住所変更処理中...", msg_show_time)

    # ワーカースレッドを作成して実行
    main_window.change_address_worker = ChangeAddressWorker(
        start_row=start_row,
        end_row=end_row
    )
    main_window.change_address_worker.progress.connect(
        lambda msg: on_change_address_progress(main_window, msg)
    )
    main_window.change_address_worker.finished.connect(
        lambda success, msg: on_change_address_finished(main_window, success, msg, msg_show_time)
    )
    main_window.change_address_worker.start()


def on_change_address_progress(main_window, message):
    """
    住所変更処理の進捗を表示

    Args:
        main_window: メインウィンドウのインスタンス
        message: 進捗メッセージ
    """
    main_window.change_address_log.append(message)


def on_change_address_finished(main_window, success, message, msg_show_time):
    """
    住所変更処理完了時の処理

    Args:
        main_window: メインウィンドウのインスタンス
        success: 成功フラグ
        message: 結果メッセージ
        msg_show_time: ステータスメッセージ表示時間（ミリ秒）
    """
    if success:
        main_window.change_address_log.append(f"\n✅ {message}\n")
        main_window.statusBar().showMessage("処理完了", msg_show_time)
    else:
        main_window.change_address_log.append(f"\n❌ {message}\n")
        main_window.statusBar().showMessage("エラー発生", msg_show_time)
    main_window.change_address_worker = None


def on_change_address_stop(main_window, msg_show_time):
    """
    住所変更処理停止処理

    Args:
        main_window: メインウィンドウのインスタンス
        msg_show_time: ステータスメッセージ表示時間（ミリ秒）
    """
    if main_window.change_address_worker and main_window.change_address_worker.isRunning():
        main_window.change_address_worker.stop()
        main_window.change_address_worker.quit()
        main_window.change_address_worker.wait()  # スレッドが終了するまで待つ
        main_window.change_address_log.append("⚠️ 住所変更処理を停止しました\n")
        main_window.statusBar().showMessage("停止しました", msg_show_time)
