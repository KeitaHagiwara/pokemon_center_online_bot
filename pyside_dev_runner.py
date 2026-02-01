"""PySide開発用ホットリロードランナー"""
import sys
import subprocess
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class PySideReloader(FileSystemEventHandler):
    """ファイル変更を監視してアプリを再起動"""

    def __init__(self, script_path):
        self.script_path = script_path
        self.process = None
        self.last_restart = 0
        self.start_app()

    def start_app(self):
        """アプリを起動"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("アプリを停止しました")

        print(f"\n{'='*50}")
        print(f"アプリを起動中: {self.script_path}")
        print(f"{'='*50}\n")

        self.process = subprocess.Popen(
            [sys.executable, self.script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def on_modified(self, event):
        """ファイル変更時の処理"""
        if event.src_path.endswith('.py'):
            # 連続した変更を防ぐため、1秒以内の変更は無視
            current_time = time.time()
            if current_time - self.last_restart < 1:
                return

            self.last_restart = current_time
            print(f"\n変更検知: {event.src_path}")
            print("アプリを再起動します...")
            self.start_app()


def main():
    if len(sys.argv) < 2:
        print("使い方: python pyside_dev_runner.py <PySideスクリプト.py>")
        sys.exit(1)

    script_path = sys.argv[1]
    if not Path(script_path).exists():
        print(f"エラー: ファイルが見つかりません: {script_path}")
        sys.exit(1)

    print("PySide開発用ホットリロードを開始します")
    print(f"監視対象: {Path.cwd()}")
    print("終了するには Ctrl+C を押してください\n")

    reloader = PySideReloader(script_path)
    observer = Observer()
    observer.schedule(reloader, path=str(Path.cwd()), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nホットリロードを停止します...")
        if reloader.process:
            reloader.process.terminate()
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
