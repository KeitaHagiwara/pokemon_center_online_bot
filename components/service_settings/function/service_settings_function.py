"""
サービス設定関連の関数
Gmail設定とスプレッドシート設定の処理を含む
"""
import os
import json
import shutil
from PySide6.QtWidgets import QFileDialog, QMessageBox
from utils.common import get_base_path
from config import CREDENTIALS_FILE_NAME, OAUTH_FILE_NAME
from components.service_settings.worker.service_settings_worker import GmailLoginWorker


def on_upload_json(parent, msg_show_time):
    """
    OAUTH設定ファイルのアップロード処理

    Args:
        parent: 親ウィンドウ
        msg_show_time: メッセージ表示時間
    """
    try:
        # ファイル選択ダイアログを表示
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "OAUTH設定ファイルを選択",
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            # キャンセルされた場合
            return

        # ファイル名を固定で「oauth.json」に設定
        file_name = OAUTH_FILE_NAME

        # 保存先ディレクトリを作成（存在しない場合）
        current_dir = get_base_path()
        oauth_dir = os.path.join(current_dir, "credentials", "oauth")
        os.makedirs(oauth_dir, exist_ok=True)

        # ファイルをコピー
        destination = os.path.join(oauth_dir, file_name)
        shutil.copy2(file_path, destination)

        # ログに出力
        parent.settings_log.append(f"OAUTH設定ファイルをアップロードしました。")
        parent.statusBar().showMessage(f"OAUTH設定ファイルをアップロードしました。", msg_show_time)

        # 成功メッセージ
        QMessageBox.information(
            parent,
            "アップロード完了",
            f"OAUTH設定ファイルを正常にアップロードしました。"
        )

    except Exception as e:
        error_msg = f"OAUTH設定ファイルのアップロード中にエラーが発生しました: {str(e)}"
        parent.settings_log.append(f"エラー: {error_msg}\n")
        parent.statusBar().showMessage("OAUTH設定ファイルのアップロードに失敗しました", msg_show_time)
        QMessageBox.critical(
            parent,
            "エラー",
            error_msg
        )


def on_upload_credentials(parent, msg_show_time):
    """
    Credentialsファイルのアップロード処理

    Args:
        parent: 親ウィンドウ
        msg_show_time: メッセージ表示時間
    """
    try:
        # ファイル選択ダイアログを表示
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "Credentialsファイルを選択",
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            # キャンセルされた場合
            return

        # ファイル名を固定で「credentials.json」に設定
        file_name = CREDENTIALS_FILE_NAME

        # 保存先ディレクトリを作成（存在しない場合）
        current_dir = get_base_path()
        service_account_dir = os.path.join(current_dir, "credentials", "service_account")
        os.makedirs(service_account_dir, exist_ok=True)

        # ファイルをコピー
        destination = os.path.join(service_account_dir, file_name)
        shutil.copy2(file_path, destination)

        # ログに出力
        parent.settings_log.append(f"Credentialsファイルをアップロードしました。")
        parent.statusBar().showMessage(f"Credentialsファイルをアップロードしました。", msg_show_time)

        # 成功メッセージ
        QMessageBox.information(
            parent,
            "アップロード完了",
            f"Credentialsファイルを正常にアップロードしました。"
        )

    except Exception as e:
        error_msg = f"Credentialsファイルのアップロード中にエラーが発生しました: {str(e)}"
        parent.settings_log.append(f"エラー: {error_msg}\n")
        parent.statusBar().showMessage("アップロードに失敗しました", msg_show_time)
        QMessageBox.critical(
            parent,
            "エラー",
            error_msg
        )


def on_save_sheet_id(parent, msg_show_time):
    """
    Sheet IDをJSONファイルに保存する処理

    Args:
        parent: 親ウィンドウ
        msg_show_time: メッセージ表示時間
    """
    try:
        # Sheet IDを取得
        sheet_id = parent.sheet_id_input.text().strip()

        if not sheet_id:
            QMessageBox.warning(
                parent,
                "入力エラー",
                "Sheet IDを入力してください。"
            )
            return

        # 保存先ディレクトリを作成（存在しない場合）
        current_dir = get_base_path()
        service_account_dir = os.path.join(current_dir, "credentials", "service_account")
        os.makedirs(service_account_dir, exist_ok=True)

        # JSONデータを作成
        sheet_info = {
            "sheet_id": sheet_id,
            "sheet_name": "accounts"
        }

        # JSONファイルに保存
        json_path = os.path.join(service_account_dir, "sheet_info.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(sheet_info, f, indent=4, ensure_ascii=False)

        # ログに出力
        parent.settings_log.append(f"Sheet IDを保存しました\n")
        parent.statusBar().showMessage("Sheet IDを保存しました", msg_show_time)

        # 成功メッセージ
        QMessageBox.information(
            parent,
            "保存完了",
            f"Sheet IDを正常に保存しました。"
        )

    except Exception as e:
        error_msg = f"Sheet IDの保存中にエラーが発生しました: {str(e)}"
        parent.settings_log.append(f"エラー: {error_msg}\n")
        parent.statusBar().showMessage("保存に失敗しました", msg_show_time)
        QMessageBox.critical(
            parent,
            "エラー",
            error_msg
        )


def on_test_spreadsheet_connection(parent, msg_show_time):
    """
    スプレッドシート接続確認処理

    Args:
        parent: 親ウィンドウ
        msg_show_time: メッセージ表示時間
    """
    try:
        parent.settings_log.append("スプレッドシートへの接続確認を開始します...\n")
        parent.statusBar().showMessage("スプレッドシート接続確認中...", msg_show_time)

        # sheet_info.jsonから設定を読み込み
        current_dir = get_base_path()
        sheet_info_path = os.path.join(current_dir, "credentials", "service_account", "sheet_info.json")

        if not os.path.exists(sheet_info_path):
            raise FileNotFoundError("スプレッドシート情報が見つかりません。Sheet IDを保存してください。")

        with open(sheet_info_path, 'r', encoding='utf-8') as f:
            sheet_info = json.load(f)
            spreadsheet_id = sheet_info.get("sheet_id")
            sheet_name = sheet_info.get("sheet_name")

        if not spreadsheet_id or not sheet_name:
            raise ValueError("sheet_info.jsonに必要な情報が含まれていません。")

        parent.settings_log.append(f"Sheet ID: {spreadsheet_id}\n")
        parent.settings_log.append(f"Sheet Name: {sheet_name}\n")

        # Credentialsファイルの確認
        credentials_path = os.path.join(current_dir, "credentials", "service_account", CREDENTIALS_FILE_NAME)
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentialsファイルが見つかりません: {CREDENTIALS_FILE_NAME}")

        parent.settings_log.append(f"Credentialsファイル: {CREDENTIALS_FILE_NAME}\n")

        # スプレッドシートに接続
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        client = gspread.authorize(creds)

        parent.settings_log.append("認証が完了しました\n")

        # スプレッドシートを開く
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)

        # シートの基本情報を取得
        row_count = worksheet.row_count
        col_count = worksheet.col_count

        parent.settings_log.append(f"スプレッドシート名: {spreadsheet.title}\n")
        parent.settings_log.append("接続確認に成功しました！\n")

        parent.statusBar().showMessage("接続確認に成功しました", msg_show_time)

        # 成功メッセージ
        QMessageBox.information(
            parent,
            "接続成功",
            f"スプレッドシートへの接続確認に成功しました。\n\n"
            f"スプレッドシート名: {spreadsheet.title}\n"
        )

    except FileNotFoundError as e:
        error_msg = f"ファイルが見つかりません: {str(e)}"
        parent.settings_log.append(f"エラー: {error_msg}\n")
        parent.statusBar().showMessage("接続確認に失敗しました", msg_show_time)
        QMessageBox.warning(
            parent,
            "エラー",
            error_msg
        )
    except Exception as e:
        error_msg = f"接続確認中にエラーが発生しました: {str(e)}"
        parent.settings_log.append(f"エラー: {error_msg}\n")
        parent.statusBar().showMessage("接続確認に失敗しました", msg_show_time)
        QMessageBox.critical(
            parent,
            "エラー",
            error_msg
        )


def on_gmail_login(parent, msg_show_time):
    """
    Gmailログイン処理

    Args:
        parent: 親ウィンドウ
        msg_show_time: メッセージ表示時間
    """
    # 既に実行中の場合は何もしない
    if parent.gmail_worker and parent.gmail_worker.isRunning():
        parent.settings_log.append("⚠️ Gmailログイン処理は既に実行中です\n")
        return

    parent.settings_log.append("Gmailログイン処理を開始します...\n")
    parent.statusBar().showMessage("Gmailログイン処理中...", msg_show_time)

    # Workerを作成して実行
    parent.gmail_worker = GmailLoginWorker()
    parent.gmail_worker.progress.connect(parent.on_gmail_progress)
    parent.gmail_worker.finished.connect(parent.on_gmail_finished)
    parent.gmail_worker.start()


def on_gmail_progress(parent, message):
    """
    Gmailログイン処理の進捗を表示

    Args:
        parent: 親ウィンドウ
        message: 進捗メッセージ
    """
    parent.settings_log.append(message)


def on_gmail_finished(parent, success, message, msg_show_time):
    """
    Gmailログイン処理完了時の処理

    Args:
        parent: 親ウィンドウ
        success: 成功/失敗
        message: メッセージ
        msg_show_time: メッセージ表示時間
    """
    if success:
        parent.statusBar().showMessage("Gmailログイン処理完了", msg_show_time)
    else:
        parent.statusBar().showMessage("Gmailログイン処理に失敗しました", msg_show_time)

    parent.gmail_worker = None
