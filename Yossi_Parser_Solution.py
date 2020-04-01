import requests
from bs4 import BeautifulSoup
import hashlib
import shutil
import os
import datetime
import time
from selenium import webdriver
import argparse

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
    soup = BeautifulSoup(page, PARSER, from_encoding='latin1')
    print('done!')
    return soup


def grab_data(item):
    """ collecting each item's data from left to right, as it appears on the site """
    item_data = {
        'rank': int(item.find('span', class_='chart-element__rank__number').text),
        'delta': int_if_int(item.find('span', class_='chart-element__information__delta__text text--default').text),
        'song': item.find('span', class_='chart-element__information__song').text,
        'artist': item.find('span', class_='chart-element__information__artist').text,
        'last_pos': int_if_int(
            item.find('span', class_='chart-element__meta text--center color--secondary text--last').text),
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


def get_selenium_image_list(url):
    """"given a top chart URL returns image list with selenium """
    driver = webdriver.Chrome()  # need to install chrome with specific  driver
    driver.get(url)
    driver.fullscreen_window()
    selenium_query = driver.find_elements_by_xpath(
        '//span[@class="chart-element__image flex--no-shrink"][starts-with(@style,"background-image")]')
    image_list = []
    for element in selenium_query:
        image_list.append(element.get_attribute('style'))
    return image_list


def get_all_time():
    """scrapes everything - all tables from all weeks. Outputs to all_time_data.txt"""
    # TODO: have the file opened in a way that we can open it while scraping, not only after it ends.
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


def generate_week(most_recent_date, start_date=FIRST_WEEK_EVER):  # very important modified this function!
    """given a starting date, yields dates going backwards one week each time.
    Runs until the first ever published billboard"""
    current_week = datetime.datetime.strptime(most_recent_date, '%Y-%m-%d')
    print(most_recent_date, start_date)
    while current_week >= datetime.datetime.strptime(start_date, '%Y-%m-%d'):
        current_week_str = current_week.strftime('%Y-%m-%d')
        yield current_week_str
        current_week -= datetime.timedelta(7)


def get_specific_date(input_date):
    """"given input scrapes data from it returns chart"""
    check_dates(input_date)
    soup = get_page_soup(BASE_URL + input_date, PARSER)
    chart = get_weekly_chart(soup)
    return chart


def get_range_date(start_date, end_date):
    """"given a range of dates scrapes charts within range of week"""
    check_dates(start_date, end_date)
    weeks = generate_week(end_date, start_date)
    data_file = open('./%s_%s.txt' % (start_date, end_date), 'w')

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


def check_dates(input_date, end_date=None):
    """"given a date or two dates checks
    if they are valid dates
    and if first date is smaller then second date"""
    try:
        d = datetime.datetime.strptime(input_date, '%Y-%m-%d')
    except ValueError:
        print('%s is not a valid date format please provide yyyy-mm-dd' % input_date)
        exit(1)
    if d > datetime.datetime.now():
        print('cannot scrape for %s ' % input_date)
        exit(1)
    if end_date is not None:
        try:
            d2 = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            print('%s is not a valid date format please provide yyyy-mm-dd' % input_date)
            exit(1)
        if d2 > datetime.datetime.now():
            print('cannot scrape for %s ' % input_date)
            exit(1)
        if d2 <= d:
            print('starting date: %s must be smaller then ending date: %s' % (input_date, end_date))
            exit(1)


ACTION_DICT = {'all': get_all_time, 'single': get_specific_date, 'range': get_range_date}


def get_args():
    """define parser and return user input"""
    parser = argparse.ArgumentParser(description='Web Scraper : please specify data and/or action ')
    parser.add_argument('command', type=str, help='desired function',
                        choices=ACTION_DICT.keys())
    command = parser.parse_known_args()[0].command
    if command in ('single', 'range'):
        parser.add_argument('start_date', type=str, help='first number')
        if command == 'range':
            parser.add_argument('end_date', type=str, help='second number')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = list(get_args().__dict__.values())
    print(args)
    f = ACTION_DICT[args[0]] # desired action
    f(*args[1:])  # un-list all other potential arguments
