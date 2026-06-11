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

# Token va Chat ID — GitHub Secrets dan olinadi
BOT_TOKEN = os.getenv("8711798125:AAGXq6hFwcWKYjU8ZhMHGySojqyLYR4wWo0")
CHAT_ID = os.getenv("-1003805780800")

# Vaqtga qarab salom
def vaqt_salomi():
    soat = int(time.strftime('%H'))
    if 5 <= soat < 12:
        return "🌅 Xayrli tong!"
    elif 12 <= soat < 17:
        return "☀️ Xayrli kun!"
    else:
        return "🌙 Xayrli kech!"

def tozalash(matn):
    if not matn:
        return 0
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
            return {"name": "Oltin", "values": results} if results else None

        buy_raw = wait.until(EC.presence_of_element_located((By.XPATH, x_paths[0]))).text
        sell_raw = wait.until(EC.presence_of_element_located((By.XPATH, x_paths[1]))).text
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

tasks = [
    ("Ipak Yo'li",  "https://ipakyulibank.uz/physical",                    ['//*[@id="124"]/div[2]/div/div[2]/table/tbody/tr[1]/td[2]', '//*[@id="124"]/div[2]/div/div[2]/table/tbody/tr[1]/td[3]']),
    ("Davr Bank",   "https://davrbank.uz/ru",                               ['//*[@id="individual-services"]/div/div[1]/div[2]/table/tbody/tr[1]/td[4]', '//*[@id="individual-services"]/div/div[1]/div[2]/table/tbody/tr[1]/td[3]']),
    ("OFB Bank",    "https://ofb.uz/",                                      ['/html/body/main/section[2]/div/div[2]/div[1]/div[2]/div/table/tbody/tr[1]/td[2]/div/p', '/html/body/main/section[2]/div/div[2]/div[1]/div[2]/div/table/tbody/tr[1]/td[3]/div/p']),
    ("Turon Bank",  "https://turonbank.uz/uz/",                             ['//*[@id="js-main-page"]/div[1]/div/div/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[2]/div/span', '//*[@id="js-main-page"]/div[1]/div/div/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[3]/div/span']),
    ("Hamkor Bank", "https://hamkorbank.uz/uz/exchange-rate/",              ['//*[@id="block_mAWMGK"]/div/div[4]/div[2]/div[2]/div[2]', '//*[@id="block_mAWMGK"]/div/div[4]/div[2]/div[3]/div[2]']),
    ("NBU Bank",    "https://nbu.uz/jismoniy-shaxslar-valyutalar-kursi",   ['//*[@id="02"]/div/div/div/div[1]/div[2]/div[1]/div[2]/div', '//*[@id="02"]/div/div/div/div[1]/div[2]/div[1]/div[3]/div']),
    ("Aloqa Bank",  "https://aloqabank.uz/ru/services/exchange-rates/",    ['/html/body/div[2]/div[5]/div/div[2]/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[2]/div/span', '/html/body/div[2]/div[5]/div/div[2]/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[3]/div/span']),
    ("Xalq Bank",   "https://xb.uz/page/valyuta-ayirboshlash",             ['//*[@id="__next"]/div[2]/main/div/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/div[3]/div/div/p', '//*[@id="__next"]/div[2]/main/div/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/p']),
    ("Trast Bank",  "https://trustbank.uz/uz/",                            ['/html/body/div[2]/div[4]/section[2]/div/div/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[2]/td[2]/div/span', '/html/body/div[2]/div[4]/section[2]/div/div/div/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[2]/td[3]/div/span']),
    ("Ipoteka Bank","https://www.ipotekabank.uz/ru/private/services/currency/", ['//*[@id="all"]/div/table/tbody/tr[1]/td[2]', '//*[@id="all"]/div/table/tbody/tr[1]/td[3]']),
    ("Octo Bank",   "https://octobank.uz/uz",                              ['//*[@id="w-node-_23a24b74-a88d-5f36-44f5-45399e0decee-9e0dece1"]/div[2]/div/div[1]/p', '//*[@id="w-node-_23a24b74-a88d-5f36-44f5-45399e0decee-9e0dece1"]/div[2]/div/div[2]/p']),
    ("Oltin",       "https://cbu.uz/oz/banknotes-coins/gold-bars/prices/", [
        "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[3]/td[2]/p",
        "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[4]/td[2]/p",
        "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[5]/td[2]/p",
        "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[6]/td[2]/p",
        "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[7]/td[2]/p"
    ]),
]

def ma_lumot_yig(path):
    """Barcha banklardan ma'lumot yig'adi"""
    print("🏦 Banklar tekshirilmoqda...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(get_data, cfg, path) for cfg in tasks]
        all_results = [f.result() for f in futures if f.result() is not None]

    banks = [r for r in all_results if r['name'] != "Oltin" and r.get('buy_num', 0) > 0]
    gold = next((r for r in all_results if r['name'] == "Oltin"), None)
    return banks, gold

def xabar_shaklla(banks, gold, kanal=True):
    """Chiroyli xabar shakllantiradi"""
    if not banks:
        return None

    ey_x_val = max(r['buy_num'] for r in banks)
    ey_s_val = min(r['sell_num'] for r in banks)
    ey_x_bank = next(r['name'] for r in banks if r['buy_num'] == ey_x_val)
    ey_s_bank = next(r['name'] for r in banks if r['sell_num'] == ey_s_val)
    ey_x = f"{ey_x_val:,}".replace(",", " ")
    ey_s = f"{ey_s_val:,}".replace(",", " ")
    vaqt = time.strftime('%d.%m.%Y %H:%M')
    salom = vaqt_salomi()

    # ===== KANAL UCHUN CHIROYLI XABAR =====
    if kanal:
        xabar  = f"{salom}\n"
        xabar += f"━━━━━━━━━━━━━━━━━━━━━━\n"
        xabar += f"💵 <b>DOLLAR KURSI — {time.strftime('%d.%m.%Y')}</b>\n"
        xabar += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        xabar += f"{'🏛 Bank':<16} {'📥 Xarid':>10} {'📤 Sotuv':>10}\n"
        xabar += f"{'─'*38}\n"
        for r in banks:
            xabar += f"🔹 <a href='{r['url']}'>{r['name']:<14}</a>  {r['buy']:>8}  {r['sell']:>8}\n"
        xabar += f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
        xabar += f"🏆 <b>Eng yaxshi narxlar:</b>\n"
        xabar += f"   📥 Xarid: <b>{ey_x} so'm</b> — {ey_x_bank}\n"
        xabar += f"   📤 Sotuv: <b>{ey_s} so'm</b> — {ey_s_bank}\n"

    # ===== LICHKA UCHUN XABAR =====
    else:
        xabar  = f"💵 <b>BUGUNGI DOLLAR KURSI</b>\n"
        xabar += f"📅 {vaqt}\n"
        xabar += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for r in banks:
            xabar += f"🏦 <b>{r['name']}</b>\n"
            xabar += f"   📥 Xarid: <code>{r['buy']}</code> so'm\n"
            xabar += f"   📤 Sotuv: <code>{r['sell']}</code> so'm\n\n"
        xabar += f"━━━━━━━━━━━━━━━━━━━━━━\n"
        xabar += f"🏆 <b>Eng yaxshi:</b>\n"
        xabar += f"📥 Xarid: <b>{ey_x} so'm</b> ({ey_x_bank})\n"
        xabar += f"📤 Sotuv: <b>{ey_s} so'm</b> ({ey_s_bank})\n"

    # Oltin narxlari (ikkalasida ham)
    if gold and len(gold.get('values', [])) >= 5:
        g = gold['values']
        xabar += f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
        xabar += f"💰 <b>QUYMA OLTIN NARXLARI</b>\n"
        xabar += f"🟡   5 gr: <code>{g[0]}</code> so'm\n"
        xabar += f"🟡  10 gr: <code>{g[1]}</code> so'm\n"
        xabar += f"🟡  20 gr: <code>{g[2]}</code> so'm\n"
        xabar += f"🟡  50 gr: <code>{g[3]}</code> so'm\n"
        xabar += f"🟡 100 gr: <code>{g[4]}</code> so'm\n"

    if kanal:
        xabar += f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
        xabar += f"🕒 Yangilandi: {vaqt}\n"
        xabar += f"📢 @dollorkurslariUZ"

    return xabar

def telegram_yuborish(chat_id, xabar):
    """Telegram ga xabar yuboradi"""
    print(f"📡 Yuborilmoqda... chat_id={chat_id}, token={BOT_TOKEN[:10]}...")
    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": xabar,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
    )
    print(f"📬 Telegram javobi: {resp.status_code} — {resp.text}")
    return resp.status_code == 200

# ==========================================
# KANALGA AVTOMATIK XABAR (GitHub Actions)
# ==========================================
def run_bot():
    print("🚀 Drayver tayyorlanmoqda...")
    path = ChromeDriverManager().install()
    banks, gold = ma_lumot_yig(path)

    if not banks:
        print("❌ Banklardan ma'lumot kelmadi.")
        return

    xabar = xabar_shaklla(banks, gold, kanal=True)
    print("📤 Kanalga yuborilmoqda...")
    if telegram_yuborish(CHAT_ID, xabar):
        print("✅ Muvaffaqiyatli yuborildi!")
    else:
        print("❌ Yuborishda xatolik!")

# ==========================================
# /kurs KOMANDASI UCHUN (Polling)
# ==========================================
def polling():
    print("🤖 Bot ishga tushdi — /kurs komandasi kutilmoqda...")
    path = ChromeDriverManager().install()
    offset = 0

    while True:
        try:
            resp = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                params={"offset": offset, "timeout": 30},
                timeout=35
            )
            updates = resp.json().get("result", [])

            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message", {})
                text = message.get("text", "")
                chat_id = message.get("chat", {}).get("id")

                if text.lower() in ["/kurs", "/start"]:
                    if text.lower() == "/start":
                        salom_xabar = (
                            "👋 <b>Assalomu alaykum!</b>\n\n"
                            "Men <b>Valyuta Bot</b>man 🤖\n\n"
                            "📌 <b>Buyruqlar:</b>\n"
                            "💵 /kurs — Bugungi dollar kursi\n\n"
                            "📢 Kanalimiz: @dollorkurslariUZ"
                        )
                        telegram_yuborish(chat_id, salom_xabar)
                    else:
                        # /kurs so'raldi
                        yuklash = requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            data={"chat_id": chat_id, "text": "⏳ Kurslar yuklanmoqda, biroz kuting..."}
                        )
                        banks, gold = ma_lumot_yig(path)
                        if banks:
                            xabar = xabar_shaklla(banks, gold, kanal=False)
                            telegram_yuborish(chat_id, xabar)
                        else:
                            telegram_yuborish(chat_id, "❌ Ma'lumot olishda xatolik. Keyinroq urinib ko'ring.")

        except Exception as e:
            print(f"⚠️ Xatolik: {e}")
            time.sleep(5)

# ==========================================
# ISHGA TUSHIRISH
# ==========================================
if __name__ == "__main__":
    mode = os.getenv("MODE", "send")   # "send" = kanalga yuborish, "poll" = polling
    if mode == "poll":
        polling()
    else:
        run_bot()
