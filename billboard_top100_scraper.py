import requests
from bs4 import BeautifulSoup
import hashlib
import shutil
import os
import datetime
import time
from sys import exit

import csv

PARSER = 'lxml'
IMAGE_DIR = './images/'
BASE_URL = "https://www.billboard.com/charts/hot-100/"
MOST_RECENT_WEEK = '2020-03-14'
FIRST_WEEK_EVER = '1958-08-04'


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
    # TODO: Check why only first 5 images are downloading and not the rest
    """
    downloads an image and saves it to destination folder. The file name is the original url's hash.
    @param url: image source url
    @param destination: folder to save the image to
    @return: 0 if everything runs properly
    """
    if url == '':
        print('no image url, aborting download')
        return
    if not os.path.isdir(IMAGE_DIR):
        try:
            os.mkdir(IMAGE_DIR)
        except Exception as e:
            print('could not create image directory! ', e)
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
        print(f'Fetching page from {url}')
        trial = 0
        while True:
            trial += 1
            print(f'requesting page, attempt #{trial} --- ', end='')
            r = requests.get(url)
            if r.status_code == 200:
                break
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
        'last_pos': int_if_int(item.find('span', class_='chart-element__meta text--center color--secondary text--last').text),
        'peak': int(item.find('span', class_='chart-element__meta text--center color--secondary text--peak').text),
        'duration': int(item.find('span', class_='chart-element__meta text--center color--secondary text--week').text),
        'img_url': item.find('span', class_='chart-element__image flex--no-shrink')['style'][23:-3]
    }

    item_data['img_filename'] = hash_img_name(item_data['img_url'])

    return item_data


def get_first_item(soup):
    """
    grabs a first item from a soup object. Good for quick testing purposes and incremental development.
    @param soup: a soup object or a complete web page
    @return: a dictionary with a data of a first item
    """
    # a first bs4 item
    item = soup.find('li', class_='chart-list__element')

    # a dictionary that holds the data of a first item
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
    """ gets the entire weekly chart (all items). returns a list of dicts, each dict is a song-item  """
    print(f'fetching entire chart for week {get_week(soup)} ...')
    try:
        items = soup.findAll('li', class_='chart-list__element display--flex')
        print('got all items bs4 objects')
    except Exception as e:
        print('something went wrong!', e)

    all_page_items = []  # storing all the items for a page
    for item in items:
        item_data = grab_data(item)
        print(f"got data for {item_data['rank']}) {item_data['song']} - {item_data['artist']}")

        try:
            print(f'getting image from {item_data["img_url"]} ')
            download_image(item_data['img_url'], IMAGE_DIR)
        except Exception as e:
            print(f'image download failed for {item_data["song"]}, {item_data["artist"]}! ', e)

        print('done!')

        all_page_items.append(item_data)

    return all_page_items


def get_week(soup):
    """ get's the week of a given chart soup-object. returns a string"""
    print('figuring out the week')
    week = soup.find('button', class_='date-selector__button button--link').text
    week = week.strip('\n').strip(' ').strip('\n')
    return week


def get_all_time():
    """scrapes everything - all tables from all weeks. Outputs to all_time_data.txt"""
    #TODO: have the file opened in a way that we can open it while scraping, not only after it ends.
    weeks = generate_week(MOST_RECENT_WEEK)
    data_file = open('./all_time_data.txt', 'w')

    try:
        for current_week in weeks:
            print(f'current week: {current_week}')
            week = get_page_soup(BASE_URL + current_week, PARSER)
            current_week_data = get_weekly_chart(week)

            # printing current week data to screen
            print(f'Data for <----------->  <----------->  <----------->  <----------->  <-----------> {current_week}')
            for item in current_week_data:
                print(item)

            # writing current week data to file
            data_file.write('\n\n\n' + current_week + '\n')
            for item in current_week_data:
                data_file.writelines(str(item) + '\n')

            time.sleep(3)
        data_file.close()
    except:
        print('something went wrong while running get_all_time() !!!')
        exit(1)
    return 0


def generate_week(most_recent_date):
    """given a starting date, yields dates going backwards one week each time.
    Runs until the first ever published billboard"""
    current_week = datetime.datetime.strptime(most_recent_date, '%Y-%m-%d')
    first_week = True
    while current_week >= datetime.datetime.strptime(FIRST_WEEK_EVER, '%Y-%m-%d'):
        if not first_week:
            current_week -= datetime.timedelta(7)
        first_week = False
        current_week_str = current_week.strftime('%Y-%m-%d')
        yield current_week_str




if __name__ == '__main__':

    # # scraping the most recent page (which is the default week for the main url)
    # soup = get_page_soup(BASE_URL, PARSER)

    # # for testing: getting the first item of the most recent week
    # some_test_item = get_first_item(soup)
    # print(some_test_item)

    # week = get_week(soup)
    # print(week, '\n')

    # # scraping the entire first week
    # weekly_items = get_weekly_chart(soup)
    # for item in weekly_items:
    #     print(item)

    # the real deal: scraping all time, from most recent week to the beginning


    # all_time_chart = get_all_time()
    # print(all_time_chart)

    get_weekly_chart()