from scraping.ios.appium_utilities import AppiumUtilities

if __name__ == '__main__':
    appium_utils = AppiumUtilities()
    driver = appium_utils.driver
    print("Safariドライバーが起動しました")