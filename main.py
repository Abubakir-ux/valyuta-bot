import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime

# Load configuration from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

telegram_token = config['telegram_token']
chat_id = config['chat_id']

# Function to scrape exchange rates
def scrape_exchange_rates():
    # Initialize Selenium WebDriver
    driver = webdriver.Chrome() # Ensure driver path is set if necessary
    rates = {}
    try:
        driver.get(config['exchange_rates_url'])
        # Example code to scrape rates - modify selectors based on the page structure
        banks = config['banks']
        for bank in banks:
            element = driver.find_element(By.XPATH, bank['xpath'])
            rates[bank['name']] = element.text
    finally:
        driver.quit()
    return rates

# Function to compare rates
def compare_rates(today_rates, yesterday_rates):
    comparison = {}
    for bank in today_rates:
        today_rate = today_rates[bank]
        yesterday_rate = yesterday_rates.get(bank)
        if yesterday_rate:
            if today_rate > yesterday_rate:
                comparison[bank] = (today_rate, yesterday_rate, '↑')
            elif today_rate < yesterday_rate:
                comparison[bank] = (today_rate, yesterday_rate, '↓')
            else:
                comparison[bank] = (today_rate, yesterday_rate, '→')
        else:
            comparison[bank] = (today_rate, None, 'N/A')
    return comparison

# Load yesterday's rates from rates_history.json
try:
    with open('rates_history.json', 'r') as f:
        rates_history = json.load(f)
        yesterday_rates = rates_history.get(str(datetime.now().date() - timedelta(days=1)), {})
except FileNotFoundError:
    yesterday_rates = {}

# Scrape today's rates
today_rates = scrape_exchange_rates()

# Compare rates
comparison = compare_rates(today_rates, yesterday_rates)

# Send message to Telegram
message = "Exchange Rate Comparison:\n"
for bank, (today, yesterday, arrow) in comparison.items():
    message += f"{bank}: {today} (Yesterday: {yesterday} {arrow})\n"
requests.post(f'https://api.telegram.org/bot{telegram_token}/sendMessage', data={'chat_id': chat_id, 'text': message})

# Save today's rates to rates_history.json
with open('rates_history.json', 'r+') as f:
    try:
        rates_history = json.load(f)
    except json.JSONDecodeError:
        rates_history = {}
    rates_history[str(datetime.now().date())] = today_rates
    f.seek(0)
    json.dump(rates_history, f)
    f.truncate()