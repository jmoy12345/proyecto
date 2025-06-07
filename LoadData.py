from sqlalchemy import create_engine, MetaData, Table, insert, select
import pandas as pd
def load_datasets():
    files = [
        'event_fights_transformed.csv',
        'events_transformed.csv',
        'fighter_stats_transformed.csv',
        'fight_stats_transformed.csv'
    ]
    return [pd.read_csv(f) for f in files]

def extract_id_from_url(url):
    return url.strip().split("/")[-1]

def insert_lookup_values(df, col_name, table_name, column_name, conn):
    unique_vals = df[col_name].dropna().unique()
    meta = MetaData()
    table = Table(table_name, meta, autoload_with=conn)
    for val in unique_vals:
        stmt = insert(table).values({column_name: val})
        try:
            conn.execute(stmt)
        except:
            pass
# alchemy triggers and error because of the nan on date_of_birth, reach, etc. for some fighters from very old records
def handle_nan(value):
    return None if pd.isna(value) else value

def insert_events(events_df, conn):
    meta = MetaData()
    cities = Table("cities", meta, autoload_with=conn)
    states = Table("states", meta, autoload_with=conn)
    countries = Table("countries", meta, autoload_with=conn)
    events = Table("events", meta, autoload_with=conn)

    for _, row in events_df.iterrows():
        city_id = conn.execute(
            select(cities.c.id).where(cities.c.city == row["city"])
        ).scalar() or None

        state_id = None
        if pd.notna(row["state"]):
            state_id = conn.execute(
                select(states.c.id).where(states.c.state == row["state"])
            ).scalar()

        country_id = conn.execute(
            select(countries.c.id).where(countries.c.state == row["country"])
        ).scalar() or None

        stmt = insert(events).values(
            id=extract_id_from_url(row["event_link"]),
            event_name=row["event_name"],
            event_date=row["date"],
            city_id=city_id,
            state_id=state_id,
            country_id=country_id
        )
        print(f"Inserting event: {row['event_name']} | {row['city']} | {row['state']} | {row['country']}")
        try:
            conn.execute(stmt)
        except:
            pass

def insert_fighters(fighters_df, conn):
    meta = MetaData()
    stances = Table("stances", meta, autoload_with=conn)
    fighters = Table("fighters", meta, autoload_with=conn)

    for _, row in fighters_df.iterrows():
        stance_id = None
        if pd.notna(row["stance"]):
            stance_id = conn.execute(select(stances.c.id).where(stances.c.stance == row["stance"])).scalar()
            if not stance_id:
                result = conn.execute(insert(stances).values(stance=row["stance"]))
                stance_id = result.inserted_primary_key[0]

        stmt = insert(fighters).values(
            id=extract_id_from_url(row["fighter_details_link"]),
            fighter_name=row["fighter_name"],
            height=handle_nan(row["height"]),
            weight=handle_nan(row["weight"]),
            reach=handle_nan(row["reach"]),
            stance_id=handle_nan(stance_id),
            date_of_birth=handle_nan(row["date_of_birth"]),
            significant_strikes_per_minute=row["significant_strikes_per_minute"],
            striking_accuracy_per=row["striking_accuracy_per"],
            strikes_absorbed_per_minute=row["strikes_absorbed_per_minute"],
            strike_defence_per=row["strike_defence_per"],
            average_takedowns_per_15_minutes=row["average_takedowns_per_15_minutes"],
            takedown_accuracy_per=row["takedown_accuracy_per"],
            takedown_defence_per=row["takedown_defence_per"],
            average_submission_attempts_per_15_min=row["average_submission_attempts_per_15_min"],
            wins=row["wins"],
            losses=row["losses"],
            draws=row["draws"]
        )
        try:
            conn.execute(stmt)
        except Exception as e:
            print(f"Error inserting stance_fighter_fighter: {e}")


def insert_fights(fights_df, conn):
    # Uses event_fights_df
    meta = MetaData()
    fights = Table("fights", meta, autoload_with=conn)
    weight_classes = Table("weight_classes", meta, autoload_with=conn)
    methods = Table("methods", meta, autoload_with=conn)

    for _, row in fights_df.iterrows():
        weight_class_id = conn.execute(
            select(weight_classes.c.id).where(weight_classes.c["class"] == row["weight_class"])
        ).scalar()
        method_id = conn.execute(
            select(methods.c.id).where(methods.c["method"] == row["methods"])
        ).scalar()

        print("Inserting fight: ", row["fight_conclusion_link"])
        stmt = insert(fights).values(
            id=extract_id_from_url(row["fight_conclusion_link"]),
            event_id=extract_id_from_url(row["event_link"]),
            fighter_1_id=extract_id_from_url(row["fighter_1_details_link"]),
            fighter_2_id=extract_id_from_url(row["fighter_2_details_link"]),
            weight_class_id=weight_class_id,
            method_id=method_id
        )
        try:
            conn.execute(stmt)
        except Exception as e:
            print(f"Error inserting fights: {e}")

def insert_fight_stats(fight_stats_df, conn):
    meta = MetaData()
    stats = Table("fight_stats", meta, autoload_with=conn)
    for _, row in fight_stats_df.iterrows():
        # A lot of fighter has no alias so handle_nan
        stmt = insert(stats).values(
            fight_id=extract_id_from_url(row["fight_conclusion_link"]),
            fighter_1_alias=handle_nan(row["fighter_1_alias"]),
            fighter_2_alias=handle_nan(row["fighter_2_alias"]),
            fighter_1_fight_conclusion=row["fighter_1_fight_conclusion"],
            fighter_2_fight_conclusion=row["fighter_2_fight_conclusion"],
            fighter_1_knockdowns=row["fighter_1_knockdowns"],
            fighter_2_knockdowns=row["fighter_2_knockdowns"],
            fighter_1_significant_strikes_per=row["fighter_1_significant_strikes_per"],
            fighter_2_significant_strikes_per=row["fighter_2_significant_strikes_per"],
            fighter_1_takedowns_per=row["fighter_1_takedowns_per"],
            fighter_2_takedowns_per=row["fighter_2_takedowns_per"],
            fighter_1_submission_attempts=row["fighter_1_submission_attempts"],
            fighter_2_submission_attempts=row["fighter_2_submission_attempts"],
            fighter_1_reversals=row["fighter_1_reversals"],
            fighter_2_reversals=row["fighter_2_reversals"],
            fighter_1_strikes_landed=row["fighter_1_strikes_landed"],
            fighter_1_strikes_attempted=row["fighter_1_strikes_attempted"],
            fighter_2_strikes_landed=row["fighter_2_strikes_landed"],
            fighter_2_strikes_attempted=row["fighter_2_strikes_attempted"]
        )
        print(f"Inserting fight stats: ", extract_id_from_url(row["fight_conclusion_link"]))
        try:
            conn.execute(stmt)
        except Exception as e:
            print(f"Error inserting fight_stats {e}")

def main():
    engine = create_engine('mysql+pymysql://a:a@127.0.0.1:3306/ufc')
    with engine.connect() as conn:
        events_fights_df, events_df, fighters_df, fight_stats_df = load_datasets()
        
        insert_lookup_values(fighters_df, "stance", "stances", "stance", conn)
        insert_lookup_values(events_fights_df, "weight_class", "weight_classes", "class", conn)
        insert_lookup_values(events_fights_df, "methods", "methods", "method", conn)
        insert_lookup_values(events_df, "country", "countries", "state", conn)
        insert_lookup_values(events_df, "city", "cities", "city", conn)
        insert_lookup_values(events_df, "state", "states", "state", conn)
        print("Lookup values inserted...")

        insert_fighters(fighters_df, conn)
        insert_events(events_df, conn)
        insert_fights(events_fights_df, conn)
        insert_fight_stats(fight_stats_df, conn)
        conn.commit()

if __name__ == '__main__':
    main()
