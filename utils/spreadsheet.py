import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from config import SPREADSHEET_ID, SHEET_NAME, CREDENTIALS_FILE_NAME

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

    def extract_user_info(self, all_data, start_row=4, end_row=5):
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
        password = all_data[1][0]
        for row in  all_data[start_row - 1:end_row]:
            user_info = {
                'email': row[1],
                'password': password
            }
            user_info_list.append(user_info)
        return user_info_list

    # def get_all_records_by_df(self, spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME):
    #     """
    #     スプレッドシートの全データをDataFrame形式で取得する

    #     Args:
    #         None

    #     Returns:
    #         df (DataFrame): スプレッドシートの全データを格納したDataFrame
    #     """
    #     client = self.create_client()
    #     if not client:
    #         print("クライアントの作成に失敗しました。")
    #         return None

    #     try:
    #         print(f"スプレッドシートID: {spreadsheet_id}, シート名: {sheet_name} からデータを取得中...")
    #         # スプレッドシートを開く
    #         spreadsheet = client.open_by_key(spreadsheet_id)

    #         # ワークシートを取得
    #         worksheet = spreadsheet.worksheet(sheet_name)

    #         # 全てのデータを取得してDataFrame形式に変換
    #         all_data = worksheet.get_all_values()

    #         # DataFrameに変換（最初の行をヘッダーとして使用）
    #         if all_data:
    #             df = pd.DataFrame(all_data[1:], columns=all_data[0])
    #             return df
    #         else:
    #             print("データが見つかりません")
    #             return None

    #     except Exception as e:
    #         print(f"データ取得エラー: {e}")
    #         return None

    # def get_user_info(self, df):
    #     """
    #     DataFrameからユーザー情報を取得する

    #     Args:
    #         df (DataFrame): ユーザー情報が格納されたDataFrame

    #     Returns:
    #         list: ユーザー情報のリスト
    #     """
    #     user_info_list = []
    #     for index, row in df.iterrows():
    #         user_info = {
    #             'ID': row['ID'],
    #             'PW': row['PW']
    #         }
    #         user_info_list.append(user_info)
    #     return user_info_list


if __name__ == "__main__":
    spreadsheet_service = SpreadsheetApiClient()
    # スプレッドシートの全データをDataFrame形式で取得
    df = spreadsheet_service.get_all_records_by_df(spreadsheet_id=SPREADSHEET_ID, sheet_name=SHEET_NAME)
    user_info_list = spreadsheet_service.get_user_info(df)
    print(user_info_list)