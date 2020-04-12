from billboard_scraper import Scraper
from query_handler import Query
import argparse

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

@except_on_error
def main():
    # action, args = get_args()

    query = Query()
    scraper = Scraper(auto_most_recent=True, query=query)

    # action_dict = {'all': scraper.get_all_time, 'single': scraper.get_specific_week, 'range': scraper.get_time_range}
    # action_dict[action](*args)

    # scraper.get_specific_week('2010-09-14')

    scraper.get_all_time()

if __name__ == '__main__':
    main()
