import logging
import requests
from bs4 import BeautifulSoup
import json
from bot_action import send_message


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self, login_data):
        self.login_data = login_data
        self.session = requests.Session()

    def login(self):
        login_url = 'https://my.roe.vsei.ua/cabinet/login/'
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = self.session.post(login_url, data=self.login_data, headers=headers)
        if response.status_code == 200:
            logger.info("Login successful!")
            return response
        else:
            logger.error("Login failed. Status code:", response.status_code)
            exit()

    def parse_table(self):
        pokaz_url = 'https://my.roe.vsei.ua/cabinet/pokaz/'
        response = self.session.get(pokaz_url)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the table element
            table = soup.find('table', id='table')
            # Extract table headers
            headers = [th.text.strip() for th in table.find('thead').find('tr').find_all('th')]
            # Extract table rows
            data = []
            for row in table.find('tbody').find_all('tr'):
                row_data = [td.text.strip() for td in row.find_all('td')]
                data.append(dict(zip(headers, row_data)))
            # Store data into a JSON file
            with open('table_data.json', 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

            logger.info("Data stored in 'table_data.json' file.")
        else:
            logger.error("Failed to retrieve data from the URL.")


def get_meter_data(login_data):
    processor = DataProcessor(login_data)
    processor.login()
    processor.parse_table()

    with open('table_data.json', 'r') as file:
        data = json.load(file)

    return data


# Prepare data
with open('secure.json') as f:
    data = json.load(f)

bot_token = data.get("bot_token")
chat_id = data.get("chat_id")


def get_data_for_last_months(months=1):
    rows = months * 2
    parsed_data = get_meter_data(data.get("login_data"))
    data_gen = (
        {k: v for k, v in row.items() if k not in ['Номер лічильника', 'Тип зняття']}
        for row in parsed_data
    )

    data_list = []


    for _ in range(rows):
        row = next(data_gen)
        data_list.append(row)

    transformed_data = {}
    for entry in data_list:
        date = entry['Дата']
        value = entry['Значення лiчильника']
        if date in transformed_data:
            transformed_data[date].append(value)
        else:
            transformed_data[date] = [value]

    formatted_data = ""
    for key, value in transformed_data.items():
        formatted_data += f"'{key}': {value},\n"
    formatted_data = formatted_data.rstrip(',\n')

    return formatted_data


message = get_data_for_last_months(2)

send_message(bot_token, chat_id, message)
