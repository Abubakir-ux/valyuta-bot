import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- SOZLAMALAR (GitHub Secrets orqali olinadi) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8592762047:AAGyO5OxRoBi1nZzcN0jXz9IeeVrtgl4Q6c")
CHAT_ID = os.getenv("CHAT_ID", "-1003805780800")

def tozalash(matn):
    """Xatolikka chidamli tozalash funksiyasi"""
    if not matn or matn.strip() == "":
        return 0
    toza_son = "".join(filter(str.isdigit, matn))
    return int(toza_son) if toza_son else 0  

# --- BRAUZERNI SOZLASH ---
chrome_options = Options()
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 45)

try:
    print("Ma'lumotlar yig'ilmoqda...")

    # 1. Ipak Yo'li
    driver.get("https://ipakyulibank.uz/physical")
    time.sleep(5)
    iy_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="124"]/div[2]/div/div[2]/table/tbody/tr[1]/td[2]'))).text
    iy_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="124"]/div[2]/div/div[2]/table/tbody/tr[1]/td[3]'))).text

    # 2. Turon bank
    driver.get("https://turonbank.uz/uz/")
    time.sleep(5)
    tb_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="js-main-page"]/div[1]/div/div/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[2]/div/span'))).text
    tb_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="js-main-page"]/div[1]/div/div/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[3]/div/span'))).text

    # 3. Hamkor bank
    driver.get("https://hamkorbank.uz/uz/exchange-rate/")
    time.sleep(5) 
    hm_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="block_mAWMGK"]/div/div[4]/div[2]/div[2]/div[2]'))).text
    hm_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="block_mAWMGK"]/div/div[4]/div[2]/div[3]/div[2]'))).text

    # 4. NBU bank
    driver.get("https://nbu.uz/jismoniy-shaxslar-valyutalar-kursi")
    time.sleep(5)
    nb_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="02"]/div/div/div/div[1]/div[2]/div[2]/div[2]/div'))).text
    nb_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="w-node-b74b34b0-2973-298a-2b6d-79ba92bf482f-92bf4808"]/div'))).text

    # 5. Aloqa bank
    driver.get("https://aloqabank.uz/ru/services/exchange-rates/")
    time.sleep(5)
    al_x = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[5]/div/div[2]/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[2]/div/span'))).text
    al_s = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[5]/div/div[2]/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[3]/div/span'))).text

    # 6. Xalq bank
    driver.get("https://xb.uz/page/valyuta-ayirboshlash")
    time.sleep(5)
    xq_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/div[3]/div/div/p'))).text
    xq_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/p'))).text

    # 7. Trast bank
    driver.get("https://trustbank.uz/uz/")
    time.sleep(5)
    tr_x = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/section[2]/div/div/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[2]/td[2]/div/span'))).text
    tr_s = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/section[2]/div/div/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[2]/td[3]/div/span'))).text

    # 8. Mikro bank
    driver.get("https://mkbank.uz/uz/")
    time.sleep(5)
    mb_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="top"]/div[2]/div[1]/header[2]/div/div/noindex[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]'))).text
    mb_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="top"]/div[2]/div[1]/header[2]/div/div/noindex[1]/div/div[1]/div[2]/div[2]/div[2]/div[1]'))).text

    # 9. Ipoteka bank
    driver.get("https://www.ipotekabank.uz/ru/private/services/currency/")
    time.sleep(5)
    ip_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="all"]/div/table/tbody/tr[1]/td[2]'))).text
    ip_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="all"]/div/table/tbody/tr[1]/td[3]'))).text

    # 10. Octo bank
    driver.get("https://octobank.uz/uz")
    time.sleep(5)
    oc_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="w-node-_23a24b74-a88d-5f36-44f5-45399e0decee-9e0dece1"]/div[2]/div/div[1]/p'))).text
    oc_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="w-node-_23a24b74-a88d-5f36-44f5-45399e0decee-9e0dece1"]/div[2]/div/div[2]/p'))).text

    # 11. Oltin
    driver.get("https://cbu.uz/oz/banknotes-coins/gold-bars/prices/")
    time.sleep(5)
    oltin_5 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[3]/td[2]/p'))).text
    oltin_10 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[4]/td[2]/p'))).text
    oltin_20 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[5]/td[2]/p'))).text
    oltin_50 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[6]/td[2]/p'))).text
    oltin_100 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[7]/td[2]/p'))).text

    # --- HISOBLASH ---
    x_list = [tozalash(iy_x), tozalash(tb_x), tozalash(hm_x), tozalash(nb_x), tozalash(al_x), tozalash(xq_x), tozalash(tr_x), tozalash(mb_x), tozalash(ip_x), tozalash(oc_x)]
    s_list = [tozalash(iy_s), tozalash(tb_s), tozalash(hm_s), tozalash(nb_s), tozalash(al_s), tozalash(xq_s), tozalash(tr_s), tozalash(mb_s), tozalash(ip_s), tozalash(oc_s)]

    x_filtrlangan = [i for i in x_list if i > 10000]
    s_filtrlangan = [i for i in s_list if i > 10000]

    ey_x = f"{max(x_filtrlangan):,}".replace(",", " ") if x_filtrlangan else "0"
    ey_s = f"{min(s_filtrlangan):,}".replace(",", " ") if s_filtrlangan else "0"

    # --- XABAR ---
    vaqt = time.strftime('%d.%m.%Y %H:%M')
    xabar = (
        f"<b>🏦 KUNLIK VALYUTA NARXLARI ($)</b>\n"
        f"— — — — — — — — — — — — — — —\n"
        f"🏛 Bank nomi          |  Xarid  |  Sotuv \n"
        f"— — — — — — — — — — — — — — —\n"
        f"🏙 Ipak Yo'li        | {iy_x.strip():<5} | {iy_s.strip()}\n"
        f"🏙 Turon Bank        | {tb_x.strip():<5} | {tb_s.strip()}\n"
        f"🏙 Hamkor Bank       | {hm_x.strip():<5} | {hm_s.strip()}\n"
        f"🏙 NBU Bank          | {nb_x.strip():<5} | {nb_s.strip()}\n"
        f"🏙 Aloqa Bank        | {al_x.strip():<5} | {al_s.strip()}\n"
        f"🏙 Xalq Bank         | {xq_x.strip():<5} | {xq_s.strip()}\n"
        f"🏙 Trast Bank        | {tr_x.strip():<5} | {tr_s.strip()}\n"
        f"🏙 Mikro Bank        | {mb_x.strip():<5} | {mb_s.strip()}\n"
        f"🏙 Ipoteka Bank      | {ip_x.strip():<5} | {ip_s.strip()}\n"
        f"🏙 Octo Bank         | {oc_x.strip():<5} | {oc_s.strip()}\n"
        f"— — — — — — — — — — — — — — —\n"
        f"<blockquote>Eng yaxshi narx: | {ey_x} | {ey_s} 📈</blockquote>\n"
        f"<b>💰 Quyma oltin:</b>\n"
        f"🟡 5g: {oltin_5} | 10g: {oltin_10}\n"
        f"🟡 20g: {oltin_20} | 50g: {oltin_50}\n"
        f"🟡 100g: {oltin_100}\n"
        f"🕒 <b>Yangilandi:</b> {vaqt}\n\n"
        f"📢 @dollorkurslariUZ"
    )

    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": xabar, "parse_mode": "HTML"})
    print("✅ Bajarildi!")

except Exception as e:
    print(f"❌ Xato: {e}")
finally:
    driver.quit()
