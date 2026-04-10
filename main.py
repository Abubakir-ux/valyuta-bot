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

# 1. Vaqtni O'zbekistonga moslash
os.environ['TZ'] = 'Asia/Tashkent'
if hasattr(time, 'tzset'):
    time.tzset()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8711798125:AAGXq6hFwcWKYjU8ZhMHGySojqyLYR4wWo0")
CHAT_ID = os.getenv("CHAT_ID", "-1003805780800")

def tozalash(matn):
    if not matn or matn.strip() == "": return 0
    toza_son = "".join(filter(str.isdigit, matn))
    return int(toza_son) if toza_son else 0

def get_bank_data(bank_info):
    name, url, x_path, s_path = bank_info
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(60)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 30)
        buy = wait.until(EC.presence_of_element_located((By.XPATH, x_path))).text
        sell = wait.until(EC.presence_of_element_located((By.XPATH, s_path))).text
        return {"name": name, "buy": buy.strip(), "sell": sell.strip(), "url": url}
    except:
        return None
    finally:
        driver.quit()

# Banklar konfiguratsiyasi (Sening XPath'laring yangilandi)
banks_config = [
    ("Ipak Yo'li", "https://ipakyulibank.uz/physical", "//div[contains(@class, 'exchange-rates')]//table//tr[td[contains(.,'USD')]]/td[2]", "//div[contains(@class, 'exchange-rates')]//table//tr[td[contains(.,'USD')]]/td[3]"),
    ("Davr Bank", "https://davrbank.uz/ru", '//*[@id="individual-services"]/div/div[1]/div[2]/table/tbody/tr[1]/td[4]', '//*[@id="individual-services"]/div/div[1]/div[2]/table/tbody/tr[1]/td[3]'),
    ("Ziraat Bank", "https://ziraatbank.uz/uz", '//*[@id="currency-list"]/ul/li[1]/div/div[1]/span', '//*[@id="currency-list"]/ul/li[1]/div/div[2]/span'),
    ("OFB Bank", "https://ofb.uz/", '//table//tr[td[contains(., "USD")]]/td[2]', '//table//tr[td[contains(., "USD")]]/td[3]'),
    ("Turon Bank", "https://turonbank.uz/uz/", "//table//tr[td//span[contains(.,'USD')]]/td[2]//span", "//table//tr[td//span[contains(.,'USD')]]/td[3]//span"),
    ("Hamkor Bank", "https://hamkorbank.uz/uz/exchange-rate/", "//div[contains(@class, 'currency__item') and .//span[text()='USD']]//div[contains(@class, 'buy')]/div[2]", "//div[contains(@class, 'currency__item') and .//span[text()='USD']]//div[contains(@class, 'sell')]/div[2]"),
    ("NBU Bank", "https://nbu.uz/jismoniy-shaxslar-valyutalar-kursi", "//div[contains(@class, 'course-item') and .//div[contains(text(), 'USD')]]/div[2]/div", "//div[contains(@class, 'course-item') and .//div[contains(text(), 'USD')]]/div[3]/div"),
    ("Aloqa Bank", "https://aloqabank.uz/ru/services/exchange-rates/", "//table//tr[td//span[contains(.,'USD')]]/td[2]//span", "//table//tr[td//span[contains(.,'USD')]]/td[3]//span"),
    ("Xalq Bank", "https://xb.uz/page/valyuta-ayirboshlash", "//div[contains(@class, 'exchange-item') and .//p[contains(.,'USD')]]//div[3]//p", "//div[contains(@class, 'exchange-item') and .//p[contains(.,'USD')]]//div[2]//p"),
    ("Trast Bank", "https://trustbank.uz/uz/", "//table//tr[td//span[contains(.,'USD')]]/td[2]//span", "//table//tr[td//span[contains(.,'USD')]]/td[3]//span"),
    ("Ipoteka Bank", "https://www.ipotekabank.uz/ru/private/services/currency/", "//table//tr[td[contains(.,'USD')]]/td[2]", "//table//tr[td[contains(.,'USD')]]/td[3]"),
    ("Octo Bank", "https://octobank.uz/uz", "//div[contains(@class, 'exchange-row') and .//p[contains(.,'USD')]]/div[2]//p", "//div[contains(@class, 'exchange-row') and .//p[contains(.,'USD')]]/div[3]//p")
]

def run_bot():
    print("Ma'lumotlar bir vaqtda yig'ilmoqda...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(filter(None, executor.map(get_bank_data, banks_config)))

    # Oltin narxlari uchun alohida (CBU)
    oltin = get_bank_data(("Oltin", "https://cbu.uz/oz/banknotes-coins/gold-bars/prices/", "//table//tr[td[contains(.,'5')]]/td[2]/p", "//table//tr[td[contains(.,'100')]]/td[2]/p"))

    if not results: return

    # Eng yaxshi narxlar
    x_val = [tozalash(r['buy']) for r in results if tozalash(r['buy']) > 10000]
    s_val = [tozalash(r['sell']) for r in results if tozalash(r['sell']) > 10000]
    ey_x = f"{max(x_val):,}".replace(",", " ") if x_val else "0"
    ey_s = f"{min(s_val):,}".replace(",", " ") if s_val else "0"

    # Xabarni yig'ish
    vaqt = time.strftime('%d.%m.%Y %H:%M')
    xabar = f"<b>🏦 KUNLIK VALYUTA NARXLARI ($)</b>\n"
    xabar += f"— — — — — — — — — — — — — — —\n"
    xabar += f"🏛 Bank nomi          |  Xarid  |  Sotuv \n"
    xabar += f"— — — — — — — — — — — — — — —\n"

    for r in results:
        xabar += f"🔹 <a href='{r['url']}'>{r['name']:<14}</a> | {r['buy']:<5} | {r['sell']}\n"

    xabar += f"— — — — — — — — — — — — — — —\n"
    xabar += f"<blockquote>Eng yaxshi narx: | {ey_x} | {ey_s} 📈</blockquote>\n"
    xabar += f"🕒 <b>Yangilandi:</b> {vaqt}\n\n📢 @dollorkurslariUZ"

    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": xabar, "parse_mode": "HTML", "disable_web_page_preview": True})

if __name__ == "__main__":
    run_bot()
