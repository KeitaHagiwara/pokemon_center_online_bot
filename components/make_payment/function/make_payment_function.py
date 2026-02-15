"""
決済処理の機能関数
"""
from components.make_payment.worker.make_payment_worker import MakePaymentWorker

def on_payment_start(main_window, msg_show_time):
    """
    決済処理開始

    Args:
        main_window: MainWindowインスタンス
        msg_show_time: ステータスメッセージの表示時間
    """
    start_row = main_window.payment_start_row.value()
    end_row = main_window.payment_end_row.value()
    write_col = main_window.payment_write_col.text()
    top_p = main_window.payment_top_p.value()

    # 入力検証
    if not write_col:
        main_window.payment_log.append("エラー: 書き込み列を入力してください\n")
        main_window.statusBar().showMessage("エラー: 書き込み列が未入力です", msg_show_time)
        return

    if start_row > end_row:
        main_window.payment_log.append("エラー: 開始行は終了行以下にしてください\n")
        main_window.statusBar().showMessage("エラー: 行の範囲が不正です", msg_show_time)
        return

    message = f"決済処理を開始します\n開始行: {start_row}\n終了行: {end_row}\n書き込み列: {write_col}\n上位件数: {top_p}\n"
    main_window.payment_log.append(message)
    main_window.statusBar().showMessage("決済処理中...", msg_show_time)

    # ワーカー開始
    main_window.payment_worker = MakePaymentWorker(
        start_row=start_row,
        end_row=end_row,
        write_col=write_col,
        top_p=top_p
    )
    main_window.payment_worker.progress.connect(lambda msg: on_payment_progress(main_window, msg))
    main_window.payment_worker.finished.connect(lambda success, msg: on_payment_finished(main_window, success, msg, msg_show_time))
    main_window.payment_worker.start()

def on_payment_progress(main_window, message):
    """
    決済処理の進捗を表示

    Args:
        main_window: MainWindowインスタンス
        message: 進捗メッセージ
    """
    main_window.payment_log.append(message)

def on_payment_finished(main_window, success, message, msg_show_time):
    """
    決済処理完了時の処理

    Args:
        main_window: MainWindowインスタンス
        success: 成功フラグ
        message: 完了メッセージ
        msg_show_time: ステータスメッセージの表示時間
    """
    if success:
        main_window.payment_log.append(f"\n✅ {message}\n")
        main_window.statusBar().showMessage("処理完了", msg_show_time)
    else:
        main_window.payment_log.append(f"\n❌ {message}\n")
        main_window.statusBar().showMessage("エラー発生", msg_show_time)
    main_window.payment_worker = None

def on_payment_stop(main_window, msg_show_time):
    """
    決済処理停止

    Args:
        main_window: MainWindowインスタンス
        msg_show_time: ステータスメッセージの表示時間
    """
    if main_window.payment_worker and main_window.payment_worker.isRunning():
        main_window.payment_worker.stop()
        main_window.payment_worker.quit()
        main_window.payment_worker.wait()  # スレッドが終了するまで待つ
        main_window.payment_log.append("⚠️ 決済処理を停止しました\n")
        main_window.statusBar().showMessage("停止しました", msg_show_time)
        main_window.payment_worker = None
