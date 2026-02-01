from components.shipping_status.worker.shipping_status_worker import ShippingStatusWorker


def on_shipping_status_start(main_window, msg_show_time):
    """
    発送ステータス確認開始処理

    Args:
        main_window: メインウィンドウのインスタンス
        msg_show_time: ステータスメッセージ表示時間（ミリ秒）
    """
    start_row = main_window.shipping_start_row.value()
    end_row = main_window.shipping_end_row.value()
    write_col = main_window.shipping_write_col.text()
    top_p = main_window.shipping_top_p.value()

    # 入力検証
    if not write_col:
        main_window.shipping_log.append("エラー: 書き込み列を入力してください\n")
        main_window.statusBar().showMessage("エラー: 書き込み列が未入力です", msg_show_time)
        return

    if start_row > end_row:
        main_window.shipping_log.append("エラー: 開始行は終了行以下にしてください\n")
        main_window.statusBar().showMessage("エラー: 行の範囲が不正です", msg_show_time)
        return

    message = f"発送ステータス確認を開始します\n開始行: {start_row}\n終了行: {end_row}\n書き込み列: {write_col}\n上位件数: {top_p}\n"
    main_window.shipping_log.append(message)
    main_window.statusBar().showMessage("発送ステータス確認中...", msg_show_time)

    # ワーカースレッドを作成して実行
    main_window.shipping_worker = ShippingStatusWorker(start_row, end_row, write_col, top_p)
    main_window.shipping_worker.progress.connect(lambda msg: on_shipping_progress(main_window, msg))
    main_window.shipping_worker.finished.connect(lambda success, msg: on_shipping_finished(main_window, success, msg, msg_show_time))
    main_window.shipping_worker.start()


def on_shipping_progress(main_window, message):
    """
    発送ステータス確認の進捗を表示

    Args:
        main_window: メインウィンドウのインスタンス
        message: 進捗メッセージ
    """
    main_window.shipping_log.append(message)


def on_shipping_finished(main_window, success, message, msg_show_time):
    """
    発送ステータス確認完了時の処理

    Args:
        main_window: メインウィンドウのインスタンス
        success: 成功フラグ
        message: メッセージ
        msg_show_time: ステータスメッセージ表示時間（ミリ秒）
    """
    if success:
        main_window.shipping_log.append(f"✅ {message}\n")
        main_window.statusBar().showMessage("処理完了", msg_show_time)
    else:
        main_window.shipping_log.append(f"❌ {message}\n")
        main_window.statusBar().showMessage("エラー発生", msg_show_time)
    main_window.shipping_worker = None  # ワーカーをクリア


def on_shipping_stop(main_window, msg_show_time):
    """
    発送ステータス確認停止処理

    Args:
        main_window: メインウィンドウのインスタンス
        msg_show_time: ステータスメッセージ表示時間（ミリ秒）
    """
    if main_window.shipping_worker and main_window.shipping_worker.isRunning():
        main_window.shipping_worker.stop()
        main_window.shipping_worker.quit()
        main_window.shipping_worker.wait()  # スレッドが終了するまで待つ
        main_window.shipping_log.append("⚠️ 発送ステータス確認を停止しました\n")
        main_window.statusBar().showMessage("停止しました", msg_show_time)
        main_window.shipping_worker = None
