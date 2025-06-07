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

event_details = []
total = data.shape[0]
counter = data.shape[0]
for url in data['event_link']:
    counter -= 1
    print("Recopilating fights from event: ", url, f" remaining {counter} of {total}")
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html5lib")
        html_tbody = soup.find("tbody")
        html_rows = html_tbody.find_all("tr")
        for row in html_rows:
            row_cells = row.find_all("td")
            if len(row_cells) == 10:
                fight_conclusion_link = row_cells[0].find("a")
                fight_conclusion_link = fight_conclusion_link.get("href") if fight_conclusion_link else pd.NA
                fighters_cell = row_cells[1].find_all("a") or False
                fighter_1_details_link = fighters_cell[0].get("href") if fighters_cell else pd.NA
                fighter_1_name = fighters_cell[0].get_text(strip=True) if fighters_cell else pd.NA
                fighter_2_details_link = fighters_cell[1].get("href") if len(fighters_cell) > 1 else pd.NA
                fighter_2_name = fighters_cell[1].get_text(strip=True) if len(fighters_cell) > 1 else pd.NA
                knowdowns = row_cells[2].find_all("p") or False
                fighter_1_knowdowns = knowdowns[0].get_text(strip=True) if knowdowns else pd.NA
                fighter_2_knowdowns = knowdowns[1].get_text(strip=True) if knowdowns and len(knowdowns) > 1 else pd.NA
                strikes = row_cells[3].find_all("p") or False
                fighter_1_strikes = strikes[0].get_text(strip=True) if strikes else pd.NA
                fighter_2_strikes = strikes[1].get_text(strip=True) if strikes and len(strikes) > 1 else pd.NA
                takedowns = row_cells[4].find_all("p") or False
                fighter_1_takedows = takedowns[0].get_text(strip=True) if takedowns else pd.NA
                fighter_2_takedows = takedowns[1].get_text(strip=True) if takedowns and len(takedowns) > 1 else pd.NA
                submissions = row_cells[5].find_all("p") or False
                fighter_1_submissions = submissions[0].get_text(strip=True) if submissions else pd.NA
                fighter_2_submissions = submissions[1].get_text(strip=True) if submissions and len(submissions) > 1 else pd.NA
                weight_class = row_cells[6].find("p").get_text(strip=True) if row_cells[6].find("p") else pd.NA
                methods = [tag.get_text(strip=True) for tag in row_cells[7].find_all("p")] or False
                end_round = row_cells[7].find("p").get_text(strip=True) if row_cells[7].find("p") else pd.NA
                time_end = row_cells[8].find("p").get_text(strip=True) if row_cells[8].find("p") else pd.NA

                new_row = {
                    "event_link":url,
                    "fight_conclusion_link":fight_conclusion_link,
                    "fighter_1_details_link":fighter_1_details_link,
                    "fighter_1_name":fighter_1_name,
                    "fighter_2_details_link":fighter_2_details_link,
                    "fighter_2_name":fighter_2_name,
                    "fighter_1_knowdowns":fighter_1_knowdowns,
                    "fighter_2_knowdowns":fighter_2_knowdowns,
                    "fighter_1_strikes":fighter_1_strikes,
                    "fighter_2_strikes":fighter_2_strikes,
                    "fighter_1_takedows":fighter_1_takedows,
                    "fighter_2_takedows":fighter_2_takedows,
                    "fighter_1_submissions":fighter_1_submissions,
                    "fighter_2_submissions":fighter_2_submissions,
                    "weight_class":weight_class,
                    "methods":methods,
                }
                event_details.append(new_row)
                print(f"\tAddid fight: {fighter_1_name} vs {fighter_2_name}")
event_fights_df = pd.DataFrame(event_details)


event_fights_df.to_csv("event_fights.csv", index=False)