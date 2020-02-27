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
item_data.rank = item.find('span', class_='chart-element__rank')
