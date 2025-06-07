import requests
from bs4 import BeautifulSoup
import html5lib
import pandas as pd


def save_fragment(data: pd.DataFrame, name: str):
    data.to_csv(name, index=False)


event_fights_df = pd.read_csv("event_fights.csv")
urls = event_fights_df["fight_conclusion_link"].dropna()
session = requests.Session()
fight_stats = []
total = len(urls)
counter = total
for url in urls:
    counter -= 1
    print("Recopilating stats from fight: ", url, f" remaining {counter} of {total}")
    response = session.get(url)
    soup = BeautifulSoup(response.text, "html5lib")
    html_fight_details = soup.find("div", attrs={"class": "b-fight-details"})
    fighters = html_fight_details.find_all("div", attrs={"class": "b-fight-details__person"}) or False
    fighter_1_name = fighters[0].find("a").get_text(strip=True) if fighters and len(fighters) > 0 else pd.NA
    fighter_2_name = fighters[1].find("a").get_text(strip=True) if fighters and len(fighters) > 1 else pd.NA
    fighter_1_alias = fighters[0].find("p").get_text(strip=True) if fighters and len(fighters) > 0 else pd.NA
    fighter_2_alias = fighters[1].find("p").get_text(strip=True) if fighters and len(fighters) > 1 else pd.NA
    fighter_1_fight_conclusion = fighters[0].find("i").get_text(strip=True) if fighters and len(fighters) > 0 else pd.NA
    fighter_2_fight_conclusion = fighters[1].find("i").get_text(strip=True) if fighters and len(fighters) > 1 else pd.NA
    fight_total_stats = soup.find("tbody", attrs={"class": "b-fight-details__table-body"})
    row_cells = fight_total_stats.find_all("td") if fight_total_stats else []
    fighters_knowdowns = row_cells[1].find_all("p") if len(row_cells) > 1 else []
    fighter_1_knockdowns = fighters_knowdowns[0].get_text(strip=True) if len(fighters_knowdowns) > 0 else pd.NA
    fighter_2_knockdowns = fighters_knowdowns[1].get_text(strip=True) if len(fighters_knowdowns) > 1 else pd.NA
    fighters_significant_strikes_per = row_cells[3].find_all("p") if len(row_cells) > 3 else []
    fighter_1_significant_strikes_per = fighters_significant_strikes_per[0].get_text(strip=True) if len(
        fighters_significant_strikes_per) > 0 else pd.NA
    fighter_2_significant_strikes_per = fighters_significant_strikes_per[1].get_text(strip=True) if len(
        fighters_significant_strikes_per) > 1 else pd.NA
    fighters_total_strikes = row_cells[4].find_all("p") if len(row_cells) > 4 else []
    fighter_1_total_strikes = fighters_total_strikes[0].get_text(strip=True) if len(
        fighters_total_strikes) > 0 else pd.NA
    fighter_2_total_strikes = fighters_total_strikes[1].get_text(strip=True) if len(
        fighters_total_strikes) > 1 else pd.NA
    fighters_takedowns_per = row_cells[6].find_all("p") if len(row_cells) > 5 else []
    fighter_1_takedowns_per = fighters_takedowns_per[0].get_text(strip=True) if len(
        fighters_takedowns_per) > 0 else pd.NA
    fighter_2_takedowns_per = fighters_takedowns_per[1].get_text(strip=True) if len(
        fighters_takedowns_per) > 1 else pd.NA
    fighters_submission_attempts = row_cells[7].find_all("p") if len(row_cells) > 6 else []
    fighter_1_submission_attempts = fighters_submission_attempts[0].get_text(strip=True) if len(
        fighters_submission_attempts) > 0 else pd.NA
    fighter_2_submission_attempts = fighters_submission_attempts[1].get_text(strip=True) if len(
        fighters_submission_attempts) > 1 else pd.NA
    fighters_reversals = row_cells[8].find_all("p") if len(row_cells) > 7 else []
    fighter_1_reversals = fighters_reversals[0].get_text(strip=True) if len(fighters_reversals) > 0 else pd.NA
    fighter_2_reversals = fighters_reversals[1].get_text(strip=True) if len(fighters_reversals) > 1 else pd.NA
    new_row = {
        "fight_conclusion_link": url,
        "fighter_1_name": fighter_1_name,
        "fighter_2_name": fighter_2_name,
        "fighter_1_alias": fighter_1_alias,
        "fighter_2_alias": fighter_2_alias,
        "fighter_1_fight_conclusion": fighter_1_fight_conclusion,
        "fighter_2_fight_conclusion": fighter_2_fight_conclusion,
        "fighter_1_knockdowns": fighter_1_knockdowns,
        "fighter_2_knockdowns": fighter_2_knockdowns,
        "fighter_1_significant_strikes_per": fighter_1_significant_strikes_per,
        "fighter_2_significant_strikes_per": fighter_2_significant_strikes_per,
        "fighter_1_total_strikes": fighter_1_total_strikes,
        "fighter_2_total_strikes": fighter_2_total_strikes,
        "fighter_1_takedowns_per": fighter_1_takedowns_per,
        "fighter_2_takedowns_per": fighter_2_takedowns_per,
        "fighter_1_submission_attempts": fighter_1_submission_attempts,
        "fighter_2_submission_attempts": fighter_2_submission_attempts,
        "fighter_1_reversals": fighter_1_reversals,
        "fighter_2_reversals": fighter_2_reversals
    }
    fight_stats.append(new_row)
    print(f"\tAdding stats of fight: {fighter_1_name} vs {fighter_2_name}")
    if len(fight_stats) % 1000 == 0 or url == list(urls)[-1]:
        frag_name = f"fight_stats.{counter}.csv"
        print("Saving fragment: ", frag_name)
        save_fragment(pd.DataFrame(fight_stats), frag_name)
        fight_stats = []

# fight_stats_df = pd.DataFrame(fight_stats)
# fight_stats_df.to_csv("fight_stats.csv")

