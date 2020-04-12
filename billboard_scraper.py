import requests
from bs4 import BeautifulSoup
import hashlib
import shutil
import os
import datetime
import time
from sys import exit
import traceback
from config.scraper_config import *


def date_string_to_numeric(string_week):
    """
    takes a date in a string formatting (September 14, 1981) and returns it as 1981-09-14
    :param string_week: American style string date
    :return: Numeric European style date
    """
    numeric_week = datetime.datetime.strptime(string_week, '%B %d, %Y').strftime('%Y-%m-%d')
    return numeric_week

def hash_img_name(url):
    """
    Crates a unique filename based on a hash of an image url
    @param url: image web address
    @return: a file name of form 'some_hash_number.jpg'
    """
    return hashlib.sha1(url.encode('utf8')).hexdigest() + '.jpg'


def int_if_int(i):
    """
    Takes some type and returns it as int only if can actually be converted to int. Otherwise, returns None
    @param i: a number, can be of any type (i.e, int, float, string etc).
    @return: the provided i, but as an int
    """
    try:
        return int(i)
    except ValueError as e:
        return None


def download_image(url, destination):
    # TODO: Check why only first 5 images are downloading and not the rest
    """
    Downloads an image and saves it to destination folder. The file name is the original url's hash.
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


class Chart:
    """Class of a weekly chart. The chart is a list of dicts, each dict is a row item from a weekly billboard.com chart."""

    def __init__(self, week, chart):
        self.chart = chart
        self.week = week

    def __getitem__(self, item):
        """
        getting a specific item (song) from a Chart
        :param item: rank in the table
        :return: a dict with all data about a song
        """
        return self.chart[item]

    def __setitem__(self, key, value):
        """
        setting a specific item (song) in a Chart
        :param key: rank in the table
        :param value: dict in the standard structure as defined in Scraper.grab_data()
        :return: None
        """
        self.chart[key] = value

    def set_chart(self, week, chart):
        """
        sets an entire Chart list
        :param week: week of Chart
        :param chart: list of dicts, each dict is a row item data (song)
        :return: None
a        """
        self.chart = chart
        self.week = week

    def get_chart(self):
        """
        get's an entire Chart
        :return: a Chart
        """
        return self.chart

    def get_week(self):
        """
        get's a Chart week
        :return: a week
        """
        return self.week


def generate_week(start_week, end_week):
    """
    Given a starting date, yields dates going backwards one week each time.
    Runs until the first ever published billboard
    @param end_week: the week from which previous week would be calculated backward from
    @param start_week: the week to stop once reached (going backwards from end_week).
    @return: None

    """
    current_week = datetime.datetime.strptime(end_week, '%Y-%m-%d')
    first_week = True
    while current_week >= datetime.datetime.strptime(start_week, '%Y-%m-%d'):
        if not first_week:
            current_week -= datetime.timedelta(7)
        first_week = False
        current_week_str = current_week.strftime('%Y-%m-%d')
        yield current_week_str
    return None


class Scraper:
    def __init__(self, start_week=FIRST_WEEK_EVER, end_week=MOST_RECENT_WEEK, auto_most_recent=False):
        self.start_week = start_week
        if not auto_most_recent:
            self.end_week = end_week
        else:
            self.end_week = self.figure_out_most_recent_week()

        if auto_most_recent == True:
            self.figure_out_most_recent_week()

    def get_page_soup(self, url):
        """
        Grabs a web page and returns a bs4 object
        @param url: the web page to grab
        @param parser: the parser to use
        @return: a bs4 object, representation of whatever is in `url`
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

    @staticmethod
    def grab_data(item):
        """
        Collecting each item's data from left to right, as it appears inside the relevant html tag on the site
        @param item: an object resulted from a soup.findAll() command
        @return: a dictionary holding the data of a row item from a billborad table.
        """
        item_data = {
            'rank': int(item.find('span', class_='chart-element__rank__number').text),
            'delta': int_if_int(item.find('span', class_='chart-element__information__delta__text text--default').text),
            'song': item.find('span', class_='chart-element__information__song').text,
            'artist': item.find('span', class_='chart-element__information__artist').text,
            'last_pos': int_if_int(
                item.find('span', class_='chart-element__meta text--center color--secondary text--last').text),
            'peak': int(item.find('span', class_='chart-element__meta text--center color--secondary text--peak').text),
            'duration': int(
                item.find('span', class_='chart-element__meta text--center color--secondary text--week').text),
            'img_url': item.find('span', class_='chart-element__image flex--no-shrink')['style'][23:-3]
        }

        item_data['img_filename'] = hash_img_name(item_data['img_url'])

        return item_data

    def get_first_item(self, soup):
        """
        Grabs a first item from a soup object. Good for quick testing purposes and incremental development.
        @param soup: a soup object or a complete web page
        @return: a dictionary with a data of a first item
        """
        # a first bs4 item
        item = soup.find('li', class_='chart-list__element')

        # a dictionary that holds the data of a first item
        print('collecting an item... ')

        item_data = self.grab_data(item)

        try:
            print(f'getting image from {item_data["img_url"]} ')
            download_image(item_data['img_url'], IMAGE_DIR)
        except Exception as e:
            print(f'image download failed for {item_data["song"]}, {item_data["artist"]}! ', e)

        print('done!')
        return item_data

    def weekly_chart_from_soup(self, soup):
        """
        Gets the entire weekly chart (all items).
        @param soup: a soup object of a page containing a billboard chart
        @return: a Chart object
        """
        week = self.get_week_string(soup)
        print(f'fetching entire chart for week {week} ...')
        try:
            items = soup.findAll('li', class_='chart-list__element display--flex')
            print('got all items bs4 objects')
        except Exception as e:
            print(f'something went wrong with getting weekly chart from week {week}!', e)
            raise

        all_page_items = []  # storing all the items for a page
        for item in items:
            item_data = self.grab_data(item)
            print(f"got data for {item_data['rank']}) {item_data['song']} - {item_data['artist']}")

            try:
                print(f'getting image from {item_data["img_url"]} ')
                download_image(item_data['img_url'], IMAGE_DIR)
            except Exception as e:
                print(f'image download failed for {item_data["song"]}, {item_data["artist"]}! ', e)

            print('done!')

            all_page_items.append(item_data)

        week = date_string_to_numeric(week)

        chart = Chart(week, all_page_items)

        return chart

    @staticmethod
    def get_week_string(soup):
        """
        Get's the week of a given chart soup-object. returns a string
        @param soup: soup object of a billboard.com chart page
        @return: string representing the week
        """
        print('figuring out the week')
        week = soup.find('button', class_='date-selector__button button--link').text
        week = week.strip('\n').strip(' ').strip('\n')
        return week

    def get_time_range(self, start_week=None, end_week=None):
        """
        Scrapes everything - all tables from all weeks as defined by `start_week` and `end_week` (defaults in
        parser_config.py).
        Outputs to file as defined by SONG_DATA (default: all_time_data.txt)
        @return: a dictionary of all weekly chart within the chosen time range as {week: chart} key-value pairs.
        """
        if start_week is None:
            start_week = self.start_week
        if end_week is None:
            end_week = self.end_week

        if end_week == MOST_RECENT_WEEK and start_week == FIRST_WEEK_EVER:
            print('Scraper is getting time range, but since no `start_weekd` and `end_weed` arguments passed when\
             creating the Scraper object, it will be using default values')

        print(f'getting charts from {self.start_week} to {self.end_week}')
        weeks = generate_week(start_week, end_week)

        now = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        try:
            print(f'Creating data directory at {DATA_DIR}')
            os.mkdir(DATA_DIR)
        except FileExistsError:
            print('Data directory already exists')
        data_file = open(f'{DATA_DIR}{now}_{start_week}_{end_week}_{SONG_DATA_FILE}', 'w')
        print(f'Writing data to {SONG_DATA_FILE}')
        time_range_charts = {}

        try:
            for current_week in weeks:
                print(f'current week: {current_week}')
                weekly_soup = self.get_page_soup(BASE_URL + current_week)
                current_week_chart = self.weekly_chart_from_soup(weekly_soup)
                current_week_list = current_week_chart.get_chart()

                # appending weekly Chart object to time_range_charts
                time_range_charts[current_week] = current_week_chart

                # printing current week data to screen
                print('\t\t\t<-----------*-----------*-----------*-----------*----------->')
                print(f'\t\t\t\t\t\tData for {current_week}')
                print('\t\t\t<-----------*-----------*-----------*-----------*----------->')
                for item in current_week_list:
                    print(item)

                # writing current week data to text file
                data_file.write('\n\n\n' + current_week + '\n')
                for item in current_week_list:
                    data_file.writelines(str(item) + '\n')

                # TODO: get tid of the next line if possible
                time.sleep(1)
            data_file.close()
        except Exception as e:
            print('Something went wrong while running get_time_range():', e)
            traceback.print_exc()
            exit(1)

        return time_range_charts

    def get_all_time(self):
        """
        Hard coded method go get all time charts from the first week ever on billboard.com until most recent week
        (as defined in MOST_RECENT_WEEK in ./config/scraper_config.py)
        :return: list of Chart objects from all time.
        """
        print('Getting all time! This might take a while.')
        try:
            all_time_charts = self.get_time_range(FIRST_WEEK_EVER, MOST_RECENT_WEEK)
        except Exception as e:
            print(f'There was a problem while running get_all_time(): {e}')
            raise Exception

        return all_time_charts

    def figure_out_most_recent_week(self, url=BASE_URL):
        """
        This function runs if __init__() parameter auto_most_recent is set to True (it is False by default).
        The method retrieves the week from BASE_URL, and overrides the constant `MOST_RECENT_WEEK` from the
        scraper_config with that week.
        :param url: by default it is: https://www.billboard.com/charts/hot-100 and probably should not be changed.
        :return: string of most recent week with an available chart
        """

        website_formatted_date = self.get_week_string(self.get_page_soup(BASE_URL))
        scraper_formatted_date = datetime.datetime.strptime(website_formatted_date, '%B %d, %Y').strftime('%Y-%m-%d')

        return scraper_formatted_date

    def get_update_from_time(self, start_week=None):
        """
        Get's the charts from a certain time point until MOST_RECENT_WEEK from scraper_config or until today if
        auto_most_recent is set to True.
        :param start_week: the week from which the update is starting.
        :return: list of Chart objects
        """
        if start_week == None:
            start_week = self.start_week

        return self.get_time_range(start_week, self.end_week)

    def get_specific_week(self, specific_week):
        """
        Get's a Chart of a specific single week.
        :param specific_week: date string in the form of YYYY-MM-DD.
        :return: Chart object
        """
        try:
            weekly_soup = self.get_page_soup(BASE_URL + specific_week)
            chart = self.weekly_chart_from_soup(weekly_soup)
        except Exception as e:
            print(f'There was an error getting specific week ({specific_week}) chart:', e)
            traceback.print_exc()
            exit(1)

        return chart
