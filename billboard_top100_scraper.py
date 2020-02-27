import requests
from bs4 import BeautifulSoup

URL = "https://www.billboard.com/charts/hot-100"
PARSER = 'lxml'

try:
    print(f'Fetching page from {URL}')
    r = requests.get(URL)
    print(f"Successful! {r}")
except requests.exceptions.RequestException:
    print(f"something went wrong... ({r})")

page = r.text

print(f'Parsing using {PARSER}... ', end='')
soup = BeautifulSoup(page, PARSER)
print('done')

item = soup.find('li', class_='chart-list__element')

item_data = {}

# collecting each item's data from left to right, as it appears on the site
item_data['rank'] = item.find('span', class_='chart-element__rank__number').text
item_data['song'] = item.find('span', class_='chart-element__information__song').text
item_data['artist'] = item.find('span', class_='chart-element__information__artist').text
item_data['last_pos'] = item.find('span', class_='text--last').text
item_data['peak'] = item.find('span', class_='text--peak').text
item_data['duration'] = item.find('span', class_='text--week').text
