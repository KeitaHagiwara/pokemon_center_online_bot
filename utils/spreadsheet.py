import os
import json
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SpreadsheetManager:
    def __init__(self, credentials_dir='./credentials', credentials_file='pco-bot-credentials.json'):
        """
        Googleスプレッドシート管理クラス

        Args:
            credentials_dir (str): 認証情報ファイルが格納されているディレクトリ
            credentials_file (str): Google Service Accountの認証情報ファイル名
        """
        self.credentials_dir = credentials_dir
        self.credentials_file = credentials_file
        self.credentials_path = os.path.join(credentials_dir, credentials_file)
        self.service = None
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

    def authenticate(self):
        """
        Google Sheets APIの認証を行う

        Returns:
            bool: 認証が成功した場合True、失敗した場合False
        """
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"認証情報ファイルが見つかりません: {self.credentials_path}")

            # サービスアカウントの認証情報を読み込み
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.scopes
            )

            # Google Sheets APIサービスを構築
            self.service = build('sheets', 'v4', credentials=credentials)
            print("Google Sheets APIの認証が完了しました。")
            return True

        except Exception as e:
            print(f"認証エラー: {e}")
            return False

    def get_spreadsheet_info(self, spreadsheet_id):
        """
        スプレッドシートの基本情報を取得する

        Args:
            spreadsheet_id (str): スプレッドシートID

        Returns:
            dict: スプレッドシートの情報
        """
        try:
            result = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            return result
        except HttpError as error:
            print(f"スプレッドシート情報取得エラー: {error}")
            return None

    def read_range(self, spreadsheet_id, range_name):
        """
        指定された範囲のデータを読み取る

        Args:
            spreadsheet_id (str): スプレッドシートID
            range_name (str): 読み取る範囲（例: 'Sheet1!A1:C10'）

        Returns:
            list: セルの値のリスト
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])
            if not values:
                print('データが見つかりませんでした。')
                return []

            return values

        except HttpError as error:
            print(f"データ読み取りエラー: {error}")
            return []

    def write_range(self, spreadsheet_id, range_name, values):
        """
        指定された範囲にデータを書き込む

        Args:
            spreadsheet_id (str): スプレッドシートID
            range_name (str): 書き込む範囲（例: 'Sheet1!A1:C10'）
            values (list): 書き込むデータの2次元リスト

        Returns:
            dict: APIレスポンス
        """
        try:
            body = {
                'values': values
            }

            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()

            print(f'{result.get("updatedCells")}個のセルが更新されました。')
            return result

        except HttpError as error:
            print(f"データ書き込みエラー: {error}")
            return None

    def append_data(self, spreadsheet_id, range_name, values):
        """
        スプレッドシートの末尾にデータを追加する

        Args:
            spreadsheet_id (str): スプレッドシートID
            range_name (str): 追加する範囲の開始位置（例: 'Sheet1!A1'）
            values (list): 追加するデータの2次元リスト

        Returns:
            dict: APIレスポンス
        """
        try:
            body = {
                'values': values
            }

            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()

            print(f'{result.get("updates").get("updatedCells")}個のセルが追加されました。')
            return result

        except HttpError as error:
            print(f"データ追加エラー: {error}")
            return None

    def clear_range(self, spreadsheet_id, range_name):
        """
        指定された範囲のデータをクリアする

        Args:
            spreadsheet_id (str): スプレッドシートID
            range_name (str): クリアする範囲（例: 'Sheet1!A1:C10'）

        Returns:
            dict: APIレスポンス
        """
        try:
            result = self.service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()

            print(f'範囲 {range_name} がクリアされました。')
            return result

        except HttpError as error:
            print(f"データクリアエラー: {error}")
            return None

    def create_sheet(self, spreadsheet_id, sheet_title):
        """
        新しいシートを作成する

        Args:
            spreadsheet_id (str): スプレッドシートID
            sheet_title (str): 新しいシートのタイトル

        Returns:
            dict: APIレスポンス
        """
        try:
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_title
                        }
                    }
                }]
            }

            result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()

            print(f'新しいシート "{sheet_title}" が作成されました。')
            return result

        except HttpError as error:
            print(f"シート作成エラー: {error}")
            return None


# 使用例
def main():
    """
    SpreadsheetManagerの使用例
    """
    # スプレッドシート管理インスタンスを作成
    sheet_manager = SpreadsheetManager()

    # 認証
    if not sheet_manager.authenticate():
        print("認証に失敗しました。")
        return

    # スプレッドシートIDを指定（実際のIDに置き換えてください）
    spreadsheet_id = '1Df1ztQAaYKCu8t51VbYMP3JCy2ppcg_LLEe4RxOyT9o'

    # データを読み取り
    print("データ読み取り例:")
    data = sheet_manager.read_range(spreadsheet_id, 'Sheet1!A1:B10')
    for row in data:
        print(row)

    # # データを書き込み
    # print("\nデータ書き込み例:")
    # sample_data = [
    #     ['名前', '年齢', '職業'],
    #     ['田中太郎', '30', 'エンジニア'],
    #     ['佐藤花子', '25', 'デザイナー']
    # ]
    # sheet_manager.write_range(spreadsheet_id, 'Sheet1!A1:C3', sample_data)

    # # データを追加
    # print("\nデータ追加例:")
    # new_data = [
    #     ['山田次郎', '35', 'マネージャー']
    # ]
    # sheet_manager.append_data(spreadsheet_id, 'Sheet1!A1', new_data)


if __name__ == '__main__':
    main()
