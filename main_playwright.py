#!/usr/bin/python3
import sys
import signal
import time
import getpass
import os
import asyncio
from playwright.async_api import async_playwright

def sig_handler(sig, frame):
    if os.path.exists('qr.png'):
        os.remove('qr.png')
    sys.exit(0)

signal.signal(signal.SIGINT, sig_handler)

async def whatsapp_send_messages(phone, count, message):
    async with async_playwright() as p:
        browser = await p.firefox.launch(
            headless=False,
            args=["--no-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        page = await context.new_page()
        await page.goto(f"https://web.whatsapp.com/send?phone={phone}")
        
        print("[*] Waiting for QR code scan...")
        await page.wait_for_timeout(5000)
        await page.screenshot(path="qr.png")
        os.system('xdg-open qr.png 2>/dev/null || open qr.png 2>/dev/null')
        
        try:
            await page.wait_for_selector("div[contenteditable='true'][data-tab='10']", timeout=60000)
            print("[+] Login successful")
        except:
            print("[-] QR code scan timeout")
            await context.close()
            await browser.close()
            return False
        
        for i in range(1, count + 1):
            try:
                await page.fill("div[contenteditable='true'][data-tab='10']", "")
                await page.type("div[contenteditable='true'][data-tab='10']", message, delay=100)
                
                # Try both clicking and Enter key
                await page.click("button[data-testid='compose-btn-send']")
                await page.keyboard.press("Enter")
                
                print(f"[+] Sent message {i}/{count}")
                await page.wait_for_timeout(1000 + (i % 3) * 200)  # Random delay
                
            except Exception as e:
                print(f"[-] Error sending message {i}: {str(e)}")
                continue
        
        await context.close()
        await browser.close()
        return True

async def main():
    if len(sys.argv) != 4:
        print(f"\n[!] Usage: {sys.argv[0]} <phone> <count> <message>\n")
        print("Example: ./main_playwright.py 1234567890 5 'Hello World'")
        sys.exit(1)

    phone = sys.argv[1]
    count = int(sys.argv[2])
    message = sys.argv[3]

    start_time = time.time()
    result = await whatsapp_send_messages(phone, count, message)
    end_time = time.time()
    
    if os.path.exists('qr.png'):
        os.remove('qr.png')
    
    if result:
        print(f"\n[+] Successfully sent {count} messages in {end_time-start_time:.2f} seconds")
    else:
        print("\n[-] Message sending failed")

if __name__ == '__main__':
    asyncio.run(main())
