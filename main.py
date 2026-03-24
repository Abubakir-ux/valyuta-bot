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

BOT_TOKEN = os.getenv("BOT_TOKEN", "8711798125:AAGXq6hFwcWKYjU8ZhMHGySojqyLYR4wWo0")
CHAT_ID = os.getenv("CHAT_ID", "-1003805780800")

def tozalash(matn):
    """Xatolikka chidamli tozalash funksiyasi"""
    if not matn or matn.strip() == "":
        return 0
    toza_son = "".join(filter(str.isdigit, matn))
    return int(toza_son) if toza_son else 0  

chrome_options = Options()
chrome_options.add_argument("--headless=new") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.set_page_load_timeout(180)
wait = WebDriverWait(driver, 20)

try:
    print("Ma'lumotlar yig'ilmoqda...")

    driver.get("https://ipakyulibank.uz/physical")
    time.sleep(15)
    iy_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="124"]/div[2]/div/div[2]/table/tbody/tr[1]/td[2]'))).text
    iy_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="124"]/div[2]/div/div[2]/table/tbody/tr[1]/td[3]'))).text

    driver.get("https://ziraatbank.uz/uz")
    time.sleep(15)
    as_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="currency-list"]/ul/li[1]/div/div[1]/span'))).text
    as_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="currency-list"]/ul/li[1]/div/div[2]/span'))).text

    driver.get("https://turonbank.uz/uz/")
    time.sleep(15)
    tb_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="js-main-page"]/div[1]/div/div/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[2]/div/span'))).text
    tb_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="js-main-page"]/div[1]/div/div/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[3]/div/span'))).text

    driver.get("https://hamkorbank.uz/uz/exchange-rate/")
    time.sleep(15) 
    hm_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="block_mAWMGK"]/div/div[4]/div[2]/div[2]/div[2]'))).text
    hm_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="block_mAWMGK"]/div/div[4]/div[2]/div[3]/div[2]'))).text

    driver.get("https://nbu.uz/jismoniy-shaxslar-valyutalar-kursi")
    time.sleep(15)
    nb_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="02"]/div/div/div/div[1]/div[2]/div[1]/div[2]/div'))).text
    nb_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="02"]/div/div/div/div[1]/div[2]/div[1]/div[3]/div'))).text

    driver.get("https://aloqabank.uz/ru/services/exchange-rates/")
    time.sleep(15)
    al_x = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[5]/div/div[2]/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[2]/div/span'))).text
    al_s = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[5]/div/div[2]/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[3]/div/span'))).text

    driver.get("https://xb.uz/page/valyuta-ayirboshlash")
    time.sleep(15)
    xq_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/div[3]/div/div/p'))).text
    xq_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/p'))).text

    driver.get("https://trustbank.uz/uz/")
    time.sleep(15)
    tr_x = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/section[2]/div/div/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[2]/td[2]/div/span'))).text
    tr_s = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/section[2]/div/div/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[2]/td[3]/div/span'))).text

    driver.get("https://www.ipotekabank.uz/ru/private/services/currency/")
    time.sleep(15)
    ip_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="all"]/div/table/tbody/tr[1]/td[2]'))).text
    ip_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="all"]/div/table/tbody/tr[1]/td[3]'))).text

    driver.get("https://octobank.uz/uz")
    time.sleep(15)
    oc_x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="w-node-_23a24b74-a88d-5f36-44f5-45399e0decee-9e0dece1"]/div[2]/div/div[1]/p'))).text
    oc_s = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="w-node-_23a24b74-a88d-5f36-44f5-45399e0decee-9e0dece1"]/div[2]/div/div[2]/p'))).text

    driver.get("https://cbu.uz/oz/banknotes-coins/gold-bars/prices/")
    time.sleep(15)
    oltin_5 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[3]/td[2]/p'))).text
    oltin_10 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[4]/td[2]/p'))).text
    oltin_20 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[5]/td[2]/p'))).text
    oltin_50 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[6]/td[2]/p'))).text
    oltin_100 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/section[1]/div/div/div[1]/table/tbody/tr[7]/td[2]/p'))).text

    x_list = [tozalash(iy_x), tozalash(zr_x), tozalash(tb_x), tozalash(hm_x), tozalash(nb_x), tozalash(al_x), tozalash(xq_x), tozalash(tr_x), tozalash(ip_x), tozalash(oc_x)]
    s_list = [tozalash(iy_s), tozalash(zr_s), tozalash(tb_s), tozalash(hm_s), tozalash(nb_s), tozalash(al_s), tozalash(xq_s), tozalash(tr_s), tozalash(ip_s), tozalash(oc_s)]
    x_filtrlangan = [i for i in x_list if i > 10000]
    s_filtrlangan = [i for i in s_list if i > 10000]

    ey_x = f"{max(x_filtrlangan):,}".replace(",", " ") if x_filtrlangan else "0"
    ey_s = f"{min(s_filtrlangan):,}".replace(",", " ") if s_filtrlangan else "0"
                    
    vaqt = time.strftime('%d.%m.%Y %H:%M')
    
    xabar = (
       f"<b>🏦 KUNLIK VALYUTA NARXLARI ($)</b>\n"
        f"— — — — — — — — — — — — — — —\n"
        f"🏛 Bank nomi          |  Xarid  |  Sotuv \n"
        f"— — — — — — — — — — — — — — —\n"
        f"🏙 <a href='https://ipakyulibank.uz/physical'>Ipak Yo'li      </a>       | {iy_x.strip():<5} | {iy_s.strip()}\n"
        f"🏙 <a href='https://ziraatbank.uz/uz'>Ziraat bank</a>    | {zr_x.strip():<5} | {zr_s.strip()}\n"
        f"🏙 <a href='https://turonbank.uz/uz/'>Turon Bank   </a>     | {tb_x.strip():<5} | {tb_s.strip()}\n"
        f"🏙 <a href='https://hamkorbank.uz/uz/'>Hamkor Bank   </a> | {hm_x.strip():<5} | {hm_s.strip()}\n"
        f"🏙 <a href='https://nbu.uz/'>NBU Bank          </a> | {nb_x.strip():<5} | {nb_s.strip()}\n"
        f"🏙 <a href='https://aloqabank.uz/ru/services/exchange-rates/'>Aloqa Bank        </a> | {al_x.strip():<5} | {al_s.strip()}\n"
        f"🏙 <a href='https://xb.uz/'>Xalq Bank       </a>     | {xq_x.strip():<5} | {xq_s.strip()}\n"
        f"🏙 <a href='https://trustbank.uz/uz/'>Trast Bank        </a>   | {tr_x.strip():<5} | {tr_s.strip()}\n"
        f"🏙 <a href='https://www.ipotekabank.uz/ru/private/services/currency/'>Ipoteka Bank    </a> | {ip_x.strip():<5} | {ip_s.strip()}\n"
        f"🏙 <a href='https://octobank.uz/uz'>Octo Bank      </a>     | {oc_x.strip():<5} | {oc_s.strip()}\n"
        f"— — — — — — — — — — — — — — —\n"
        f"<blockquote>Eng yaxshi narx: | {ey_x} | {ey_s} 📈</blockquote>\n"
        f"<b>💰 Quyma oltin narxlari:</b>\n"
        f"🟡 5 грамм:  {oltin_5}\n"
        f"🟡 10 грамм:  {oltin_10}\n"
        f"🟡 20 грамм:  {oltin_20}\n"
        f"🟡 50 грамм:  {oltin_50}\n"
        f"🟡 100 грамм: {oltin_100}\n"
        f"🕒 <b>Yangilandi:</b> {vaqt}\n\n"
        f" Bu ma'lumotlar Bankarning rasmiy saytlaridan olingan ! \n"
        f"📢 @dollorkurslariUZ — tezkor va aniq"
    )

    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  data={
                  "chat_id": CHAT_ID, 
                  "text": xabar,
                  "parse_mode": "HTML",
                  "disable_web_page_preview": True})
    print("✅ Bajarildi!")

except Exception as e:
    import traceback
    print(f"❌ Xatolik yuz berdi: {e}")
    print("--- To'liq xatolik izi (Stacktrace) ---")
    traceback.print_exc()
finally:
    driver.quit()
