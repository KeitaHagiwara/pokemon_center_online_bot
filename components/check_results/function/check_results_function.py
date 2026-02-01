from components.check_results.worker.check_results_worker import CheckResultsWorker


def on_result_start(main_window, msg_show_time):
    """
    抽選結果取得開始処理

    Args:
        main_window: メインウィンドウのインスタンス
        msg_show_time: ステータスメッセージ表示時間(ミリ秒)
    """
    start_row = main_window.result_start_row.value()
    end_row = main_window.result_end_row.value()
    write_col = main_window.result_write_col.text().strip()
    top_p = main_window.result_top_p.value()

    # 入力検証
    if not write_col:
        main_window.result_log.append("エラー: 書き込み列を入力してください\n")
        main_window.statusBar().showMessage("エラー: 書き込み列が未入力です", msg_show_time)
        return

    if start_row > end_row:
        main_window.result_log.append("エラー: 開始行は終了行以下にしてください\n")
        main_window.statusBar().showMessage("エラー: 行の範囲が不正です", msg_show_time)
        return

    message = f"抽選結果取得を開始します\n開始行: {start_row}\n終了行: {end_row}\n上位件数: {top_p}\n書き込み列: {write_col}\n"
    main_window.result_log.append(message)
    main_window.statusBar().showMessage("抽選結果取得中...", msg_show_time)

    # ワーカースレッドを作成して実行
    main_window.result_worker = CheckResultsWorker(
        start_row=start_row,
        end_row=end_row,
        write_col=write_col,
        top_p=top_p,
        stop_check_callback=lambda: getattr(main_window, 'result_stop_flag', False)
    )
    main_window.result_worker.progress.connect(lambda msg: on_result_progress(main_window, msg))
    main_window.result_worker.finished.connect(lambda success, msg: on_result_finished(main_window, success, msg, msg_show_time))
    main_window.result_worker.start()


def on_result_progress(main_window, message):
    """
    抽選結果取得の進捗を表示

    Args:
        main_window: メインウィンドウのインスタンス
        message: 進捗メッセージ
    """
    main_window.result_log.append(message)

def on_result_finished(main_window, success, message, msg_show_time):
    """
    抽選結果取得完了時の処理

    Args:
        main_window: メインウィンドウのインスタンス
        success: 成功フラグ
        message: 結果メッセージ
        msg_show_time: ステータスメッセージ表示時間(ミリ秒)
    """
    if success:
        main_window.result_log.append(f"\n✅ {message}\n")
        main_window.statusBar().showMessage("処理完了", msg_show_time)
    else:
        main_window.result_log.append(f"\n❌ {message}\n")
        main_window.statusBar().showMessage("エラー発生", msg_show_time)
    main_window.result_worker = None


def on_result_stop(main_window, msg_show_time):
    """
    抽選結果取得停止処理

    Args:
        main_window: メインウィンドウのインスタンス
        msg_show_time: ステータスメッセージ表示時間(ミリ秒)
    """
    if main_window.result_worker and main_window.result_worker.isRunning():
        main_window.result_worker.stop()
        main_window.result_worker.quit()
        main_window.result_worker.wait()  # スレッドが終了するまで待つ
        main_window.result_log.append("⚠️ 抽選結果取得を停止しました\n")
        main_window.statusBar().showMessage("停止しました", msg_show_time)
