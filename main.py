import os
import re
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
# Token va Chat ID — ENDI KODDA EMAS!
# Serverda/kompyuteringizda muhit o'zgaruvchisi sifatida bering:
#   export BOT_TOKEN="..."
#   export CHAT_ID="..."
# GitHub Actions'da bo'lsa -> Settings -> Secrets and variables -> Actions
# ============================================================
BOT_TOKEN = os.environ.get("8917271946:AAF0ZmXyuApYQd-AZIG56kCvLr5qU2B_y2k")
CHAT_ID = os.environ.get("-1003805780800")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def tozalash(matn):
    """Matndan faqat raqamlarni ajratib oladi."""
    if not matn:
        return 0
    toza_son = "".join(filter(str.isdigit, str(matn)))
    return int(toza_son) if toza_son else 0


# ============================================================
# 1) BARCHA BANKLARNING USD KURSI — bank.uz orqali (Selenium'siz!)
#    bank.uz sahifasida deyarli barcha O'zbekiston banklari bitta
#    joyda ko'rsatiladi, shuning uchun 10-15 ta saytga alohida
#    kirishning hojati yo'q — tezroq va barqarorroq.
# ============================================================
def get_bankuz_rates():
    url = "https://bank.uz/uz/currency"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # USD blokini topamiz (sahifada har bir valyuta uchun alohida blok bor)
    container = soup.find(id="best_USD")
    if container is None:
        # zaxira variant: butun sahifadan qidiramiz
        container = soup

    container_html = str(container)

    # "Sotib olish" (bank sizdan xarid qiladi) va "Sotish" (bank sizga sotadi)
    # bloklarini ажратамiz. "Sotish" so'zi "Sotib olish" ichida uchramaydi,
    # shuning uchun bemalol ajratsak bo'ladi.
    split_idx = container_html.find(">Sotish<")
    if split_idx == -1:
        raise ValueError("bank.uz sahifa tuzilishi o'zgargan bo'lishi mumkin (Sotish bo'limi topilmadi)")

    buy_html = container_html[:split_idx]
    sell_html = container_html[split_idx:]

    def extract(html_piece):
        piece_soup = BeautifulSoup(html_piece, "html.parser")
        result = {}
        for a in piece_soup.find_all("a", href=re.compile(r"/currency/bank/")):
            name = a.get_text(strip=True)
            if not name:
                continue
            price_node = a.find_next(string=re.compile(r"so'm"))
            val = tozalash(price_node)
            if val > 0 and name not in result:
                href = a.get("href", "")
                full_url = "https://bank.uz" + href if href.startswith("/") else href
                result[name] = {"val": val, "url": full_url}
        return result

    buy = extract(buy_html)
    sell = extract(sell_html)
    return buy, sell


# ============================================================
# 2) OLTIN NARXI — cbu.uz (Markaziy bank), eski Selenium usuli
#    saqlanib qolgan, chunki faqat bitta sayt va u ishlab turibdi.
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
# ASOSIY ISHGA TUSHIRISH FUNKSIYASI
# ============================================================
def run_bot():
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN yoki CHAT_ID muhit o'zgaruvchisi topilmadi. "
              "Ularni environment variable sifatida belgilang.")
        return

    print("💱 bank.uz orqali barcha banklar kursi olinmoqda...")
    try:
        buy, sell = get_bankuz_rates()
    except Exception as e:
        print(f"❌ bank.uz'dan ma'lumot olishda xatolik: {e}")
        return

    # faqat ikkala ro'yxatda ham (xarid va sotuv) mavjud banklarni olamiz
    common_names = [n for n in buy.keys() if n in sell]

    print(f"✅ {len(common_names)} ta bank topildi.")
    if len(common_names) < 5:
        print("❌ Juda kam bank topildi, ehtimol sayt tuzilishi o'zgargan. Xabar yuborilmadi.")
        return

    banks = []
    for name in common_names:
        banks.append({
            "name": name,
            "buy_num": buy[name]["val"],
            "sell_num": sell[name]["val"],
            "url": buy[name]["url"],
        })
    # eng yaxshi narx yuqorida turishi uchun xarid bo'yicha kamayish tartibida saralaymiz
    banks.sort(key=lambda r: r["buy_num"], reverse=True)

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
