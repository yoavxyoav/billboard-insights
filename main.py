from billboard_scraper import Scraper
from config.scraper_config import *


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


@except_on_error
def main():
    ###
    ### The following commented text will be left for the process of the initial development in order to quickly
    ### test and debug various functions of the parser (instead of rewritten every time).
    ### they will be removed from the final product.
    ###

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

    scraper = Scraper(auto_most_recent=True)
    # scraper.get_time_range()
    # scraper.get_update_from_time()
    chart = scraper.get_specific_week('2010-09-14')
    print(chart.chart)
if __name__ == '__main__':
    main()
