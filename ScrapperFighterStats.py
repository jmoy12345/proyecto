import requests
from bs4 import BeautifulSoup
import html5lib
import pandas as pd

def save_fragment(data: pd.DataFrame, name: str):
    data.to_csv(name, index=False)

df = pd.read_csv("event_fights.csv")
figher_1_links = df["fighter_1_details_link"]
figher_2_links = df["fighter_2_details_link"]
combined = pd.concat([figher_1_links, figher_2_links])
unique_fighter_links = combined.unique()
total = unique_fighter_links.size
counter = total
session = requests.Session()
fight_stats = []
for url in unique_fighter_links:
    counter -= 1
    print("Recopilating fighter stats: ", url, f" remaining {counter} of {total}")
    response = session.get(url)
    soup = BeautifulSoup(response.text, "html5lib")

    # Extract fighter titles
    titles = soup.find("h2", attrs={"class": "b-content__title"}).find_all("span") or False
    fighter_name = titles[0].get_text(strip=True) if titles and len(titles) > 0 else pd.NA
    fighter_record = titles[1].get_text(strip=True) if titles and len(titles) > 1 else pd.NA

    # Extract physiological data (height, weight, reach, etc.)
    physiological_data = soup.find("ul", attrs={"class": "b-list__box-list"}).find_all("i") or False

    # Now extract the values that come right after <i> tags
    height = physiological_data[0].find_next_sibling(text=True).strip() if physiological_data else pd.NA
    weight = physiological_data[1].find_next_sibling(text=True).strip() if physiological_data else pd.NA
    reach = physiological_data[2].find_next_sibling(text=True).strip() if physiological_data else pd.NA
    stance = physiological_data[3].find_next_sibling(text=True).strip() if physiological_data else pd.NA
    date_of_birth = physiological_data[4].find_next_sibling(text=True).strip() if physiological_data else pd.NA

    # Extract performance data
    performance_data = soup.find("div", attrs={"class": "b-list__info-box-left clearfix"}).find("ul").find_all("i") or False

    # Example of extracting stats for performance data with the same method
    significant_strikes_per_minute = performance_data[0].find_next_sibling(text=True).strip() if performance_data else pd.NA
    striking_accuracy = performance_data[1].find_next_sibling(text=True).strip() if performance_data else pd.NA
    strikes_absorbed_per_minute = performance_data[2].find_next_sibling(text=True).strip() if performance_data else pd.NA
    strike_defence = performance_data[3].find_next_sibling(text=True).strip() if performance_data else pd.NA

    # Second set of performance data (right side)
    performance_data2 = soup.find("div", attrs={"class": "b-list__info-box-right b-list__info-box_style-margin-right"}).find("ul").find_all("i") or False

    average_takedowns_per_15_minutes = performance_data2[1].find_next_sibling(text=True).strip() if performance_data2 else pd.NA
    takedown_accuracy = performance_data2[2].find_next_sibling(text=True).strip() if performance_data2 else pd.NA
    takedown_defence = performance_data2[3].find_next_sibling(text=True).strip() if performance_data2 else pd.NA
    average_submission_attempts_per_15_min = performance_data2[4].find_next_sibling(text=True).strip() if performance_data2 else pd.NA

    new_row = {
        "fighter_details_link": url,
        "fighter_name": fighter_name,
        "fighter_record": fighter_record,
        "height": height,
        "weight": weight,
        "reach": reach,
        "stance": stance,
        "date_of_birth": date_of_birth,
        "significant_strikes_per_minute": significant_strikes_per_minute,
        "striking_accuracy": striking_accuracy,
        "strikes_absorbed_per_minute": strikes_absorbed_per_minute,
        "strike_defence": strike_defence,
        "average_takedowns_per_15_minutes": average_takedowns_per_15_minutes,
        "takedown_accuracy": takedown_accuracy,
        "takedown_defence": takedown_defence,
        "average_submission_attempts_per_15_min": average_submission_attempts_per_15_min,
    }


    fight_stats.append(new_row)
    print(f"\tAdding stats for fighter: {fighter_name}")

    # Saving the data to a CSV fragment every 1000 rows or on the last item
    if len(fight_stats) % 1000 == 0 or url == list(unique_fighter_links)[-1]:
        frag_name = f"fighter_stats.{counter}.csv"
        print("Saving fragment: ", frag_name)
        save_fragment(pd.DataFrame(fight_stats), frag_name)
        fight_stats = []


