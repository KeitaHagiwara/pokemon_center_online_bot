import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

from utils.common import get_column_number_by_alphabet
from config import SPREADSHEET_ID, SHEET_NAME, CREDENTIALS_FILE_NAME

HEADER_ROWS = 3  # ヘッダー行数

credentials_file_path = os.path.join(os.getcwd(), 'credentials', 'service_account', CREDENTIALS_FILE_NAME)


class SpreadsheetApiClient:
    """Googleスプレッドシート管理クラス"""

    def __init__(self):
        pass

    def authenticate(self):
        """
        Google Sheets APIの認証を行う

        Returns:
            creds: 認証が成功した場合認証情報、失敗した場合None
        """
        creds = None

        try:
            if not os.path.exists(f'{credentials_file_path}'):
                raise FileNotFoundError(f"認証情報ファイルが見つかりません: {credentials_file_path}")

            # 認証情報の設定
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(f'{credentials_file_path}', scope)

            print("Google Sheets APIの認証が完了しました。")
            return creds

        except Exception as e:
            print(f"認証エラー: {e}")

    def create_client(self):
        """
        gspreadクライアントを作成する

        Returns:
            client: gspreadクライアント
        """
        creds = self.authenticate()
        if creds:
            client = gspread.authorize(creds)
            return client
        else:
            print("クライアントの作成に失敗しました。")
            return None

    def get_all_data(self, spreadsheet_id, sheet_name):
        """
        スプレッドシートの全データを取得する

        Args:
            spreadsheet_id (str): スプレッドシートID
            sheet_name (str): シート名

        Returns:
            list: スプレッドシートの全データ
        """
        client = self.create_client()
        if not client:
            print("クライアントの作成に失敗しました。")
            return None

        try:
            print(f"スプレッドシートID: {spreadsheet_id}, シート名: {sheet_name} からデータを取得中...")
            # スプレッドシートを開く
            spreadsheet = client.open_by_key(spreadsheet_id)

            # ワークシートを取得
            worksheet = spreadsheet.worksheet(sheet_name)

            # 全てのデータを取得
            all_data = worksheet.get_all_values()
            return all_data

        except Exception as e:
            print(f"データ取得エラー: {e}")
            return None

    def get_column_dict(self, all_data):
        """
        スプレッドシートの全データから列名と列番号の辞書を作成する

        Args:
            all_data (list): スプレッドシートの全データ

        Returns:
            dict: 列名と列番号の辞書
        """
        column_dict = {}
        header_row = all_data[HEADER_ROWS - 1]  # ヘッダー行を取得

        for col_index, col_name in enumerate(header_row):
            column_dict[col_name] = col_index + 1  # 列番号は1始まり

        return column_dict

    def extract_user_info(self, all_data, start_row=4, end_row=5, write_col=None):
        """
        スプレッドシートの全データからユーザー情報を抽出する

        Args:
            all_data (list): スプレッドシートの全データ
            start_row (int): 抽出を開始する行番号（1始まり）
            end_row (int or None): 抽出を終了する行番号（1始まり）、Noneの場合は最後の行まで

        Returns:
            list: ユーザー情報のリスト
        """

        user_info_list = []

        column_dict = self.get_column_dict(all_data)
        email_col_index = column_dict.get('メールアドレス')
        password_col_index = column_dict.get('パスワード')

        if email_col_index is None or password_col_index is None:
            print("エラー: 'メールアドレス' または 'パスワード' 列が見つかりません。")
            return user_info_list

        for row_number, row in enumerate(all_data[start_row - 1:end_row]):
            # 書き込み対象の列が指定されている場合、既に値が入っている行はスキップ
            if write_col:
                target_column_index = get_column_number_by_alphabet(write_col)
                if row[target_column_index - 1].strip() != "":
                    print(f"スキップ: 行 {row_number + start_row} は既に処理済みです。")
                    continue

            user_info = {
                'row_number': row_number + start_row,
                'email': row[email_col_index - 1],
                'password': row[password_col_index - 1]
            }
            user_info_list.append(user_info)
        return user_info_list

    def get_check_target_product_name_dict(self, all_data, column_alphabet, top_p):
        """
        指定した行から確認対象の商品名を取得する

        Args:
            all_data (list): スプレッドシートの全データ
            column_alphabet (str): 行番号（A始まり）
            top_p (int): 上位件数

        Returns:
            dict: 確認対象の商品名の辞書
        """
        column_dict = self.get_column_dict(all_data)
        column_index = get_column_number_by_alphabet(column_alphabet)

        target_product_name_dict = {}
        # column_alphabetから始まってtop_p個分のカラムを取得
        for i in range(top_p):
            target_col_index = column_index + i
            for k, v in column_dict.items():
                if v == target_col_index:
                    target_product_name_dict[k] = v
                    break

        return target_product_name_dict

    def write_to_cell(self, spreadsheet_id, sheet_name, row, column, value):
        """
        スプレッドシートの指定したセルに値を書き込む

        Args:
            spreadsheet_id (str): スプレッドシートID
            sheet_name (str): シート名
            row (int): 行番号（1始まり）
            column (int): 列番号（1始まり）
            value (str): 書き込む値
        """
        client = self.create_client()
        if not client:
            print("クライアントの作成に失敗しました。")
            return

        try:
            print(f"スプレッドシートID: {spreadsheet_id}, シート名: {sheet_name} のセル({row}, {column}) に値を書き込み中...")
            # スプレッドシートを開く
            spreadsheet = client.open_by_key(spreadsheet_id)

            # ワークシートを取得
            worksheet = spreadsheet.worksheet(sheet_name)

            # 指定したセルに値を書き込む
            value_formatted = value.strip().replace('\n', '').replace('\r', '')
            worksheet.update_cell(row, column, value_formatted)
            print("値の書き込みが完了しました。")

        except Exception as e:
            print(f"セル書き込みエラー: {e}")

if __name__ == "__main__":
    spreadsheet_service = SpreadsheetApiClient()
    # スプレッドシートの全データをDataFrame形式で取得
    df = spreadsheet_service.get_all_records_by_df(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)
    user_info_list = spreadsheet_service.get_user_info(df)
    print(user_info_list)