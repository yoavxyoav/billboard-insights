from billboard_scraper import Scraper
from query_handler import Query
import argparse
import datetime


def except_on_error(func):
    """
    Decorator function for main to handle exceptions (at the moment, only raises).
    :param func: main()
    :return: a function the decorates main() and raises upon any exception
    """

    def wrapper():
        try:
            func()
        except Exception as e:
            print('An error has occurred:', e)
            raise e

    return wrapper


def get_args():
    """define parser and return user input"""
    parser = argparse.ArgumentParser(description='Web Scraper : please specify data and/or action ')
    parser.add_argument('command', type=str, help='desired function',
                        choices=('all', 'single', 'range'))
    command = parser.parse_known_args()[0].command
    if command in ('single', 'range'):
        parser.add_argument('start_date', type=str, help='first number')
        if command == 'range':
            parser.add_argument('end_date', type=str, help='second number')
    args = parser.parse_args()
    return command, list(args.__dict__.values())[1:]


def check_dates(input_date=None, end_date=None):  # this part contains try except statements to get detailed error
    """"given a date or two dates checks
    if they are valid dates
    and if first date is smaller then second date"""
    if input_date is not None:
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


@except_on_error
def main():
    action, args = get_args()
    check_dates(*args)
    query = Query()
    scraper = Scraper(auto_most_recent=True, query=query)
    action_dict = {'all': scraper.get_all_time, 'single': scraper.get_specific_week, 'range': scraper.get_time_range}
    action_dict[action](*args)  # returns a table object


if __name__ == '__main__':
    main()
