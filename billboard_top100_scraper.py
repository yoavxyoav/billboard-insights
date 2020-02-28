import requests
from bs4 import BeautifulSoup
import hashlib
import shutil
import os

URL = "https://www.billboard.com/charts/hot-100"
PARSER = 'lxml'
IMAGE_DIR = './images/'

def hash_img_name(url):
    """ crates a unique hash based on a url of an image"""
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


def get_page(url, parser):
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


def get_item(soup):
    """
    grabs a single item from a soup object
    @param soup: a soup object or a complete web page
    @return: a dictionary with a data of a single item
    """
    # a single bs4 item
    item = soup.find('li', class_='chart-list__element')

    # a dictionary that holds the data of a single item
    print('collecting an item... ')
    item_data = {}

    # collecting each item's data from left to right, as it appears on the site
    item_data['rank'] = int(item.find('span', class_='chart-element__rank__number').text)
    item_data['song'] = item.find('span', class_='chart-element__information__song').text
    item_data['artist'] = item.find('span', class_='chart-element__information__artist').text
    item_data['last_pos'] = int(
        item.find('span', class_='chart-element__meta text--center color--secondary text--last').text)
    item_data['peak'] = int(
        item.find('span', class_='chart-element__meta text--center color--secondary text--peak').text)
    item_data['duration'] = int(
        item.find('span', class_='chart-element__meta text--center color--secondary text--week').text)
    item_data['img_url'] = item.find('span', class_='chart-element__image flex--no-shrink')['style'][23:-3]
    item_data['img_filename'] = hash_img_name(item_data['img_url'])

    try:
        print(f'getting image from {item_data["img_url"]} ')
        download_image(item_data['img_url'], IMAGE_DIR)
    except Exception as e:
        print(f'image download failed for {item_data["song"]}, {item_data["artist"]}! ', e)


    print('done!')
    return item_data


def main():
    soup = get_page(URL, PARSER)
    some_item = get_item(soup)
    print(some_item)


if __name__ == '__main__':
    main()
