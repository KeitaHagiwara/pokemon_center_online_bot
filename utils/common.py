import base64

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