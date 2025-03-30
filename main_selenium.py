#!/usr/bin/python3
import sys
import signal
import time
import getpass
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def sig_handler(sig, frame):
    if os.path.exists('qr.png'):
        os.remove('qr.png')
    sys.exit(0)

signal.signal(signal.SIGINT, sig_handler)

def init_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    return webdriver.Firefox(options=options)

def wait_for_login(browser, timeout=60):
    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']"))
        )
        return True
    except:
        return False

def send_messages(browser, phone, count, message):
    try:
        browser.get(f"https://web.whatsapp.com/send?phone={phone}")
        
        if not wait_for_login(browser):
            print("[-] Failed to detect login or chat loading")
            return False
        
        input_box = browser.find_element(By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
        send_button = browser.find_element(By.CSS_SELECTOR, "button[data-testid='compose-btn-send']")
        
        for i in range(1, count + 1):
            input_box.clear()
            input_box.send_keys(message)
            
            # Simulate human typing delay
            time.sleep(0.5 + (i % 3) * 0.2)
            
            send_button.click()
            print(f"[+] Sent message {i}/{count}")
            time.sleep(1)  # Avoid rate limiting
            
        return True
    except Exception as e:
        print(f"[-] Error sending messages: {str(e)}")
        return False

def main():
    if len(sys.argv) != 4:
        print(f"\n[!] Usage: {sys.argv[0]} <phone> <count> <message>\n")
        print("Example: ./main_selenium.py 1234567890 5 'Hello World'")
        sys.exit(1)

    phone = sys.argv[1]
    count = int(sys.argv[2])
    message = sys.argv[3]

    browser = init_driver(headless=False)
    
    try:
        print("[*] Opening WhatsApp Web...")
        browser.get("https://web.whatsapp.com")
        
        print("[*] Please scan the QR code within 60 seconds")
        browser.save_screenshot('qr.png')
        os.system('xdg-open qr.png 2>/dev/null || open qr.png 2>/dev/null')
        
        if not wait_for_login(browser):
            print("[-] Login timeout. Please try again.")
            return
        
        print("[+] Login successful. Starting message sending...")
        if send_messages(browser, phone, count, message):
            print("[+] Message sending completed successfully")
        else:
            print("[-] Message sending failed")
            
    finally:
        browser.quit()
        if os.path.exists('qr.png'):
            os.remove('qr.png')

if __name__ == '__main__':
    main()
