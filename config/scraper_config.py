# parsing method
PARSER = 'lxml'

# directory to store downloaded thumbnails
IMAGE_DIR = './images/'

# base URL to parse. Default: https://www.billboard.com/charts/hot-100/
BASE_URL = "https://www.billboard.com/charts/hot-100/"

# latest week until which the parser parses
MOST_RECENT_WEEK = '2020-03-14'

# earlier week to parse from when parsing all time with get_all_time(). Default: '1958-08-04'
FIRST_WEEK_EVER = '1958-08-04'

# file suffix to save parsed data to when parsing all time with get_time_range().
# (prefix of file would be {current time}_{start_week}_{end_week}
SONG_DATA_FILE = 'song_data.txt'

# dir into which to save scraped text data
DATA_DIR = './data/'

