"""
Gmail API を使用してメールを取得するモジュール

このスクリプトは以下の機能を提供します:
- OAuth 2.0認証でGmailにアクセス
- 指定された条件でメールを検索・取得
- Pokemon Center等の特定送信者からのメールを監視

使用前の準備:
1. Google Cloud ConsoleでOAuth 2.0クライアントIDを作成
2. JSONファイルを ./credentials/oauth_credentials.json として保存
3. 初回実行時にブラウザで認証を完了

著者: Pokemon Center Bot
日付: 2025年9月30日
"""

import pickle
import os.path
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import GoogleAuthError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail APIのスコープ（読み取り専用）
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# 取得するメール件数
MAIL_COUNTS = 5

# 検索条件 - Pokemon Center関連のメールを検索
SEARCH_CRITERIA = {
    'from': "info@pokemoncenter-online.com",  # Pokemon Centerからのメール
    'to': "",
    'subject': "[ポケモンセンターオンライン]ログイン用パスコードのお知らせ"  # 件名指定なし（全てのPokemon Centerメール）
}

# メール保存用ディレクトリ
BASE_DIR = 'mail_box'

credentials_dir_path = './credentials'
credentials_file_name = 'pco-bot-credentials.json'

def authenticate(scope):
    """
    Gmail APIの認証を行う

    Args:
        scope: APIアクセススコープのリスト

    Returns:
        認証済みクレデンシャル
    """
    creds = None

    # token.pickleファイルからアクセストークンとリフレッシュトークンを読み込み
    token_path = os.path.join(credentials_dir_path, 'token.pickle')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # 有効な認証情報がない場合、ユーザーにログインを求める
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 認証トークンを更新中...")
                creds.refresh(Request())
            else:
                print("🔐 初回認証を開始...")

                # OAuth認証ファイルのパスを確認
                credentials_file = os.path.join(credentials_dir_path, credentials_file_name)
                if not os.path.exists(credentials_file):
                    print(f"❌ 認証ファイルが見つかりません: {credentials_file}")
                    print("📋 OAuth 2.0クライアントIDを作成し、JSONファイルを配置してください")
                    raise FileNotFoundError(f"認証ファイルが必要です: {credentials_file}")

                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scope)
                print("🌐 ブラウザでGoogleアカウントにログインしてください...")
                creds = flow.run_local_server(port=0)

        except GoogleAuthError as err:
            print(f'❌ 認証エラー: {err}')
            raise

        # 次回実行のために認証情報を保存
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        print("✅ 認証情報を保存しました")

    return creds


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


class ApiClient(object):
    """Gmail API クライアント"""

    def __init__(self, credential):
        """
        Gmail APIサービスを初期化

        Args:
            credential: 認証済みクレデンシャル
        """
        self.service = build('gmail', 'v1', credentials=credential)

    def get_mail_list(self, limit, query):
        """
        指定された条件でメールリストを取得

        Args:
            limit: 取得するメール件数
            query: 検索クエリ

        Returns:
            メッセージIDのリスト
        """
        try:
            results = self.service.users().messages().list(
                userId='me', maxResults=limit, q=query).execute()
            return results.get('messages', [])
        except HttpError as err:
            print(f'❌ メールリスト取得エラー: {err}')
            raise

    def get_subject_message(self, id):
        """
        指定されたメールIDのメール内容を取得

        Args:
            id: メッセージID

        Returns:
            dict: {'subject': 件名, 'message': 本文, 'sender': 送信者, 'date': 日付}
        """
        try:
            res = self.service.users().messages().get(userId='me', id=id).execute()
        except HttpError as err:
            print(f'❌ メッセージ取得エラー: {err}')
            raise

        result = {}
        headers = res['payload'].get('headers', [])

        # ヘッダー情報から必要な情報を抽出
        result['subject'] = next((d.get('value') for d in headers if d.get('name') == 'Subject'), '件名なし')
        result['sender'] = next((d.get('value') for d in headers if d.get('name') == 'From'), '送信者不明')
        result['date'] = next((d.get('value') for d in headers if d.get('name') == 'Date'), '日付不明')

        # メッセージ本文を取得
        try:
            # text/plain の場合
            if 'data' in res['payload']['body']:
                b64_message = res['payload']['body']['data']
            # text/html や multipart の場合
            elif res['payload']['parts'] is not None:
                b64_message = res['payload']['parts'][0]['body']['data']
            else:
                b64_message = ""

            result['message'] = base64_decode(b64_message) if b64_message else "本文なし"
        except (KeyError, IndexError):
            result['message'] = "本文の取得に失敗しました"

        return result


def build_search_criteria(query_dict):
    """
    検索条件辞書から検索クエリ文字列を構築

    Args:
        query_dict: 検索条件辞書

    Returns:
        Gmail API用検索クエリ文字列
    """
    query_string = ''
    for key, value in query_dict.items():
        if value:
            query_string += key + ':' + value + ' '
    return query_string

def get_passode_from_message(message):
    """
    メール本文からパスコードを抽出

    Args:
        message: メール本文

    Returns:
        抽出されたパスコード文字列、またはNone
    """
    import re
    match = re.search(r'(\d{6})', message)
    return match.group(1) if match else None

def main():
    """メイン処理：Gmail からメールを取得して表示"""
    try:
        print("🔑 Gmail認証を開始...")
        creds = authenticate(SCOPES)
        print("✅ 認証成功!")

        query = build_search_criteria(SEARCH_CRITERIA)
        print(f"🔍 検索クエリ: {query.strip() if query.strip() else '全てのメール'}")

        client = ApiClient(creds)
        messages = client.get_mail_list(MAIL_COUNTS, query)

        if not messages:
            print('📭 指定条件のメールが見つかりませんでした。')
            print('💡 ヒント: Pokemon Centerからのメールがない場合は、SEARCH_CRITERIAを変更してください')
            print('💡 例: SEARCH_CRITERIA = {"from": "", "to": "", "subject": ""} # すべてのメールを検索')
        else:
            print(f'📬 {len(messages)}件のメールを取得しました:\n')

            for i, message in enumerate(messages, 1):
                message_id = message['id']

                try:
                    # 件名とメッセージを取得
                    result = client.get_subject_message(message_id)

                    print(f'📩 メール {i}:')
                    print(f'送信者: {result["sender"]}')
                    print(f'件名: {result["subject"]}')
                    print(f'日付: {result["date"]}')
                    print(f'本文: {result["message"][:300]}{"..." if len(result["message"]) > 300 else ""}')
                    print(f'パスコード: {get_passode_from_message(result["message"]) or "見つかりませんでした"}')
                    print('─' * 80)

                except Exception as e:
                    print(f'❌ メール {i} の取得に失敗: {e}')

    except FileNotFoundError as e:
        print(f"❌ ファイルエラー: {e}")
        print("\n📋 解決方法:")
        print("1. Google Cloud ConsoleでOAuth 2.0クライアントIDを作成")
        print("2. 'デスクトップアプリケーション'として設定")
        print("3. JSONファイルを ./credentials/oauth_credentials.json として保存")
        print("4. oauth_gmail_setup.md の詳細手順を参照")

    except GoogleAuthError as e:
        print(f"❌ 認証エラー: {e}")
        print("\n📋 解決方法:")
        print("1. ブラウザでGoogleアカウントにログイン")
        print("2. アプリの権限を許可")
        print("3. OAuth同意画面でテストユーザーが追加されているか確認")

    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")


if __name__ == "__main__":
    print("=== Pokemon Center Gmail Bot ===")
    print("📧 Gmail からメールを取得します\n")
    main()