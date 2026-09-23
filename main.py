import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================
# Vaqtni O'zbekistonga moslash
# ============================================================
os.environ['TZ'] = 'Asia/Tashkent'
if hasattr(time, 'tzset'):
    time.tzset()

# ============================================================
# Token va Chat ID — muhit o'zgaruvchisi sifatida beriladi
# GitHub Actions -> Settings -> Secrets and variables -> Actions
# BOT_TOKEN = botfather tokeni
# CHAT_ID   = kanal ID (masalan @dollorkurslariUZ yoki -100...)
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "uz,ru;q=0.9,en;q=0.8",
}

OFFSET_FILE = "offset.txt"


def tozalash(matn):
    """Matndan faqat raqamlarni ajratib oladi."""
    if not matn:
        return 0
    toza_son = "".join(filter(str.isdigit, str(matn)))
    return int(toza_son) if toza_son else 0


def tg_send(chat_id, text, parse_mode="HTML"):
    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": chat_id, "text": text, "parse_mode": parse_mode,
              "disable_web_page_preview": True},
    )
    if resp.status_code != 200:
        print(f"❌ Telegram xatosi ({chat_id}): {resp.text}")
    return resp


# ============================================================
# 1) BARCHA BANKLARNING USD KURSI — bank.uz orqali
# Har bir bank ALOHIDA qayta ishlanadi: birontasi noto'g'ri
# chiqsa, faqat o'sha bank tashlab ketiladi, qolganlari yuboriladi.
# ============================================================
def get_all_bank_rates():
    url = "https://bank.uz/uz/currency"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    container = soup.find(id="best_USD") or soup
    html = str(container)

    split_idx = html.find(">Sotish<")
    if split_idx == -1:
        raise ValueError(
            f"bank.uz sahifa tuzilishi o'zgargan bo'lishi mumkin "
            f"(javob uzunligi={len(resp.text)}, status={resp.status_code})"
        )

    buy_html, sell_html = html[:split_idx], html[split_idx:]

    def extract(piece_html):
        piece_soup = BeautifulSoup(piece_html, "html.parser")
        out = {}
        for a in piece_soup.find_all("a", href=re.compile(r"/currency/bank/")):
            name = a.get_text(strip=True)
            if not name:
                continue
            try:
                price_node = a.find_next(string=re.compile(r"so'm"))
                val = tozalash(price_node)
                href = a.get("href", "")
                full_url = "https://bank.uz" + href if href.startswith("/") else href
                if val > 0 and name not in out:
                    out[name] = {"val": val, "url": full_url}
            except Exception as e:
                print(f"⚠️ '{name}' o'tkazib yuborildi: {e}")
                continue
        return out

    buy = extract(buy_html)
    sell = extract(sell_html)

    banks = []
    skipped = []
    for name in set(buy.keys()) | set(sell.keys()):
        if name in buy and name in sell:
            banks.append({
                "name": name,
                "buy_num": buy[name]["val"],
                "sell_num": sell[name]["val"],
                "url": buy[name]["url"],
            })
        else:
            skipped.append(name)

    banks.sort(key=lambda r: r["buy_num"], reverse=True)
    return banks, skipped


# ============================================================
# 2) OLTIN NARXI — cbu.uz (Markaziy bank)
# ============================================================
GOLD_URL = "https://cbu.uz/oz/banknotes-coins/gold-bars/prices/"
GOLD_XPATHS = [
    "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[3]/td[2]/p",
    "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[4]/td[2]/p",
    "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[5]/td[2]/p",
    "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[6]/td[2]/p",
    "/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[7]/td[2]/p",
]


def get_gold_prices(driver_path):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    driver.set_page_load_timeout(80)
    try:
        driver.get(GOLD_URL)
        wait = WebDriverWait(driver, 40)
        values = []
        for xp in GOLD_XPATHS:
            val = wait.until(EC.presence_of_element_located((By.XPATH, xp))).text
            if val.strip():
                values.append(val.strip())
        return values if len(values) >= 5 else None
    except Exception as e:
        print(f"⚠️ Oltin narxini olishda xatolik: {e}")
        return None
    finally:
        driver.quit()


# ============================================================
# REJIM 1: "send" — kurslarni kanalga yuborish
# (GitHub Actions'da 09:00, 13:00, 19:00 da cron orqali chaqiriladi)
# ============================================================
def run_send():
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN yoki CHAT_ID muhit o'zgaruvchisi topilmadi.")
        return

    print("💱 bank.uz orqali barcha banklar kursi olinmoqda...")
    try:
        banks, skipped = get_all_bank_rates()
    except Exception as e:
        print(f"❌ bank.uz'dan ma'lumot olishda xatolik: {e}")
        return

    print(f"✅ {len(banks)} ta bank topildi.")
    if skipped:
        print(f"⚠️ O'tkazib yuborildi ({len(skipped)} ta): {', '.join(skipped)}")

    if len(banks) < 5:
        print("❌ Juda kam bank topildi, ehtimol sayt tuzilishi o'zgargan. Xabar yuborilmadi.")
        return

    print("🥇 Oltin narxi olinmoqda...")
    path = ChromeDriverManager().install()
    gold_values = get_gold_prices(path)

    ey_x_val = max(r["buy_num"] for r in banks)
    ey_s_val = min(r["sell_num"] for r in banks)
    ey_x = f"{ey_x_val:,}".replace(",", " ")
    ey_s = f"{ey_s_val:,}".replace(",", " ")
    vaqt = time.strftime('%d.%m.%Y %H:%M')

    xabar = f"<b>🏦 KUNLIK VALYUTA NARXLARI ($)</b>\n— — — — — — — — — — — — — — —\n"
    xabar += f"🏛 Bank nomi | Xarid | Sotuv \n— — — — — — — — — — — — — — —\n"
    for r in banks:
        buy_str = f"{r['buy_num']:,}".replace(",", " ")
        sell_str = f"{r['sell_num']:,}".replace(",", " ")
        xabar += f"🔹 <a href='{r['url']}'>{r['name']:<14}</a> | {buy_str:<7} | {sell_str}\n"
    xabar += f"— — — — — — — — — — — — — — —\n"
    xabar += f"<blockquote>Eng yaxshi narx: | {ey_x} | {ey_s} 📈</blockquote>\n"

    if gold_values:
        g = gold_values
        xabar += (f"<b>💰 Quyma oltin narxlari:</b>\n"
                  f"🟡 5 грамм: {g[0]} | 10 грамм: {g[1]}\n"
                  f"🟡 20 грамм: {g[2]} | 50 грамм: {g[3]}\n"
                  f"🟡 100 грамм: {g[4]}\n")

    if skipped:
        xabar += f"\n<i>⚠️ Ushbu banklar o'tkazib yuborildi: {', '.join(skipped)}</i>\n"

    xabar += f"\n🕒 <b>Yangilandi:</b> {vaqt}\n📢 @dollorkurslariUZ"

    print("📤 Telegramga yuborilmoqda...")
    tg_send(CHAT_ID, xabar)
    print(f"✅ Yuborildi: {len(banks)} ta bank kursi. O'tkazib yuborilganlar: {len(skipped)} ta.")


# ============================================================
# REJIM 2: "listen" — /start va kanalga admin qilib qo'shilganini tinglash
# (GitHub Actions'da har 2-3 daqiqada chaqiriladi)
# ============================================================
def run_listen():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN topilmadi.")
        return

    try:
        with open(OFFSET_FILE) as f:
            offset = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        offset = 0

    resp = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
        params={"offset": offset, "timeout": 0, "allowed_updates": '["message","my_chat_member"]'},
        timeout=20,
    )
    data = resp.json()
    if not data.get("ok"):
        print(f"❌ getUpdates xatosi: {data}")
        return

    updates = data.get("result", [])
    print(f"📥 {len(updates)} ta yangi hodisa.")

    for u in updates:
        offset = u["update_id"] + 1

        # /start bosilganda
        msg = u.get("message")
        if msg and msg.get("text", "").startswith("/start"):
            chat_id = msg["chat"]["id"]
            matn = (
                "👋 Salom!\n\n"
                "Men O'zbekiston banklaridagi dollar kurslari va quyma oltin "
                "narxlarini kuzataman.\n\n"
                "📌 Meni kanalingizga <b>admin</b> qilib qo'shing — har kuni soat "
                "09:00, 13:00 va 19:00 da yangilangan narxlarni avtomatik yuborib turaman."
            )
            tg_send(chat_id, matn)
            print(f"✅ /start javobi yuborildi: {chat_id}")

        # kanalga admin qilib qo'shilganda
        cm = u.get("my_chat_member")
        if cm:
            chat = cm["chat"]
            new_status = cm["new_chat_member"]["status"]
            if new_status == "administrator":
                tg_send(
                    chat["id"],
                    "✅ Admin qilib qo'shganingiz uchun rahmat!\n"
                    "Endi har kuni 09:00, 13:00, 19:00 da kurslarni shu yerga yuboraman.",
                )
                print(f"✅ Admin xabari yuborildi: {chat['id']} ({chat.get('title')})")

    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))


# ============================================================
# KIRISH NUQTASI
# python main.py send    -> kurslarni yuborish
# python main.py listen  -> /start va admin hodisalarini tinglash
# ============================================================
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "send"
    if mode == "send":
        run_send()
    elif mode == "listen":
        run_listen()
    else:
        print(f"❌ Noma'lum rejim: {mode}. 'send' yoki 'listen' dan birini bering.")
