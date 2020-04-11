# Billboard Scraper


This is our initial scraper in a larger scale project that aspires to obtain insights from the hits charts on billboard.com
 
## Getting started

What do you need to know in order to get the script running?



1. Upcoming saturday's date in a YYYY-MM-DD format (e.g 2020-03-14)
2. Take a look at `./config/scraper_config.py` 
3. Update the script const `MOST_RECENT_WEEK` with this date as a string (will be passed via command line argument in future version).
4. import the `Scraper` class from the `billboard_scraper` module
5. Create a scraper object (i.e: `scraper = Scraper()`)
6. Use `get_all_time()` to scrape everything.

 
---
## Usage examples:

It is possible to either instantiate the Scraper with given dates or without:

both

`scraper = Scraper()` 

and

`scraper = Scraper('2010-04-04', '2015-01-15')`

are ok.

The first one is using the default time range values (as in `parser_config.py`), while the second is customized.

### After instantiation:

* `scraper.get_time_range()` will get the time range of specified (or dafault) values.
* `scraper.get_all_time()` is hardcoded to get all charts from all time (according to config default), ignoring the values
 of `start_week` and `end_week` that were passed during instantiation.
*  `scraper.get_update_from_time()` is scraping starting from `start_week`. Works in conjunction with the Scraper's 
`auto_most_recent=True` argument so that the scraper automatically assigns the very last weekly chart's date on billboard.com
to `end_eeek`.
* `scraper.get_specific_week()` does as it says. Must pass an argument (ignores instantiation values). 
Note that if the given date is within a billboard.com chart week range, the week that encompases the given date will be 
fetched. E.g, asking for 2010-09-14 will get the chart that is associated with the date 2010-09-18. 
---
## Prerequisites

Make sure packages are all installed (as per `requirements.txt`). Only do this in a dedicated environment!

---

## Development strategy

We developed the scraper incrementally going through the following steps:

1. Scraping only one table-item from the first week `get_first_item()`.
2. Scarping only one weekly table (an entire chart) using `get_weekly_chart()`.
3. Scraping all the weekly charts going back from most recent to the very first date using `get_all_time()`.

Also used:
4. A utility function `grab_data()` is going over each item (i.e, a row in a table) and crates a dictionary from collected values.
5. A generator `generate_week()` that calculates the weeks according `MOST_RECENT_WEEK` and `FIRSRT_WEEK_EVER`.  

Tried to implement but decided to wait for next stages:
1. A function `doanload_image()` that downloads thumbnails of collected items as a nice eye-candy in future views. 

## Acknowledgements
The data is the possession of buillboard.com and is scraped for educational purposes only. 