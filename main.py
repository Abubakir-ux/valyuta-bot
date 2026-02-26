import requests
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- KONFIGURATSIYA ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8592762047:AAGyO5OxRoBi1nZzcN0jXz9IeeVrtgl4Q6c")
CHAT_ID = os.environ.get("CHAT_ID", "-1003805780800")
DATA_FILE = "users.json"

def tozalash(matn):
    if not matn or matn.strip() == "": return 0
    toza_son = "".join(filter(str.isdigit, matn))
    return int(toza_son) if toza_son else 0

def yuklash_eski_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def saqlash_yangi_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def get_s(yangi, kalit, eski_data):
    eski = tozalash(eski_data.get(kalit, "0"))
    y = tozalash(yangi)
    if eski == 0: return ""
    if y > eski: return "🔺" # Ko'tarildi
    if y < eski: return "🔻" # Tushdi
    return "➖"

def run_bot():
    eski_data = yuklash_eski_data()
    print("Bot ishga tushdi...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 60)

    try:
        # 1. Ipak Yo'li
        driver.get("https://ipakyulibank.uz/physical")
        time.sleep(12)
        iy_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="124"]/div[2]/div/div[2]/table/tbody/tr[1]/td[2]'))).text
        iy_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="124"]/div[2]/div/div[2]/table/tbody/tr[1]/td[3]'))).text

        # 2. Turon Bank
        driver.get("https://turonbank.uz/uz/")
        time.sleep(15)
        tb_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="js-main-page"]/div[1]/div/div/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[2]/div/span'))).text
        tb_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="js-main-page"]/div[1]/div/div/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[3]/div/span'))).text

        # 3. Hamkor Bank
        driver.get("https://hamkorbank.uz/uz/exchange-rate/")
        time.sleep(12)
        hm_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="block_mAWMGK"]/div/div[4]/div[2]/div[2]/div[2]'))).text
        hm_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="block_mAWMGK"]/div/div[4]/div[2]/div[3]/div[2]'))).text

        # 4. NBU
        driver.get("https://nbu.uz/jismoniy-shaxslar-valyutalar-kursi")
        time.sleep(10)
        nb_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="02"]/div/div/div/div[1]/div[2]/div[2]/div[2]/div'))).text
        nb_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="w-node-b74b34b0-2973-298a-2b6d-79ba92bf482f-92bf4808"]/div'))).text

        # 5. Aloqa Bank
        driver.get("https://aloqabank.uz/ru/services/exchange-rates/")
        time.sleep(15)
        al_x = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[5]/div/div[2]/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[2]/div/span'))).text
        al_s = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[5]/div/div[2]/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[3]/div/span'))).text

        # 6. Xalq Bank
        driver.get("https://xb.uz/page/valyuta-ayirboshlash")
        time.sleep(12)
        xq_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/div[3]/div/div/p'))).text
        xq_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/p'))).text

        # 7. Trust Bank
        driver.get("https://trustbank.uz/uz/")
        time.sleep(15)
        tr_x = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/section[2]/div/div/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[2]/td[2]/div/span'))).text
        tr_s = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/section[2]/div/div/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[2]/td[3]/div/span'))).text

        # 8. MK Bank
        driver.get("https://mkbank.uz/uz/")
        time.sleep(12)
        mb_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="top"]/div[2]/div[1]/header[2]/div/div/noindex[1]/div/div[1]/div[2]/div[1]/div[2]/div[1]'))).text
        mb_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="top"]/div[2]/div[1]/header[2]/div/div/noindex[1]/div/div[1]/div[2]/div[2]/div[2]/div[1]'))).text

        # 9. Ipoteka Bank
        driver.get("https://www.ipotekabank.uz/ru/private/services/currency/")
        time.sleep(15)
        ip_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="all"]/div/table/tbody/tr[1]/td[2]'))).text
        ip_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="all"]/div/table/tbody/tr[1]/td[3]'))).text

        # 10. Octo Bank
        driver.get("https://octobank.uz/uz")
        time.sleep(12)
        oc_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="w-node-_23a24b74-a88d-5f36-44f5-45399e0decee-9e0dece1"]/div[2]/div/div[1]/p'))).text
        oc_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="w-node-_23a24b74-a88d-5f36-44f5-45399e0decee-9e0dece1"]/div[2]/div/div[2]/p'))).text

        # Oltin narxlari
        driver.get("https://cbu.uz/oz/banknotes-coins/gold-bars/prices/")
        time.sleep(15)
        g5 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[3]/td[2]/p'))).text
        g10 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[4]/td[2]/p'))).text
        g20 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[5]/td[2]/p'))).text
        g50 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[6]/td[2]/p'))).text
        g100 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[7]/td[2]/p'))).text

        # Strelkalarni hisoblash (Sotuv bo'yicha)
        s_iy = get_s(iy_s, "iy", eski_data)
        s_tb = get_s(tb_s, "tb", eski_data)
        s_hm = get_s(hm_s, "hm", eski_data)
        s_nb = get_s(nb_s, "nb", eski_data)
        s_al = get_s(al_s, "al", eski_data)
        s_xq = get_s(xq_s, "xq", eski_data)
        s_tr = get_s(tr_s, "tr", eski_data)
        s_mb = get_s(mb_s, "mb", eski_data)
        s_ip = get_s(ip_s, "ip", eski_data)
        s_oc = get_s(oc_s, "oc", eski_data)

        # Eng yaxshi narxlar
        x_list = [tozalash(iy_x), tozalash(tb_x), tozalash(hm_x), tozalash(nb_x), tozalash(al_x), tozalash(xq_x), tozalash(tr_x), tozalash(mb_x), tozalash(ip_x), tozalash(oc_x)]
        s_list = [tozalash(iy_s), tozalash(tb_s), tozalash(hm_s), tozalash(nb_s), tozalash(al_s), tozalash(xq_s), tozalash(tr_s), tozalash(mb_s), tozalash(ip_s), tozalash(oc_s)]
        x_filtr = [i for i in x_list if i > 10000]
        s_filtr = [i for i in s_list if i > 10000]
        eyx = f"{max(x_filtr):,}".replace(",", " ") if x_filtr else "0"
        eys = f"{min(s_filtr):,}".replace(",", " ") if s_filtr else "0"

        vaqt = time.strftime('%d.%m.%Y %H:%M')
        xabar = (
            f"<b>🏦 KUNLIK VALYUTA NARXLARI ($)</b>\n"
            f"— — — — — — — — — — — — — — —\n"
            f"🏛 Bank nomi          |  Xarid  |  Sotuv \n"
            f"— — — — — — — — — — — — — — —\n"
            f"🏙 <a href='https://ipakyulibank.uz/physical'>Ipak Yo'li      </a> | {iy_x.strip():<5} | {iy_s.strip()} {s_iy}\n"
            f"🏙 <a href='https://turonbank.uz/uz/'>Turon Bank   </a> | {tb_x.strip():<5} | {tb_s.strip()} {s_tb}\n"
            f"🏙 <a href='https://hamkorbank.uz/uz/'>Hamkor Bank  </a> | {hm_x.strip():<5} | {hm_s.strip()} {s_hm}\n"
            f"🏙 <a href='https://nbu.uz/'>NBU Bank       </a> | {nb_x.strip():<5} | {nb_s.strip()} {s_nb}\n"
            f"🏙 <a href='https://aloqabank.uz/ru/services/exchange-rates/'>Aloqa Bank     </a> | {al_x.strip():<5} | {al_s.strip()} {s_al}\n"
            f"🏙 <a href='https://xb.uz/'>Xalq Bank      </a> | {xq_x.strip():<5} | {xq_s.strip()} {s_xq}\n"
            f"🏙 <a href='https://trustbank.uz/uz/'>Trast Bank     </a> | {tr_x.strip():<5} | {tr_s.strip()} {s_tr}\n"
            f"🏙 <a href='https://mkbank.uz/uz/'>Mikro Bank     </a> | {mb_x.strip():<5} | {mb_s.strip()} {s_mb}\n"
            f"🏙 <a href='https://www.ipotekabank.uz/ru/private/services/currency/'>Ipoteka Bank   </a> | {ip_x.strip():<5} | {ip_s.strip()} {s_ip}\n"
            f"🏙 <a href='https://octobank.uz/uz'>Octo Bank      </a> | {oc_x.strip():<5} | {oc_s.strip()} {s_oc}\n"
            f"— — — — — — — — — — — — — — —\n"
            f"<blockquote>Eng yaxshi narx: | {eyx} | {eys} 📈</blockquote>\n"
            f"<b>💰 Quyma oltin:</b>\n"
            f"🟡 5 грамм:  {quyma_oltin_5g}\n"
            f"🟡 10 грамм:  {quyma_oltin_10g}\n"
            f"🟡 20 грамм:  {quyma_oltin_20g}\n"
            f"🟡 50 грамм:  {quyma_oltin_50g}\n"
            f"🟡 100 грамм: {quyma_oltin_100g}\n"
            f"🕒 <b>Yangilandi:</b> {vaqt}\n"
            f"📢 @dollorkurslariUZ"
        )

        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                     data={"chat_id": CHAT_ID, "text": xabar, "parse_mode": "HTML", "disable_web_page_preview": True})

        # Kelgusi safar uchun saqlash
        yangi_data = {"iy": iy_s, "tb": tb_s, "hm": hm_s, "nb": nb_s, "al": al_s, "xq": xq_s, "tr": tr_s, "mb": mb_s, "ip": ip_s, "oc": oc_s}
        saqlash_yangi_data(yangi_data)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    run_bot()
