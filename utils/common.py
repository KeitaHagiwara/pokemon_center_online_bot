import base64
import sys
import os

def get_base_path():
    """
    アプリケーションのベースパスを取得（PyInstaller対応）

    Returns:
        str: アプリケーションのベースディレクトリパス
            - PyInstallerでバンドルされている場合: sys._MEIPASS（一時展開ディレクトリ）
            - 通常のPython実行の場合: カレントディレクトリまたはスクリプトのディレクトリ
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerでバンドルされている場合
        return sys._MEIPASS
    else:
        # 通常のPython実行の場合
        return os.getcwd()

def base64_decode(b64_message):
    """
    Base64エンコードされたメッセージをデコードする

    Args:
        b64_message: Base64エンコードされたメッセージ

    Returns:
        デコードされたメッセージ文字列
    """
    try:
        message = base64.urlsafe_b64decode(
            b64_message + '=' * (-len(b64_message) % 4)).decode(encoding='utf-8')
        return message
    except Exception as e:
        return f"デコードエラー: {e}"

def pad_with_zeros(input_string):
    """
    文字列の先頭を0で埋めて10文字にする
    """
    padded_string = input_string.zfill(10)
    return padded_string

def get_column_number_by_alphabet(column_name):
    """
    列名（アルファベット）から列番号を取得する
    Args:
        column_name: 列名（例: "A", "B", ..., "Z", "AA", "AB", ...）
    Returns:
        列番号（1から始まる整数）
    """
    column_number = 0
    length = len(column_name)

    for i, char in enumerate(column_name):
        char_value = ord(char.upper()) - ord('A') + 1
        column_number = column_number * 26 + char_value

    return column_number