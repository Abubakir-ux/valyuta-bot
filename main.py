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

# Token va Chat ID
BOT_TOKEN = "8711798125:AAGXq6hFwcWKYjU8ZhMHGySojqyLYR4wWo0"
CHAT_ID = "-1003805780800"

def tozalash(matn):
    if not matn: return 0
    # Faqat raqamlarni ajratib olish
    toza_son = "".join(filter(str.isdigit, str(matn)))
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
                if val.strip():
                    results.append(val.strip())
            return {"name": "Oltin", "values": results} if len(results) > 0 else None
        
        buy_raw = wait.until(EC.presence_of_element_located((By.XPATH, x_paths[0]))).text
        sell_raw = wait.until(EC.presence_of_element_located((By.XPATH, x_paths[1]))).text
        
        # Agar narxlar bo'sh bo'lsa, bu bankni qaytarmaymiz
        if not buy_raw.strip() or not sell_raw.strip():
            return None
            
        return {
            "name": name, 
            "buy": buy_raw.strip(), 
            "sell": sell_raw.strip(), 
            "url": url,
            "buy_num": tozalash(buy_raw),
            "sell_num": tozalash(sell_raw)
        }
    except:
        return None
    finally:
        driver.quit()

# XPathlaring o'zgarishsiz qoldi
tasks = [
    ("Ipak Yo'li", "https://ipakyulibank.uz/physical", ['//*[@id="124"]/div[2]/div/div[2]/table/tbody/tr[1]/td[2]', '//*[@id="124"]/div[2]/div/div[2]/table/tbody/tr[1]/td[3]']),
    ("Davr Bank", "https://davrbank.uz/ru", ['//*[@id="individual-services"]/div/div[1]/div[2]/table/tbody/tr[1]/td[4]', '//*[@id="individual-services"]/div/div[1]/div[2]/table/tbody/tr[1]/td[3]']),
    ("OFB Bank", "https://ofb.uz/", ['/html/body/main/section[2]/div/div[2]/div[1]/div[2]/div/table/tbody/tr[1]/td[2]/div/p', '/html/body/main/section[2]/div/div[2]/div[1]/div[2]/div/table/tbody/tr[1]/td[3]/div/p']),
    ("Turon Bank", "https://turonbank.uz/uz/", ['//*[@id="js-main-page"]/div[1]/div/div/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[2]/div/span', '//*[@id="js-main-page"]/div[1]/div/div/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[3]/div/span']),
    ("Hamkor Bank", "https://hamkorbank.uz/uz/exchange-rate/", ['//*[@id="block_mAWMGK"]/div/div[4]/div[2]/div[2]/div[2]', '//*[@id="block_mAWMGK"]/div/div[4]/div[2]/div[3]/div[2]']),
    ("NBU Bank", "https://nbu.uz/jismoniy-shaxslar-valyutalar-kursi", ['//*[@id="02"]/div/div/div/div[1]/div[2]/div[1]/div[2]/div', '//*[@id="02"]/div/div/div/div[1]/div[2]/div[1]/div[3]/div']),
    ("Aloqa Bank", "https://aloqabank.uz/ru/services/exchange-rates/", ['/html/body/div[2]/div[5]/div/div[2]/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[2]/div/span', '/html/body/div[2]/div[5]/div/div[2]/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[3]/div/span']),
    ("Xalq Bank", "https://xb.uz/page/valyuta-ayirboshlash", ['//*[@id="__next"]/div[2]/main/div/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/div[3]/div/div/p', '//*[@id="__next"]/div[2]/main/div/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/p']),
    ("Trast Bank", "https://trustbank.uz/uz/", ['/html/body/div[2]/div[4]/section[2]/div/div/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[2]/td[2]/div/span', '/html/body/div[2]/div[4]/section[2]/div/div/div/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[2]/td[3]/div/span']),
    ("Ipoteka Bank", "https://www.ipotekabank.uz/ru/private/services/currency/", ['//*[@id="all"]/div/table/tbody/tr[1]/td[2]', '//*[@id="all"]/div/table/tbody/tr[1]/td[3]']),
    ("Octo Bank", "https://octobank.uz/uz", ['//*[@id="w-node-_23a24b74-a88d-5f36-44f5-45399e0decee-9e0dece1"]/div[2]/div/div[1]/p', '//*[@id="w-node-_23a24b74-a88d-5f36-44f5-45399e0decee-9e0dece1"]/div[2]/div/div[2]/p']),
    ("Oltin", "https://cbu.uz/oz/banknotes-coins/gold-bars/prices/", [
        "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[3]/td[2]/p", 
        "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[4]/td[2]/p", 
        "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[5]/td[2]/p", 
        "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[6]/td[2]/p", 
        "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[7]/td[2]/p"
    ])
]

def run_bot():
    print("🚀 Drayver tayyorlanmoqda...")
    path = ChromeDriverManager().install()
    
    print("🚀 Banklar tekshirilmoqda...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(get_data, cfg, path) for cfg in tasks]
        all_results = [f.result() for f in futures if f.result() is not None]

    # Faqat narxi nolga teng bo'lmagan banklarni qoldiramiz
    banks = [r for r in all_results if r['name'] != "Oltin" and r.get('buy_num', 0) > 0]
    gold = next((r for r in all_results if r['name'] == "Oltin"), None)

    if not banks:
        print("❌ Hech qanday bankdan to'g'ri ma'lumot kelmadi.")
        return

    # Eng yaxshi narxlar
    ey_x_val = max([r['buy_num'] for r in banks])
    ey_s_val = min([r['sell_num'] for r in banks])
    
    ey_x = f"{ey_x_val:,}".replace(",", " ")
    ey_s = f"{ey_s_val:,}".replace(",", " ")

    vaqt = time.strftime('%d.%m.%Y %H:%M')
    xabar = f"<b>🏦 KUNLIK VALYUTA NARXLARI ($)</b>\n— — — — — — — — — — — — — — —\n"
    xabar += f"🏛 Bank nomi          |  Xarid  |  Sotuv \n— — — — — — — — — — — — — — —\n"

    for r in banks:
        xabar += f"🔹 <a href='{r['url']}'>{r['name']:<14}</a> | {r['buy']:<5} | {r['sell']}\n"

    xabar += f"— — — — — — — — — — — — — — —\n"
    xabar += f"<blockquote>Eng yaxshi narx: | {ey_x} | {ey_s} 📈</blockquote>\n"

    if gold and len(gold.get('values', [])) >= 5:
        g = gold['values']
        xabar += f"<b>💰 Quyma oltin narxlari:</b>\n🟡 5 грамм: {g[0]} | 10 грамм: {g[1]}\n🟡 20 грамм: {g[2]} | 50 грамм: {g[3]}\n🟡 100 грамм: {g[4]}\n"

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
