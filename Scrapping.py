from bs4 import BeautifulSoup
import html5lib
import requests
import pandas as pd
import time
session = requests.Session()
url = "http://ufcstats.com/statistics/events/completed?page=all"
response = session.get(url)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html5lib")
    html_table = soup.find("table")
    html_rows = html_table.find_all("tr")
    rows_data = []
    for row in html_rows:
        row_cells = row.find_all("td")
        if len(row_cells) == 2:
            a_tag = row_cells[0].find('a')
            fight = a_tag.get_text(strip=True)
            fight_details_href = a_tag.get("href")
            date = row_cells[0].find('span').get_text(strip=True)
            location = row_cells[1].get_text(strip=True)
            new_row = {
                "event_name": fight,
                "date": date,
                "location": location,
                "event_link": fight_details_href
            }
            rows_data.append(new_row)
            print("Adding event: ", fight, " Details: ", fight_details_href)
    data = pd.DataFrame(rows_data)
    print("DataFrame created... with ", data.size, " items")

data.to_csv("events.csv", index=False)
