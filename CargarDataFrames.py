import os
import pandas as pd

def cargas_fight_stats(prefijo_archivos):
    df_final = []
    for prefijo in prefijo_archivos:
        directorio = os.getcwd()
        archivos = [f for f in os.listdir(directorio) if f.startswith(prefijo) and f.endswith(".csv")]
        rutas_absolutas = [os.path.join(directorio, a) for a in archivos]
        dataframes = [pd.read_csv(r) for r in rutas_absolutas]
        df_final.append(pd.concat(dataframes, ignore_index=True))
    return df_final

archivos = ["events", "event_fights", "fight_stats", "fighter_stats"]
events_df, event_fights, fight_stats_df, fighter_stats_df = cargas_fight_stats(archivos)

print(f"Dataframes cargados: {archivos}")