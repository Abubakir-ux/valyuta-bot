import os
import re
import sys
import json
import time
import datetime
import requests

# ============================================================
# bs4/Selenium — FAQAT "send" rejimida kerak, "listen" rejimida kerak emas.
# Shuning uchun bu yerda emas, pastda shu kutubxonalar
# ishlatiladigan funksiyalar ichida import qilinadi — shunda
# "listen" rejimi ularni o'rnatish shart bo'lmasdan ham ishlay oladi.
# ============================================================

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
OWNER_ID = os.environ.get("OWNER_ID")  # faqat shu Telegram ID'ga ega odamga bot javob beradi

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "uz,ru;q=0.9,en;q=0.8",
}

OFFSET_FILE = "offset.txt"


def wait_until_exact(hour, minute=0):
    """Aniq HH:MM:00 (Toshkent vaqti) gacha kutadi.
    GitHub Actions cron'ni bir necha daqiqa (ba'zan undan ko'proq ham)
    oldinroq ishga tushirsak, runner tayyor turadi va shu funksiya orqali
    aniq soniyagacha kutadi.

    MUHIM: bu funksiya HECH QACHON "ertangi kunni" kutmaydi. Agar GitHub
    ishni juda kech boshlagan bo'lsa (hatto necha soat kech bo'lsa ham),
    shunchaki DARHOL yuboradi — chunki ertangi kun uchun alohida cron
    allaqachon bor, shu yerda ikki marta kutish shart emas va navbatdagi
    ishni behuda soatlab "uxlatib qo'yish" xato edi."""
    now = datetime.datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if target <= now:
        kechikish = (now - target).total_seconds()
        print(f"⚠️ Ish {int(kechikish)} soniya kechikib boshlandi — kutmasdan darhol yuboriladi.")
        return

    wait_seconds = (target - now).total_seconds()
    print(f"⏳ Aniq {hour:02d}:{minute:02d}:00 gacha {int(wait_seconds)} soniya kutilmoqda...")
    time.sleep(wait_seconds)
    print(f"🚀 Vaqt keldi: {datetime.datetime.now().strftime('%H:%M:%S')} — yuborishni boshlaymiz.")


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
    from bs4 import BeautifulSoup  # faqat shu funksiya chaqirilganda kerak

    url = "https://bank.uz/uz/currency"

    # tarmoq vaqtincha kechiksa, 3 martagacha qayta urinib ko'ramiz
    resp = None
    for urinish in range(1, 4):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            print(f"⚠️ bank.uz'ga so'rov {urinish}-marta muvaffaqiyatsiz: {e}")
            if urinish < 3:
                time.sleep(5 * urinish)  # 5s, keyin 10s kutib qayta urinadi
            else:
                raise

    soup = BeautifulSoup(resp.text, "html.parser")

    container = soup.find(id="best_USD") or soup
    html = str(container)

    # ">Sotish<" — orasida bo'sh joy/yangi qator bo'lishi mumkin, shuning uchun
    # oddiy .find() emas, whitespace'ga chidamli regex ishlatamiz.
    match = re.search(r">\s*Sotish\s*<", html)

    if match is None:
        # muqobil urinish: BeautifulSoup orqali matni aynan "Sotish" bo'lgan
        # (boshqa so'z ichida emas, mustaqil) tegni qidiramiz.
        sotish_tag = None
        for tag in container.find_all(True):
            if tag.get_text(strip=True) == "Sotish" and len(tag.find_all(True)) == 0:
                sotish_tag = tag
                break
        if sotish_tag is None:
            raise ValueError(
                f"bank.uz sahifa tuzilishi o'zgargan bo'lishi mumkin "
                f"(javob uzunligi={len(resp.text)}, status={resp.status_code})"
            )
        split_idx = html.find(str(sotish_tag))
    else:
        split_idx = match.start()

    buy_html, sell_html = html[:split_idx], html[split_idx:]

    def extract_bank_value(a_tag, full_html):
        """Bitta bank narxini TOPISH UCHUN 3 TA USUL bilan urinadi.
        1-usul ishlamasa 2-usulni, u ham ishlamasa 3-usulni sinaydi.
        Uchalasi ham muvaffaqiyatsiz bo'lsagina None qaytaradi (bank o'tkazib yuboriladi)."""

        # 1-urinish: elementdan keyingi eng yaqin "so'm" so'zini qidirish
        try:
            price_node = a_tag.find_next(string=re.compile(r"so'm"))
            val = tozalash(price_node)
            if val > 0:
                return val
        except Exception:
            pass

        # 2-urinish: ota (parent) elementning ichidagi butun matndan raqam qidirish
        try:
            parent = a_tag.find_parent()
            if parent:
                matn = parent.get_text(" ", strip=True)
                m = re.search(r"([\d\s]{3,})\s*so'm", matn)
                if m:
                    val = tozalash(m.group(1))
                    if val > 0:
                        return val
        except Exception:
            pass

        # 3-urinish: xom HTML ichida link joylashgan joydan keyingi matndan qidirish
        try:
            idx = full_html.find(str(a_tag))
            if idx != -1:
                keyingi_qism = full_html[idx: idx + 400]
                m = re.search(r"([\d\s]{3,})\s*so'm", keyingi_qism)
                if m:
                    val = tozalash(m.group(1))
                    if val > 0:
                        return val
        except Exception:
            pass

        return None

    def extract(piece_html):
        piece_soup = BeautifulSoup(piece_html, "html.parser")
        out = {}
        for a in piece_soup.find_all("a", href=re.compile(r"/currency/bank/")):
            name = a.get_text(strip=True)
            if not name:
                continue

            val = extract_bank_value(a, piece_html)
            if val is None:
                print(f"⚠️ '{name}': 3 usul bilan ham narx topilmadi, o'tkazib yuborildi.")
                continue

            href = a.get("href", "")
            full_url = "https://bank.uz" + href if href.startswith("/") else href
            if name not in out:
                out[name] = {"val": val, "url": full_url}
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
    # faqat shu funksiya chaqirilganda kerak (send rejimida)
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

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
# YORDAMCHI FUNKSIYALAR: egasiga xabar, oldingi kursni eslab qolish, MB kursi
# ============================================================
LAST_RATES_FILE = "last_rates.json"


def notify_owner(text):
    """Xatolik bo'lsa egasiga (OWNER_ID) shaxsiy xabar yuboradi.
    Egasi botga kamida bir marta /start bosgan bo'lishi kerak."""
    if not BOT_TOKEN or not OWNER_ID:
        print("ℹ️ OWNER_ID yo'q, egasiga xabar yuborilmadi.")
        return
    try:
        tg_send(OWNER_ID, text, parse_mode=None)
    except Exception as e:
        print(f"⚠️ Egasiga xabar yuborib bo'lmadi: {e}")


def load_last_rates():
    try:
        with open(LAST_RATES_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def save_last_rates(best_buy, best_sell):
    with open(LAST_RATES_FILE, "w") as f:
        json.dump({"best_buy": best_buy, "best_sell": best_sell,
                   "time": time.strftime('%d.%m.%Y %H:%M')}, f)


def farq_belgisi(yangi, eski):
    """Oldingi yuborilgan kursga nisbatan o'zgarish: ▲ +40 yoki ▼ -20."""
    if eski is None:
        return ""
    farq = yangi - eski
    if farq > 0:
        return f" (▲ +{farq})"
    if farq < 0:
        return f" (▼ {farq})"
    return " (➖ 0)"


def get_cbu_usd_rate():
    """Markaziy bankning rasmiy USD kursi. Olinmasa None qaytaradi (xabar shundoq ham yuboriladi)."""
    try:
        resp = requests.get("https://cbu.uz/oz/arkhiv-kursov-valyut/json/USD/",
                            headers=HEADERS, timeout=20)
        resp.raise_for_status()
        rate = float(resp.json()[0]["Rate"])
        return f"{rate:,.2f}".replace(",", " ")
    except Exception as e:
        print(f"⚠️ MB kursini olishda xatolik: {e}")
        return None


# ============================================================
# REJIM 1: "send" — kurslarni kanalga yuborish
# (GitHub Actions'da 09:00, 13:00, 19:00 da cron orqali chaqiriladi)
# ============================================================
def run_send(target_hour=None):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN yoki CHAT_ID muhit o'zgaruvchisi topilmadi.")
        return

    # agar aniq soat berilgan bo'lsa (masalan 9, 13, 19) —
    # shu soatning aniq 00-soniyasigacha kutib turamiz, keyin yuboramiz.
    if target_hour is not None:
        wait_until_exact(int(target_hour))

    print("💱 bank.uz orqali barcha banklar kursi olinmoqda...")
    try:
        banks, skipped = get_all_bank_rates()
    except Exception as e:
        print(f"❌ bank.uz'dan ma'lumot olishda xatolik: {e}")
        notify_owner(f"⚠️ Kurs kanalga yuborilmadi.\nSabab: bank.uz'dan ma'lumot olib bo'lmadi.\n{e}")
        return

    print(f"✅ {len(banks)} ta bank topildi.")
    if skipped:
        print(f"⚠️ O'tkazib yuborildi ({len(skipped)} ta): {', '.join(skipped)}")

    if len(banks) < 5:
        print("❌ Juda kam bank topildi, ehtimol sayt tuzilishi o'zgargan. Xabar yuborilmadi.")
        notify_owner(f"⚠️ Kurs kanalga yuborilmadi.\nSabab: faqat {len(banks)} ta bank topildi (sayt tuzilishi o'zgargan bo'lishi mumkin).")
        return

    print("🥇 Oltin narxi olinmoqda...")
    from webdriver_manager.chrome import ChromeDriverManager  # faqat shu yerda kerak
    path = ChromeDriverManager().install()
    gold_values = get_gold_prices(path)
    if not gold_values:
        notify_owner("⚠️ Oltin narxi olinmadi (cbu.uz XPath o'zgargan bo'lishi mumkin). Xabar oltin narxisiz yuborildi.")

    mb_kursi = get_cbu_usd_rate()

    ey_x_val = max(r["buy_num"] for r in banks)
    ey_s_val = min(r["sell_num"] for r in banks)
    ey_x = f"{ey_x_val:,}".replace(",", " ")
    ey_s = f"{ey_s_val:,}".replace(",", " ")
    vaqt = time.strftime('%d.%m.%Y %H:%M')

    # oldingi yuborilgan kursga nisbatan o'zgarish
    oldingi = load_last_rates()
    xarid_farq = farq_belgisi(ey_x_val, oldingi.get("best_buy"))
    sotuv_farq = farq_belgisi(ey_s_val, oldingi.get("best_sell"))

    # eng yaxshi narx(lar)ni beruvchi bank nomlari (bir nechta bank teng bo'lishi mumkin)
    eng_yahshi_xarid_banklar = ", ".join(sorted({r["name"] for r in banks if r["buy_num"] == ey_x_val}))
    eng_yahshi_sotuv_banklar = ", ".join(sorted({r["name"] for r in banks if r["sell_num"] == ey_s_val}))

    xabar = f"<b>🏦 KUNLIK VALYUTA NARXLARI ($)</b>\n"
    if mb_kursi:
        xabar += f"🏛 <b>Markaziy bank kursi:</b> {mb_kursi} so'm\n"
    xabar += f"— — — — — — — — — — — — — — —\n"
    xabar += f"🏛 Bank nomi | Xarid | Sotuv \n— — — — — — — — — — — — — — —\n"
    for r in banks:
        buy_str = f"{r['buy_num']:,}".replace(",", " ")
        sell_str = f"{r['sell_num']:,}".replace(",", " ")
        # eng yuqori xarid yoki eng past sotuv narxini beradigan bank(lar) — ⭐ bilan ajralib turadi
        icon = "⭐" if (r["buy_num"] == ey_x_val or r["sell_num"] == ey_s_val) else "🔹"
        xabar += f"{icon} <a href='{r['url']}'>{r['name']}</a> | {buy_str} | {sell_str}\n"
    xabar += f"— — — — — — — — — — — — — — —\n"
    xabar += (f"<blockquote>⭐ Eng yaxshi xarid: {ey_x} so'm{xarid_farq} — {eng_yahshi_xarid_banklar}\n"
              f"⭐ Eng yaxshi sotuv: {ey_s} so'm{sotuv_farq} — {eng_yahshi_sotuv_banklar}</blockquote>\n")

    if gold_values:
        # cbu.uz'dan kelgan matnni tozalab, valyuta jadvali kabi "9 000 000" formatiga solamiz
        gramlar = ["5 gramm", "10 gramm", "20 gramm", "50 gramm", "100 gramm"]
        xabar += f"\n<b>💰 Quyma oltin narxlari:</b>\n"
        for gram_nomi, xom_qiymat in zip(gramlar, gold_values):
            son = tozalash(xom_qiymat)
            formatlangan = f"{son:,}".replace(",", " ") if son else xom_qiymat
            xabar += f"🟡 {gram_nomi}: {formatlangan} so'm\n"

    if skipped:
        xabar += f"\n<i>⚠️ Ushbu banklar o'tkazib yuborildi: {', '.join(skipped)}</i>\n"

    xabar += f"\n🕒 <b>Yangilandi:</b> {vaqt}\n📢 @dollorkurslariUZ"

    print("📤 Telegramga yuborilmoqda...")
    resp = tg_send(CHAT_ID, xabar)
    if resp.status_code != 200:
        notify_owner(f"⚠️ Kurs kanalga yuborilmadi.\nSabab: Telegram xatosi: {resp.text}")
        return

    # faqat muvaffaqiyatli yuborilgandan keyin keyingi safar solishtirish uchun eslab qolamiz
    save_last_rates(ey_x_val, ey_s_val)
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

        # /start bosilganda — FAQAT egasi (OWNER_ID) uchun javob beradi
        msg = u.get("message")
        if msg and msg.get("text", "").startswith("/start"):
            user_id = str(msg["from"]["id"])
            chat_id = msg["chat"]["id"]

            if OWNER_ID and user_id != str(OWNER_ID):
                print(f"⛔ Begona foydalanuvchi /start bosdi (id={user_id}) — e'tiborsiz qoldirildi.")
                continue

            matn = (
                "👋 Salom!\n\n"
                "Men O'zbekiston banklaridagi dollar kurslari va quyma oltin "
                "narxlarini kuzataman.\n\n"
                "📌 Meni kanalingizga <b>admin</b> qilib qo'shing — har kuni soat "
                "09:00, 13:00 va 19:00 da yangilangan narxlarni avtomatik yuborib turaman."
            )
            tg_send(chat_id, matn)
            print(f"✅ /start javobi yuborildi: {chat_id}")

        # kanalga admin qilib qo'shilganda — FAQAT egasi qo'shgan bo'lsa xabar beradi
        cm = u.get("my_chat_member")
        if cm:
            chat = cm["chat"]
            new_status = cm["new_chat_member"]["status"]
            actor_id = str(cm["from"]["id"])

            if OWNER_ID and actor_id != str(OWNER_ID):
                print(f"⛔ Begona odam botni admin qildi (id={actor_id}) — e'tiborsiz qoldirildi.")
                continue

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
        # python main.py send        -> darhol yuboradi (qo'lda test uchun)
        # python main.py send 9      -> aniq 09:00:00 gacha kutib, keyin yuboradi
        hour_arg = sys.argv[2] if len(sys.argv) > 2 else None
        run_send(target_hour=hour_arg)
    elif mode == "listen":
        run_listen()
    else:
        print(f"❌ Noma'lum rejim: {mode}. 'send' yoki 'listen' dan birini bering.")
