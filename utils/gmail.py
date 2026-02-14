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

import re
import datetime
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import GoogleAuthError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.common import base64_decode, get_base_path
from email.utils import parsedate_to_datetime
from config import OAUTH_FILE_NAME, OAUTH_TOKEN_FILE_NAME
# from common import base64_decode

# 取得するメール件数
MAIL_COUNTS = 5

# メール保存用ディレクトリ
BASE_DIR = 'mail_box'

# 検索条件 - Pokemon Center関連のメールを検索
# 'from': "info@pokemoncenter-online.com",  # Pokemon Centerからのメール
SEARCH_CRITERIA = {
    'from': '',
    'to': '',
    'subject': '[ポケモンセンターオンライン]ログイン用パスコードのお知らせ'  # パスコードメールに絞り込む
}

EMAIL_TYPE_DICT = {
    'passcode': {'name': '二段階認証コード', 'icon': '🔑'},
    'auth_link': {'name': '認証リンク', 'icon': '🔗'}
}

credentials_dir_path = os.path.join(get_base_path(), 'credentials', 'oauth')
# credentials_file_name = 'oauth_credentials.json'
# credentials_file_name = 'ポケセン鍵_テスト.json'
# credentials_file_name = 'oauth_ohtani.json'
credentials_file_path = os.path.join(credentials_dir_path, OAUTH_FILE_NAME)
token_file_name = OAUTH_TOKEN_FILE_NAME
# token_file_name = "token.pickle"

class AuthenticationService:
    """Gmail API サービスクラス"""

    def __init__(self):
        pass

    def delete_token(self):
        """既存のトークンファイルを削除する"""
        token_path = os.path.join(credentials_dir_path, token_file_name)
        if os.path.exists(token_path):
            os.remove(token_path)
            print("🗑️ 既存のトークンファイルを削除しました")
        else:
            print("ℹ️ トークンファイルは存在しません")

    def authenticate(self):
        """
        Gmail APIの認証を行う

        Args:
            None

        Returns:
            認証済みクレデンシャル
        """
        creds = None

        # token.pickleファイルからアクセストークンとリフレッシュトークンを読み込み
        token_path = os.path.join(credentials_dir_path, token_file_name)
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # 有効な認証情報がない場合、ユーザーにログインを求める
        if not creds or not creds.valid:
            try:
                if creds and creds.expired and creds.refresh_token:
                    print("🔄 認証トークンを更新中...")
                    creds.refresh(Request())
                    # 更新後のトークンを保存（重要！）
                    with open(token_path, 'wb') as token:
                        pickle.dump(creds, token)
                    print("✅ トークンを更新しました")
                else:
                    print("🔐 初回認証を開始...")

                    # OAuth認証ファイルのパスを確認
                    if not os.path.exists(credentials_file_path):
                        print(f"❌ 認証ファイルが見つかりません: {credentials_file_path}")
                        print("📋 OAuth 2.0クライアントIDを作成し、JSONファイルを配置してください")
                        raise FileNotFoundError(f"認証ファイルが必要です: {credentials_file_path}")

                    # Gmail APIのスコープ（読み取り専用）
                    scope = ['https://www.googleapis.com/auth/gmail.readonly']

                    flow = InstalledAppFlow.from_client_secrets_file(credentials_file_path, scope)
                    print("🌐 ブラウザでGoogleアカウントにログインしてください...")
                    # オフラインアクセスを有効化してリフレッシュトークンを取得
                    creds = flow.run_local_server(
                        port=0,
                        access_type='offline',
                        prompt='consent'
                    )

                    # 次回実行のために認証情報を保存
                    with open(token_path, 'wb') as token:
                        pickle.dump(creds, token)
                    print("✅ 認証情報を保存しました")

            except GoogleAuthError as err:
                print(f'❌ 認証エラー: {err}')
                raise
        else:
            print("✅ キャッシュされた認証情報を使用")

        return creds


class GmailApiClient(object):
    """Gmail管理クラス"""

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

class ExtractService:

    def build_search_criteria(self, query_dict):
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

    def get_passcode_from_message(self, message):
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

    def get_auth_link_from_message(self, message):
        """
        メール本文から認証リンクを抽出

        Args:
            message: メール本文

        Returns:
            抽出された認証リンク文字列、またはNone
        """
        import re
        match = re.search(r'(https?://[^\s]+)', message)
        return match.group(1) if match else None


def extract_target_str_from_gmail_text_in_3min(to_email, subject_keyword, email_type="passcode"):
    """
    Gmailから欲しい情報を抽出する（3分以内のメールのみ）

    Args:
        to_email: 送信先メールアドレス
        subject_keyword: 件名キーワード
        email_type: 抽出する情報の種類 ("passcode" または "auth_link")

    Returns:
        抽出されたパスコード文字列、またはNone
    """
    try:

        print("🔑 Gmail認証を開始...")
        creds = AuthenticationService().authenticate()
        print("✅ 認証成功!")

        # 現在時刻から3分前の時刻を計算
        now = datetime.datetime.now(datetime.timezone.utc)
        one_minute_ago = now - datetime.timedelta(minutes=3)
        print(f"⏰ 検索対象時間: {one_minute_ago.strftime('%Y-%m-%d %H:%M:%S')} 以降")

        # 検索条件を設定する
        SEARCH_CRITERIA['to'] = to_email
        SEARCH_CRITERIA['subject'] = subject_keyword

        extract_service = ExtractService()
        query = extract_service.build_search_criteria(SEARCH_CRITERIA)
        print(f"🔍 検索クエリ: {query.strip() if query.strip() else '全てのメール'}")

        client = GmailApiClient(creds)
        messages = client.get_mail_list(MAIL_COUNTS, query)

        target_str = None
        recent_messages = []  # 3分以内のメールを格納
        if not messages:
            print('📭 指定条件のメールが見つかりませんでした。')
            print('💡 ヒント: Pokemon Centerからのメールがない場合は、SEARCH_CRITERIAを変更してください')
            print('💡 例: SEARCH_CRITERIA = {"from": "", "to": "", "subject": ""} # すべてのメールを検索')
        else:
            print(f'📬 {len(messages)}件のメールを取得しました。3分以内のメールを絞り込み中...\n')

            # メールの日時チェックと絞り込み
            for i, message in enumerate(messages, 1):
                message_id = message['id']

                try:
                    # 件名とメッセージを取得
                    result = client.get_subject_message(message_id)

                    # メールの日時を解析
                    try:
                        email_date_str = result["date"]
                        # RFC2822形式の日時文字列をパース
                        email_datetime = parsedate_to_datetime(email_date_str)

                        # UTCに変換（タイムゾーン情報がない場合はUTCとして扱う）
                        if email_datetime.tzinfo is None:
                            email_datetime = email_datetime.replace(tzinfo=datetime.timezone.utc)
                        else:
                            email_datetime = email_datetime.astimezone(datetime.timezone.utc)

                        print(f'📧 メール {i}: {email_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")}')

                        # 3分以内のメールかチェック
                        if email_datetime >= one_minute_ago:
                            print(f'✅ 3分以内のメールです！')
                            recent_messages.append((message_id, result, email_datetime))
                        else:
                            time_diff = (now - email_datetime).total_seconds()
                            print(f'⏰ {time_diff:.0f}秒前のメールです（対象外）')

                    except Exception as date_error:
                        print(f'⚠️  日時の解析に失敗: {date_error}')
                        print(f'   生の日時データ: {result["date"]}')
                        # 日時解析に失敗した場合は対象に含める（安全のため）
                        recent_messages.append((message_id, result, None))

                except Exception as e:
                    print(f'❌ メール {i} の取得に失敗: {e}')

            # 3分以内のメールからパスコードを抽出
            if not recent_messages:
                print('📭 3分以内に受信したメールが見つかりませんでした。')
            else:
                print(f'\n🎯 3分以内のメール: {len(recent_messages)}件')
                print('─' * 80)

                # 最新のメールから順に処理（日時でソート）
                recent_messages.sort(key=lambda x: x[2] if x[2] else datetime.datetime.min.replace(tzinfo=datetime.timezone.utc), reverse=True)

                for i, (message_id, result, email_datetime) in enumerate(recent_messages, 1):
                    # 抽出するロジックが異なるため、場合分け
                    if email_type == "passcode":
                        target_str = extract_service.get_passcode_from_message(result["message"])
                    elif email_type == "auth_link":
                        target_str = extract_service.get_auth_link_from_message(result["message"])

                    print(f'📩 最近のメール {i}:')
                    print(f'送信者: {result["sender"]}')
                    print(f'件名: {result["subject"]}')
                    print(f'日付: {result["date"]}')
                    if email_datetime:
                        time_diff = (now - email_datetime).total_seconds()
                        print(f'受信: {time_diff:.0f}秒前')
                    print(f'本文: {result["message"][:300]}{"..." if len(result["message"]) > 300 else ""}')
                    print(f'{EMAIL_TYPE_DICT[email_type]["name"]}: {target_str or "見つかりませんでした"}')
                    print('─' * 80)

                    if target_str:
                        print(f'{EMAIL_TYPE_DICT[email_type]["icon"]} {EMAIL_TYPE_DICT[email_type]["name"]}（{time_diff:.0f}秒前受信）: {target_str}')
                        break  # 最新のパスコードを取得したらループを抜ける

                if not target_str:
                    print(f'❌ 3分以内のメールから{EMAIL_TYPE_DICT[email_type]["name"]}が見つかりませんでした。')

        return target_str

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


def main(to_email):
    """メイン処理：Gmail からメールを取得して表示"""

    try:
        print("🔑 Gmail認証を開始...")
        creds = AuthenticationService().authenticate()
        print("✅ 認証成功!")

        SEARCH_CRITERIA['to'] = to_email
        extract_service = ExtractService()
        query = extract_service.build_search_criteria(SEARCH_CRITERIA)
        print(f"🔍 検索クエリ: {query.strip() if query.strip() else '全てのメール'}")

        client = GmailApiClient(creds)
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
                    print(f'パスコード: {extract_service.get_passcode_from_message(result["message"]) or "見つかりませんでした"}')
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

    to_email = "bigfly20230901@gmail.com"
    # to_email = "k.f.hagiwara@gmail.com"
    main(to_email)