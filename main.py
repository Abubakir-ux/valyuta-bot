import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Vaqtni O'zbekistonga moslash
os.environ['TZ'] = 'Asia/Tashkent'
if hasattr(time, 'tzset'):
    time.tzset()

# Token va Chat ID (To'g'ridan-to'g'ri yozildi)
BOT_TOKEN = "8711798125:AAGXq6hFwcWKYjU8ZhMHGySojqyLYR4wWo0"
CHAT_ID = "-1003805780800"

def tozalash(matn):
    if not matn or matn.strip() == "": return 0
    toza_son = "".join(filter(str.isdigit, matn))
    return int(toza_son) if toza_son else 0

def get_data(info, driver_path):
    name, url, x_paths = info
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    driver.set_page_load_timeout(80)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 40)
        
        if name == "Oltin":
            results = []
            for xp in x_paths:
                val = wait.until(EC.presence_of_element_located((By.XPATH, xp))).text
                results.append(val.strip())
            return {"name": "Oltin", "values": results}
        
        buy = wait.until(EC.presence_of_element_located((By.XPATH, x_paths[0]))).text
        sell = wait.until(EC.presence_of_element_located((By.XPATH, x_paths[1]))).text
        return {"name": name, "buy": buy.strip(), "sell": sell.strip(), "url": url}
    except:
        return None
    finally:
        driver.quit()

tasks = [
    ("Ipak Yo'li", "https://ipakyulibank.uz/physical", ['//*[@id="124"]//tr[1]/td[2]', '//*[@id="124"]//tr[1]/td[3]']),
    ("Davr Bank", "https://davrbank.uz/ru", ['//*[@id="individual-services"]//tr[1]/td[4]', '//*[@id="individual-services"]//tr[1]/td[3]']),
    ("Ziraat Bank", "https://ziraatbank.uz/uz", ['//*[@id="currency-list"]//li[1]//div[1]/span', '//*[@id="currency-list"]//li[1]//div[2]/span']),
    ("OFB Bank", "https://ofb.uz/", ['/html/body/main/section[2]//table/tbody/tr[1]/td[2]//p', '/html/body/main/section[2]//table/tbody/tr[1]/td[3]//p']),
    ("Turon Bank", "https://turonbank.uz/uz/", ['//*[@id="js-main-page"]//tr[2]/td[2]//span', '//*[@id="js-main-page"]//tr[2]/td[3]//span']),
    ("Hamkor Bank", "https://hamkorbank.uz/uz/exchange-rate/", ['//div[contains(@class,"buy")]/div[2]', '//div[contains(@class,"sell")]/div[2]']),
    ("NBU Bank", "https://nbu.uz/jismoniy-shaxslar-valyutalar-kursi", ['//*[@id="02"]//div[2]/div[1]/div[2]/div', '//*[@id="02"]//div[2]/div[1]/div[3]/div']),
    ("Aloqa Bank", "https://aloqabank.uz/ru/services/exchange-rates/", ['//table//tr[2]/td[2]//span', '//table//tr[2]/td[3]//span']),
    ("Xalq Bank", "https://xb.uz/page/valyuta-ayirboshlash", ['//div[contains(@class,"exchange-item")]//div[3]//p', '//div[contains(@class,"exchange-item")]//div[2]//p']),
    ("Trast Bank", "https://trustbank.uz/uz/", ['//table//tr[2]/td[2]//span', '//table//tr[2]/td[3]//span']),
    ("Ipoteka Bank", "https://www.ipotekabank.uz/ru/private/services/currency/", ['//*[@id="all"]//tr[1]/td[2]', '//*[@id="all"]//tr[1]/td[3]']),
    ("Octo Bank", "https://octobank.uz/uz", ['//div[contains(@class,"exchange-row")]/div[2]//p', '//div[contains(@class,"exchange-row")]/div[3]//p']),
    ("Oltin", "https://cbu.uz/oz/banknotes-coins/gold-bars/prices/", [
        "//table//tr[3]/td[2]/p", "//table//tr[4]/td[2]/p", 
        "//table//tr[5]/td[2]/p", "//table//tr[6]/td[2]/p", "//table//tr[7]/td[2]/p"
    ])
]

def run_bot():
    print("🚀 Drayver tayyorlanmoqda...")
    path = ChromeDriverManager().install()
    
    print("🚀 Banklar tekshirilmoqda...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(get_data, cfg, path) for cfg in tasks]
        all_results = [f.result() for f in futures if f.result() is not None]

    banks = [r for r in all_results if r['name'] != "Oltin"]
    gold = next((r for r in all_results if r['name'] == "Oltin"), None)

    if not banks:
        print("❌ Ma'lumot yig'ilmadi.")
        return

    x_val = [tozalash(r['buy']) for r in banks if tozalash(r['buy']) > 10000]
    s_val = [tozalash(r['sell']) for r in banks if tozalash(r['sell']) > 10000]
    ey_x = f"{max(x_val):,}".replace(",", " ") if x_val else "0"
    ey_s = f"{min(s_val):,}".replace(",", " ") if s_val else "0"

    vaqt = time.strftime('%d.%m.%Y %H:%M')
    xabar = f"<b>🏦 KUNLIK VALYUTA NARXLARI ($)</b>\n— — — — — — — — — — — — — — —\n"
    xabar += f"🏛 Bank nomi          |  Xarid  |  Sotuv \n— — — — — — — — — — — — — — —\n"

    for r in banks:
        xabar += f"🔹 <a href='{r['url']}'>{r['name']:<14}</a> | {r['buy']:<5} | {r['sell']}\n"

    xabar += f"— — — — — — — — — — — — — — —\n"
    xabar += f"<blockquote>Eng yaxshi narx: | {ey_x} | {ey_s} 📈</blockquote>\n"

    if gold:
        g = gold['values']
        xabar += f"<b>💰 Quyma oltin narxlari:</b>\n🟡 5 gr: {g[0]} | 10 gr: {g[1]}\n🟡 20 gr: {g[2]} | 50 gr: {g[3]}\n🟡 100 gr: {g[4]}\n"

    xabar += f"\n🕒 <b>Yangilandi:</b> {vaqt}\n📢 @dollorkurslariUZ"

    print("📤 Telegramga yuborilmoqda...")
    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
        data={"chat_id": CHAT_ID, "text": xabar, "parse_mode": "HTML", "disable_web_page_preview": True}
    )
    
    if resp.status_code != 200:
        print(f"❌ Telegram xatosi: {resp.text}")
    else:
        print("✅ Telegram'ga muvaffaqiyatli yuborildi!")

if __name__ == "__main__":
    run_bot()
