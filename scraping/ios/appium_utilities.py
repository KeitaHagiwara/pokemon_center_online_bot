import time, random
from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

class AppiumUtilities:
    """
    Appiumを操作するためのクラス

    """
    def __init__(self):
        self.driver = self.setup_driver()

    def setup_driver(self):
        """Appiumドライバーをセットアップ"""
        options = XCUITestOptions()

        # iOSシミュレータの設定
        options.platform_name = 'iOS'
        options.platform_version = '18.0'  # 使用するiOSバージョン
        options.device_name = 'iPhone SE (3rd generation)'  # シミュレータのデバイス名
        options.browser_name = 'Safari'
        options.automation_name = 'XCUITest'

        # オプション設定
        options.new_command_timeout = 300
        options.no_reset = True

        # Appiumサーバーに接続
        driver = webdriver.Remote('http://localhost:4723', options=options)

        return driver

    def delete_browser_page(self):
        """Safariのブラウザページ（タブ）を削除"""
        print("Safariのブラウザページを削除中...")

        try:
            # 方法1: JavaScriptでストレージとキャッシュをクリア
            try:
                self.driver.execute_script("localStorage.clear();")
                self.driver.execute_script("sessionStorage.clear();")
                print("✅ ローカルストレージとセッションストレージをクリアしました")
            except Exception as e:
                print(f"ストレージクリアエラー: {e}")

            # 方法2: Cookieを削除
            try:
                self.driver.delete_all_cookies()
                print("✅ すべてのCookieを削除しました")
            except Exception as e:
                print(f"Cookie削除エラー: {e}")

            # 方法3: 代替手段 - blank pageに遷移してからリロード
            try:
                self.driver.get("about:blank")
                time.sleep(1)
                print("✅ 空白ページに遷移しました")
            except Exception as e:
                print(f"空白ページ遷移エラー: {e}")

            print("✅ ブラウザページの削除処理が完了しました")
            return True

        except Exception as e:
            print(f"❌ ブラウザページ削除処理でエラーが発生: {e}")
            return False

    def scroll_down(self):
        """画面を下にスクロール"""
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']

        start_x = width // 2
        start_y = height * 0.8
        end_x = width // 2
        end_y = height * 0.2

        self.driver.swipe(start_x, start_y, end_x, end_y, duration=800)
        print("画面を下にスクロールしました")

    def scroll_up(self):
        """画面を上にスクロール"""
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']

        start_x = width // 2
        start_y = height * 0.2
        end_x = width // 2
        end_y = height * 0.8

        self.driver.swipe(start_x, start_y, end_x, end_y, duration=800)
        print("画面を上にスクロールしました")

    def wait_and_click_element(self, by, value, timeout=10, scroll_attempts=3):
        """要素が表示されるまで待機し、必要に応じてスクロールしてからクリック"""
        for scroll_attempt in range(scroll_attempts + 1):
            try:
                # 要素の存在を確認
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )

                # 要素が表示されているか確認
                if element.is_displayed():
                    # 要素を画面内にスクロール
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(random.uniform(1, 3))

                    # クリック可能になるまで待機
                    clickable_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, value))
                    )
                    clickable_element.click()
                    print(f"要素をクリックしました: {value}")
                    return True
                else:
                    print(f"要素は存在しますが表示されていません: {value}")

            except Exception as e:
                if scroll_attempt < scroll_attempts:
                    print(f"要素が見つからないか表示されていません。スクロールします... ({scroll_attempt + 1}/{scroll_attempts})")
                    self.scroll_down()
                    time.sleep(random.uniform(1, 3))
                else:
                    print(f"要素の操作に失敗しました: {e}")
                    return False

        return False

    def safe_find_elements(self, by, value, attempt=0, timeout=10):
        """要素を安全に取得（スクロール付き）"""
        print(f"要素検索開始: {by} = {value}")

        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )

            # 表示されている要素のみフィルタ
            visible_elements = [el for el in elements if el.is_displayed()]

            if visible_elements:
                print(f"表示中の要素数: {len(visible_elements)} / 全体: {len(elements)}")
                # 各要素の詳細をログ出力
                for i, el in enumerate(visible_elements[:attempt]):
                    try:
                        element_class = el.get_attribute('class') or ''
                        element_id = el.get_attribute('id') or ''
                        element_text = (el.text or '')[:30]
                        print(f"  要素[{i}]: tag={el.tag_name}, class={element_class[:50]}, id={element_id}, text='{element_text}'")

                        # checkboxWrapper の場合は子要素も表示
                        if 'checkboxWrapper' in element_class or 'checkbox' in element_class.lower():
                            try:
                                children = el.find_elements(AppiumBy.XPATH, ".//*")
                                print(f"    子要素数: {len(children)}")
                                for j, child in enumerate(children[:2]):
                                    child_tag = child.tag_name
                                    child_class = child.get_attribute('class') or ''
                                    child_type = child.get_attribute('type') or ''
                                    print(f"      子[{j}]: {child_tag}, class={child_class[:30]}, type={child_type}")
                            except:
                                pass
                    except:
                        pass
                return visible_elements
            else:
                print("要素は存在しますが、表示されているものがありません")

        except Exception as e:
            if attempt < 2:
                print(f"要素取得失敗。スクロールして再試行... ({attempt + 1}/3)")
                self.scroll_down()
                time.sleep(random.uniform(1, 3))
            else:
                print(f"要素の取得に失敗: {e}")
                return []

        return []

    def open_accordion(self, element, element_name="要素"):
        """アコーディオンを開く専用関数 - 改良版"""
        print(f"{element_name}のアコーディオンを開こうとしています...")

        # 要素の詳細情報を出力
        try:
            print(f"要素情報: tag={element.tag_name}, class={element.get_attribute('class')}")
            print(f"位置情報: location={element.location}, size={element.size}")
            print(f"表示状態: displayed={element.is_displayed()}, enabled={element.is_enabled()}")
        except Exception as e:
            print(f"要素情報取得エラー: {e}")

        # 既に開いているかチェック
        def is_accordion_open():
            try:
                class_attr = element.get_attribute("class") or ""
                aria_expanded = element.get_attribute("aria-expanded") or ""
                style_attr = element.get_attribute("style") or ""

                # 複数の開いている状態をチェック
                open_indicators = [
                    "open" in class_attr.lower(),
                    "active" in class_attr.lower(),
                    "expanded" in class_attr.lower(),
                    "show" in class_attr.lower(),
                    aria_expanded.lower() == "true",
                    "display: block" in style_attr.lower(),
                    "height: auto" in style_attr.lower()
                ]

                is_open = any(open_indicators)
                print(f"アコーディオン状態チェック: {open_indicators} -> {is_open}")
                return is_open
            except Exception as e:
                print(f"アコーディオン状態確認エラー: {e}")
                return False

        if is_accordion_open():
            print(f"✅ {element_name}は既に開いています")
            return True

        print(f"アコーディオンが閉じています。ヘッダー優先でクリック試行を開始します。")

        # アコーディオンのクリック可能な部分を探す（ヘッダー優先）
        clickable_elements = []

        # 1. 最初にヘッダー部分を探す（成功実績があるため優先）
        try:
            headers = element.find_elements(AppiumBy.XPATH, ".//dt | .//h1 | .//h2 | .//h3 | .//h4 | .//h5 | .//h6")
            for i, header in enumerate(headers[:3]):  # 最初の3つまで
                if header.is_displayed():
                    clickable_elements.append((f"ヘッダー{i+1}", header))
                    print(f"ヘッダー{i+1}を発見: {header.tag_name}, class={header.get_attribute('class')}")
        except Exception as e:
            print(f"ヘッダー要素検索エラー: {e}")

        # 2. ヘッダーが見つからない場合の代替要素
        if not clickable_elements:
            try:
                # class名にclickableやtriggerが含まれる要素を探す
                triggers = element.find_elements(AppiumBy.XPATH, ".//*[contains(@class,'trigger') or contains(@class,'clickable') or contains(@class,'toggle') or contains(@class,'title')]")
                for i, trigger in enumerate(triggers[:2]):  # 最初の2つまで
                    if trigger.is_displayed():
                        clickable_elements.append((f"トリガー{i+1}", trigger))

                # ボタンやリンクを探す
                buttons = element.find_elements(AppiumBy.XPATH, ".//button | .//a | .//*[@role='button']")
                for i, button in enumerate(buttons[:2]):  # 最初の2つまで
                    if button.is_displayed():
                        clickable_elements.append((f"ボタン{i+1}", button))

                # 最終手段として親要素自体
                clickable_elements.append(("親要素", element))

            except Exception as e:
                print(f"代替要素検索エラー: {e}")

        print(f"クリック試行対象: {len(clickable_elements)}個の要素（ヘッダー優先）")

        # 各要素に対して複数の方法でクリックを試行
        for elem_name, click_element in clickable_elements:
            print(f"\n=== {elem_name}でのクリック試行 ===")

            # 要素を画面中央に移動
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", click_element)
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"スクロールエラー: {e}")

            # ヘッダー要素の場合は効率的な方法のみを試行（成功実績があるため）
            if "ヘッダー" in elem_name:
                print(f"ヘッダー要素検出: 効率的な方法のみを試行")
                methods = [
                    ("WebDriverWait + click", lambda ce: WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(ce)).click()),
                    ("通常クリック", lambda ce: ce.click()),
                    ("JavaScriptクリック", lambda ce: self.driver.execute_script("arguments[0].click();", ce)),
                ]
            else:
                # その他の要素には全ての方法を試行
                methods = [
                    ("WebDriverWait + click", lambda ce: WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(ce)).click()),
                    ("通常クリック", lambda ce: ce.click()),
                    ("JavaScriptクリック", lambda ce: self.driver.execute_script("arguments[0].click();", ce)),
                    ("ActionChainsクリック", lambda ce: ActionChains(self.driver).move_to_element(ce).click().perform()),
                    ("強制JavaScriptクリック", lambda ce: self.driver.execute_script("arguments[0].dispatchEvent(new Event('click', {bubbles: true}));", ce)),
                ]

                # 座標クリックは位置が取得できる場合のみ追加
                try:
                    location = click_element.location
                    size = click_element.size
                    if location and size and location['x'] >= 0 and location['y'] >= 0:
                        center_x = location['x'] + size['width'] / 2
                        center_y = location['y'] + size['height'] / 2
                        methods.append(("座標タップ", lambda ce: self.driver.tap([(int(center_x), int(center_y))])))
                except Exception as e:
                    print(f"座標取得失敗: {e}")

            for method_name, method_func in methods:
                try:
                    print(f"  試行中: {method_name}")
                    method_func(click_element)
                    time.sleep(random.uniform(1, 3))  # アニメーション待機

                    # 開いたかチェック
                    if is_accordion_open():
                        print(f"✅ {method_name}で{elem_name}のアコーディオンを開きました")
                        return True
                    else:
                        # 内容が表示されているかも確認
                        try:
                            child_elements = element.find_elements(AppiumBy.XPATH, ".//*")
                            visible_children = [el for el in child_elements if el.is_displayed()]
                            if len(visible_children) > 3:  # 十分な子要素が表示されている
                                print(f"✅ {method_name}: 子要素の表示からアコーディオンが開いていると判断")
                                return True
                        except:
                            pass
                        print(f"⚠️ {method_name}: アコーディオンが開いていない可能性があります")

                except Exception as e:
                    print(f"❌ {method_name}失敗: {e}")

            # ヘッダー要素で成功しなかった場合は、この要素では諦めて次へ
            if "ヘッダー" in elem_name:
                print(f"ヘッダー要素 {elem_name} では開けませんでした。次のヘッダーを試行します。")
                continue

        # 最終手段: フォーカスしてからEnterキーやスペースキーを試行
        print("\n=== 最終手段: キーボード操作 ===")
        try:
            element.click()  # フォーカスを当てる
            time.sleep(random.uniform(1, 3))

            # Enterキー
            ActionChains(self.driver).send_keys_to_element(element, "\n").perform()
            time.sleep(random.uniform(1, 3))
            if is_accordion_open():
                print("✅ Enterキーでアコーディオンを開きました")
                return True

            # スペースキー
            ActionChains(self.driver).send_keys_to_element(element, " ").perform()
            time.sleep(random.uniform(1, 3))
            if is_accordion_open():
                print("✅ スペースキーでアコーディオンを開きました")
                return True

        except Exception as e:
            print(f"キーボード操作失敗: {e}")

        print(f"❌ {element_name}のアコーディオンを開くことができませんでした")
        return False

    def safe_click(self, button_elements, target_index, element_name="ボタン要素"):
        """ボタン要素を安全にクリックする専用関数"""
        if not button_elements or len(button_elements) <= target_index:
            print(f"❌ {element_name}[{target_index}]が見つかりませんでした")
            return False

        target_button = button_elements[target_index]
        print(f"\n=== {element_name}[{target_index}]のクリック処理開始（座標タップ優先） ===")

        # ボタン要素の詳細情報を出力
        try:
            print(f"ボタン要素情報:")
            print(f"  - タグ名: {target_button.tag_name}")
            print(f"  - クラス: {target_button.get_attribute('class')}")
            print(f"  - タイプ: {target_button.get_attribute('type')}")
            print(f"  - 名前: {target_button.get_attribute('name')}")
            print(f"  - 値: {target_button.get_attribute('value')}")
            print(f"  - チェック状態: {target_button.get_attribute('checked')}")
            print(f"  - 表示状態: {target_button.is_displayed()}")
            print(f"  - 有効状態: {target_button.is_enabled()}")
        except Exception as e:
            print(f"ボタン要素情報取得エラー: {e}")

        # 既にチェック済みかどうか確認
        try:
            if target_button.get_attribute('checked') == 'true':
                print(f"✅ {element_name}[{target_index}]は既にチェックされています")
                return True
        except Exception as e:
            print(f"チェック状態確認エラー: {e}")

        # ボタン要素を画面中央にスクロール
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_button)
            time.sleep(random.uniform(1, 3))
            print("ボタン要素を画面中央にスクロールしました")
        except Exception as e:
            print(f"スクロールエラー: {e}")

        # クリック可能な要素を探す（ラジオボタン、ラベル、親要素など）
        clickable_targets = []

        # 1. ラジオボタン自体
        clickable_targets.append(("ラジオボタン本体", target_button))

        # # 2. 関連するラベル要素を探す
        # try:
        #     # for属性でリンクされたラベルを探す
        #     target_id = target_button.get_attribute('id')
        #     if target_id:
        #         labels = self.driver.find_elements(AppiumBy.XPATH, f"//label[@for='{target_id}']")
        #         for i, label in enumerate(labels[:2]):
        #             if label.is_displayed():
        #                 clickable_targets.append((f"ラベル{i+1}", label))

        #     # 親要素のラベルを探す
        #     parent_label = target_button.find_element(AppiumBy.XPATH, "./ancestor::label[1]")
        #     if parent_label and parent_label.is_displayed():
        #         clickable_targets.append(("親ラベル", parent_label))

        # except Exception as e:
        #     print(f"ラベル要素検索エラー: {e}")

        # 3. 親要素やラッパー要素
        try:
            parent = target_button.find_element(AppiumBy.XPATH, "./..")
            if parent and parent.is_displayed():
                clickable_targets.append(("親要素", parent))
        except Exception as e:
            print(f"親要素取得エラー: {e}")

        print(f"クリック対象候補: {len(clickable_targets)}個（座標タップ優先）")

        # 最優先：座標でのタップ（成功実績があるため）
        try:
            print(f"\n--- 最優先: 座標タップ ---")
            location = target_button.location
            size = target_button.size
            center_x = location['x'] + size['width'] / 2
            center_y = location['y'] + size['height'] / 2

            print(f"座標タップ実行: ({int(center_x)}, {int(center_y)})")
            self.driver.tap([(int(center_x), int(center_y))])
            time.sleep(random.uniform(1, 3))

            # if target_button.get_attribute('checked') == 'true':
            #     print(f"✅ 座標タップでラジオボタンのクリックが成功しました")
            #     return True
            # else:
            #     print(f"⚠️ 座標タップ: ラジオボタンがチェックされていません")
            return True  # 座標タップのみで成功とみなす

        except Exception as e:
            print(f"❌ 座標タップ失敗: {e}")

        # # 代替手段：各対象に対してクリックを試行
        # for target_name, target_element in clickable_targets:
        #     print(f"\n--- {target_name}でのクリック試行 ---")

        #     # 効率的なクリック方法のみ試行
        #     methods = [
        #         ("WebDriverWait + click", lambda te: WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(te)).click()),
        #         ("JavaScriptクリック", lambda te: self.driver.execute_script("arguments[0].click();", te)),
        #         ("通常クリック", lambda te: te.click()),
        #     ]

        #     for method_name, method_func in methods:
        #         try:
        #             print(f"  試行中: {method_name}")
        #             method_func(target_element)
        #             time.sleep(random.uniform(1, 3))

        #             # チェックされたかどうか確認
        #             if target_button.get_attribute('checked') == 'true':
        #                 print(f"✅ {method_name}で{target_name}のクリックが成功しました")
        #                 return True
        #             else:
        #                 print(f"⚠️ {method_name}: ラジオボタンがチェックされていません")

        #         except Exception as e:
        #             print(f"❌ {method_name}失敗: {e}")

        #     # 次の対象に移る前に短い待機
        #     break  # 座標タップで成功しない場合、最初の代替手段のみ試行して効率化

        # print(f"❌ {element_name}[{target_index}]のクリックに失敗しました")
        return False
