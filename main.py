import json
import requests
import selenium.common.exceptions
from seleniumwire import webdriver
from selenium.webdriver.common.by import By

API_KEY = "1X4B3B88CQ8QXZIS3C89U556DJC4D6I6H6"
url = 'https://api.etherscan.io/api'
OPENSEA_CONTRACT = '0x7Be8076f4EA4A4AD08075C2508e481d6C946D12b'

# тут будут уже обработанные транзакции
transactions_refactored = []

for i in range(1, 2):
    print(f"Страница {i}")
    params = {
        'module': 'logs',
        'action': 'getLogs',
        'fromBlock': 0,
        'toBlock': 'latest',
        'page': i,
        'offset': 10,
        'address': OPENSEA_CONTRACT,
        'apikey': API_KEY
    }
    r = requests.get(url, params=params)
    if json.loads(r.text)['message'] == "No records found":
        print("Транзакций не найдено")
    else:
        transactions = json.loads(r.text)["result"]
        print(f"Получено {len(transactions)} транзакций")
        # Подпись нужного нам метода
        OrdersMatchedSig = "0xc4109843e0b7d514e4c093114b863f8e7d8d9a458c372cd51bfe526b588006c9"

        # Для конвертации wei в ETH
        DIVIDER = 10 ** 18

        for tr in transactions:
            result = {}
            if tr['topics'][0] == OrdersMatchedSig:
                result['maker'] = '0x' + (tr['topics'][1])[26:]
                result['taker'] = '0x' + (tr['topics'][2])[26:]
                result['price'] = int('0x' + tr['data'][-32:], 16) / DIVIDER
                transactions_refactored.append(result)

addresses = set()
for tr in transactions_refactored:
    addresses.add(tr['maker'])
    addresses.add(tr['taker'])

print(f"Уникальных адресов получено: {len(addresses)}")
print(len(transactions_refactored))
list_dict = []
for a in addresses:
    params = {
        'module': 'account',
        'action': 'balance',
        'address': a,
        'tag': 'latest',
        'apikey': API_KEY
    }
    r = requests.get(url, params=params)
    result = {}
    balance = json.loads(r.text)["result"]
    result['address'] = a
    result['balance'] = int(balance)/10**18
    list_dict.append(result)

#
# options = {
#     'proxy': {
#         'http': 'http://p1tw1X:q7peLP@196.17.67.189:8000',
#         'https': 'https://p1tw1X:q7peLP@196.17.67.189:8000',
#         'no_proxy': 'localhost,127.0.0.1'
#     }
# }
driver = webdriver.Chrome()
for person in list_dict:
    driver.get("https://opensea.io/" + person['address'])
    links = []
    try:
        social_section = driver.find_element(By.CLASS_NAME, "sc-29427738-0 sc-630fc9ab-0 sc-4ce9b68d-0 dVNeWL jSPhMX exDVqa")
        socials = driver.find_elements(By.XPATH, '//*[@id="main"]/div/div/div/div[3]/div/div/div[2]/div/div/div[1]/div/div[1]/a')
        for social in socials:
            links.append(social.get_attribute('href'))
    except selenium.common.exceptions.NoSuchElementException:
        print("Соцсетей нет")
    finally:
        person['socials'] = links
driver.quit()

for person in list_dict:
    print(person)

