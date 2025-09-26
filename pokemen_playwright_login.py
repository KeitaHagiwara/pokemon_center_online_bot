import time
import asyncio
from playwright.async_api import async_playwright
from config import EMAIL, PASSWORD

LOGIN_URL = "https://www.pokemoncenter-online.com/login/"

async def run():
    async with async_playwright() as p:
        # Firefoxブラウザを起動（非ヘッドレスで確認）
        browser = await p.firefox.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        # ブラウザコンテキストを作成
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="ja-JP",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            extra_http_headers={
                "Accept-Language": "ja-JP,ja,en-US,en"
            },
            # JavaScriptを有効化
            java_script_enabled=True,
            # 画像読み込みを有効化
            bypass_csp=True
        )
        
        page = await context.new_page()
        
        # ページのタイムアウト設定
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(60000)
        
        # JavaScriptエラーを無視する設定
        page.on("console", lambda msg: None)  # コンソールメッセージを無視
        page.on("pageerror", lambda error: None)  # ページエラーを無視
        
        # ログインページへアクセス
        print("ログインページにアクセス中...")
        try:
            await page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
            print(f"現在のURL: {page.url}")
        except Exception as e:
            print(f"ページ読み込みでエラー: {e}")
            # フォールバック: 基本的な読み込みを待機
            await page.goto(LOGIN_URL, timeout=60000)
            await page.wait_for_timeout(5000)  # 5秒待機
            print(f"現在のURL: {page.url}")

        # ログインフォームの要素を検索（正確なセレクターを使用）
        print("ログインフォームを検索中...")
        
        try:
            # 正確なセレクターを使用
            email_field = page.locator("#login-form-email")
            password_field = page.locator("#current-password")
            login_button = page.locator("#form1Button")
            
            # 要素が表示されるまで待機
            await email_field.wait_for(state="visible", timeout=60000)
            await password_field.wait_for(state="visible", timeout=60000)
            await login_button.wait_for(state="visible", timeout=60000)
            
            print("ログインフォームの要素を発見")
            
            # ログイン情報を入力
            print("メールアドレスを入力中...")
            await email_field.clear()
            await email_field.fill(EMAIL)
            await page.wait_for_timeout(2000)
            
            print("パスワードを入力中...")
            await password_field.clear()
            await password_field.fill(PASSWORD)
            await page.wait_for_timeout(2000)

            time.sleep(20)
            
            # ログインボタンをクリック
            print("ログインボタンをクリック中...")
            await login_button.click()
            print("ログインボタンをクリックしました")
            
            # ログイン処理を待機（JavaScriptエラーを無視して継続）
            print("ログイン処理を待機中...")
            await page.wait_for_timeout(10000)  # 10秒待機
            
            # 追加の待機（手動確認用）
            print("手動確認のため360秒待機中...")
            time.sleep(360)

            # 複数の方法でログイン成功を確認
            print("ログイン成功を確認中...")
            
            # 方法1: URLの変更を確認
            current_url = page.url
            if "login" not in current_url.lower():
                print("ログインが成功しました！（URL変更確認）")
                await page.wait_for_timeout(5000)  # 手動確認のため少し待機
                return True
            
            # 方法2: ログアウトリンクの存在を確認
            try:
                logout_element = page.locator("a[href*='Logout'], a[href*='Logout-Show'], .logout, .sign-out")
                await logout_element.wait_for(state="visible", timeout=5000)
                print("ログインが成功しました！（ログアウトリンク確認）")
                await page.wait_for_timeout(5000)
                return True
            except:
                pass
            
            # 方法3: ユーザー名表示の確認
            try:
                user_element = page.locator(".user-name, .account-name, .header-user, [data-user-state='logged-in']")
                await user_element.wait_for(state="visible", timeout=5000)
                print("ログインが成功しました！（ユーザー名表示確認）")
                await page.wait_for_timeout(5000)
                return True
            except:
                pass
            
            # 方法4: エラーメッセージの確認
            try:
                error_element = page.locator(".error, .alert-danger, .login-error")
                if await error_element.is_visible():
                    error_text = await error_element.text_content()
                    print(f"ログインエラー: {error_text}")
                    return False
            except:
                pass
            
            print("ログイン状態を確認できませんでした")
            await page.wait_for_timeout(5000)  # 手動確認のため
            return False
            
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            # デバッグ用スクリーンショット
            await page.screenshot(path="poke_login_fail_playwright.png")
            print("スクリーンショット保存: poke_login_fail_playwright.png")
            await page.wait_for_timeout(5000)  # 手動確認のため
            return False
        
        finally:
            # 手動確認のため、ユーザーがエンターキーを押すまで待機
            input("エンターキーを押すとブラウザを閉じます...")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
