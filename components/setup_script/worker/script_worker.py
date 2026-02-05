import subprocess
import select
import os
import time
import re
from PySide6.QtCore import QThread, Signal


class ScriptWorker(QThread):
    """スクリプト実行用のワーカースレッド"""
    finished = Signal(bool, str)  # 成功/失敗, メッセージ
    progress = Signal(str)  # 進捗メッセージ

    def __init__(self, current_dir):
        super().__init__()
        self.current_dir = current_dir

    def run(self):
        """スレッドで実行される処理"""
        try:
            # startup.sh をバックグラウンドで実行 (Appiumサーバー起動)
            print("[DEBUG] Appiumサーバー起動処理開始")
            self.progress.emit("Appiumサーバーを起動中...")
            startup_script = os.path.join(self.current_dir, "scripts", "startup.sh")
            print(f"[DEBUG] startup_script: {startup_script}")
            # Popenを使ってバックグラウンドで実行（終了を待たない）
            subprocess.Popen(
                ["sh", startup_script],
                cwd=self.current_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Appiumサーバーの起動を少し待つ
            time.sleep(3)
            self.progress.emit("Appiumサーバーを起動しました")

            # xcode_build.sh をバックグラウンドで実行
            print("[DEBUG] xcode_build.sh 実行開始")
            self.progress.emit("iPhoneにプログラム実行環境を構築中...")
            xcode_script = os.path.join(self.current_dir, "scripts", "xcode_build.sh")
            print(f"[DEBUG] xcode_script: {xcode_script}")

            # Popenで標準出力を監視しながら実行
            process = subprocess.Popen(
                ["sh", xcode_script],
                cwd=self.current_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # 「Testing started」メッセージを待つ（タイムアウト: 5分）
            success_message_found = False
            error_message_found = False
            timeout = 300  # 5分（秒）
            start_time = time.time()

            print("[DEBUG] 'Testing started' メッセージを監視中...")

            try:
                while True:
                    # タイムアウトチェック
                    elapsed_time = time.time() - start_time
                    if elapsed_time > timeout:
                        print("[DEBUG] タイムアウト: 5分経過しても 'Testing started' が見つかりませんでした")
                        process.terminate()
                        self.finished.emit(False, "タイムアウト: xcode_build.sh の実行が5分以内に完了しませんでした")
                        return

                    # 非ブロッキングで標準出力をチェック（最大0.5秒待機）
                    remaining_time = timeout - elapsed_time
                    wait_time = min(0.5, remaining_time)

                    # selectを使って非ブロッキングで読み取り可能かチェック
                    ready, _, _ = select.select([process.stdout], [], [], wait_time)

                    if ready:
                        line = process.stdout.readline()
                        if line:
                            print(f"[DEBUG] xcode output: {line.strip()}")

                            # 「Testing started」が見つかったか確認
                            if "Testing started" in line or re.search(r"Test Case '.*' started\.", line):
                                print("[DEBUG] 'Testing started' メッセージを検出しました！")
                                success_message_found = True
                                break

                            # 「Cancel Testing」が見つかったか確認
                            if "Cancel Testing" in line:
                                print("[DEBUG] 'Cancel Testing' メッセージを検出しました！")
                                error_message_found = True
                                break

                    # プロセスが終了していたらチェック
                    if process.poll() is not None:
                        # プロセスは終了したが、メッセージが見つからなかった
                        if not success_message_found:
                            print("[DEBUG] プロセスが終了しましたが 'Testing started' が見つかりませんでした")
                            self.finished.emit(False, "xcode_build.sh が 'Testing started' を出力せずに終了しました")
                            return
                        break

                if success_message_found:
                    print("[DEBUG] xcode_build.sh が正常に開始されました")
                    self.progress.emit("iPhoneとの接続が確立されました")

                if error_message_found:
                    print("[DEBUG] xcode_build.sh でエラーが発生しました")
                    raise Exception("iPhoneが接続されていないか、セットアップが完了していません。")

            except Exception as e:
                print(f"[DEBUG] xcode_build.sh 監視中にエラー: {e}")
                process.terminate()
                self.finished.emit(False, f"iPhoneとの接続環境構築中にエラーが発生しました: {str(e)}")
                return

            print("[DEBUG] iPhone接続処理成功 - finished.emit(True) を呼び出します")
            self.finished.emit(True, "iPhone接続処理が完了しました")
            print("[DEBUG] finished.emit(True) 呼び出し完了")

        except Exception as e:
            error_message = f"iPhone接続処理でエラーが発生しました: {str(e)}"
            print(f"[DEBUG] 例外発生: {error_message}")
            import traceback
            traceback.print_exc()
            self.finished.emit(False, error_message)
            print("[DEBUG] finished.emit(False) 呼び出し完了")
