# Billboard Scraper


This is our initial scraper in a larger scale project that aspires to obtain insights from the hits charts on billboard.com
 
## Getting started

What do you need to know in order to get the script running?



1. Upcoming saturday's date in a YYYY-MM-DD format (e.g 2020-03-14)
2. Update the script const `MOST_RECENT_WEEK` with this date as a string (will be passed via command line argument in future version).
3. Use `get_all_time()` to get things moving.

 
---

## Prerequisites

Make sure packages are all installed (as per `requirements.txt`) 

---

## Development strategy

We developed the scraper incrementally going through the following steps:

1. Scraping only one table-item from the first week `get_first_item()`.
2. Scarping only one weekly table (an entire chart) using `get_weekly_chart()`.
3. Scraping all the weekly charts until the very first date using `get_all_time()`.

Also used:
4. A utility function `grab_data()` is going over each item (i.e, a row in a table) and crates a dictionary from collected values.
5. A generator `generate_week()` that calculates the weeks according `MOST_RECENT_WEEK` and `FIRSRT_WEEK_EVER`.  

Tried to implement but decided to wait for next stages:
1. A function `doanload_image()` that downloads thumbnails of collected items as a nice eye-candy in future views. 

## Acknowledgements
The data is the possession of buillboard.com and is scraped for educational purposes only. 