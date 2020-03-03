import requests
from bs4 import BeautifulSoup
import hashlib
import shutil
import os
import csv

URL = "https://www.billboard.com/charts/hot-100"
PARSER = 'lxml'
IMAGE_DIR = './images/'


def int_if_int(i):
    """ takes some type and returns it as int only if can actually be converted to int. Otherwise, returns None"""
    try:
        return int(i)
    except ValueError as e:
        return None


def hash_img_name(url):
    """ crates a unique filename based on a url of an image"""
    return hashlib.sha1(url.encode('utf8')).hexdigest() + '.jpg'


def download_image(url, destination):
    """
    downloads an image and saves it to destination folder. The file name is the original url's hash.
    @param url: image source url
    @param destination: folder to save the image to
    @return: 0 if everything runs properly
    """
    if not os.path.isdir(IMAGE_DIR):
        try:
            os.mkdir(IMAGE_DIR)
        except Exception as e:
            print('count not create image directory! ', e)
    try:
        print('requesting image... ', end='')
        img = requests.get(url, stream=True)
        print(img)
        img.raw.decode_content = True
        local_filename = hash_img_name(url)  # creates a unique filename
        with open(IMAGE_DIR + local_filename, 'wb') as f:
            shutil.copyfileobj(img.raw, f)
        return 0
    except:
        print('something went wrong')


def get_page_soup(url, parser):
    """
    grabs a web page and returns a bs4 object

    @param url: the web page to grab
    @param parser: the parser to use
    @return: a bs4 object
    """
    try:
        print(f'Fetching page from {URL}')
        r = requests.get(URL)
        print(f"Successful! {r}")
    except requests.exceptions.RequestException:
        print(f"something went wrong... ({r})")

    page = r.text

    print(f'Parsing using {PARSER}... ', end='')
    soup = BeautifulSoup(page, PARSER)
    print('done!')
    return soup


def grab_data(item):
    """ collecting each item's data from left to right, as it appears on the site """
    item_data = {
        'rank': int(item.find('span', class_='chart-element__rank__number').text),
        'delta': int_if_int(item.find('span', class_='chart-element__information__delta__text text--default').text),
        'song': item.find('span', class_='chart-element__information__song').text,
        'artist': item.find('span', class_='chart-element__information__artist').text,
        'last_pos': int(item.find('span', class_='chart-element__meta text--center color--secondary text--last').text),
        'peak': int(item.find('span', class_='chart-element__meta text--center color--secondary text--peak').text),
        'duration': int(item.find('span', class_='chart-element__meta text--center color--secondary text--week').text),
        'img_url': item.find('span', class_='chart-element__image flex--no-shrink')['style'][23:-3]
    }

    item_data['img_filename'] = hash_img_name(item_data['img_url'])

    return item_data


def get_single_item(soup):
    """
    grabs a single item from a soup object
    @param soup: a soup object or a complete web page
    @return: a dictionary with a data of a single item
    """
    # a single bs4 item
    item = soup.find('li', class_='chart-list__element')

    # a dictionary that holds the data of a single item
    print('collecting an item... ')

    item_data = grab_data(item)

    try:
        print(f'getting image from {item_data["img_url"]} ')
        download_image(item_data['img_url'], IMAGE_DIR)
    except Exception as e:
        print(f'image download failed for {item_data["song"]}, {item_data["artist"]}! ', e)

    print('done!')
    return item_data


def get_weekly_chart(soup):
    """ gets the entire weekly chart (all items) """
    print(f'fetching entire chart for week {get_week(soup)} ...')
    try:
        items = soup.findall('li', class_='chart-list__element')
        print('got all items bs4 objects')
    except:
        print('something went wrong!')


def get_week(soup):
    """ get's the week of the current chart """
    week = soup.find('button', class_='date-selector__button button--link').text
    week = week.strip('\n').strip(' ').strip('\n')
    return week


def main():
    pass


if __name__ == '__main__':
    soup = get_page_soup(URL, PARSER)

    some_test_item = get_single_item(soup)
    print(some_test_item)

    week = get_week(soup)
    print(week)
