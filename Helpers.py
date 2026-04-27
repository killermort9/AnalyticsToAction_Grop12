import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
try:
    import ipywidgets as widgets
except ImportError:
    widgets = None

# All datetime columns in the completed dataset
DATETIME_COLS_COMPLETE = [
    'Dato',
    'Pt ankommet til hospitalet',
    'Planlagt stue klargøring start',
    'Stue klargøring start',
    'Stue klargjort',
    'Patient på stuen (Planlagt)',
    'Patient på stuen',
    'Anæstesistart',
    'Anæstesi melder klar',
    'Procedure start',
    'Procedure slut',
    'Patient klar til afgang',
    'Patient forlader stuen (Planlagt)',
    'Patient forlader stuen',
    'Stue rengjort (Planlagt)',
    'Stue rengøring start',
    'Stue rengjort',
    'I opvågning',
    'Anæstesistop',
    'Klar til udskrivelse efter opvågning',
    'Patient forlader afdeling'
]

def load_clean_data(base_path='../Data and descriptions'):
    '''
    Loads the clean datasets produced by Clean_dataset.ipynb and restores
    all datetime columns to proper datetime types.

    Parameters
    ----------
    base_path : str
        Path to the "Data and descriptions" folder relative to your notebook.
        Default is '../Data and descriptions' which works for all notebooks
        in the AnalyticsToAction_Grop12 folder.

    Returns
    -------
    df_complete : pd.DataFrame
        Clean completed operations dataset with all datetime columns parsed.
    df_cancelled : pd.DataFrame
        Clean cancelled operations dataset with datetime column parsed.

    Example
    -------
    from Helpers import load_clean_data
    df_complete, df_cancelled = load_clean_data()
    '''
    df_complete  = pd.read_csv(f'{base_path}/Case Rigshospitalet - Completed operations.csv',  sep=';', low_memory=False)
    df_cancelled = pd.read_csv(f'{base_path}/Case Rigshospitalet - Cancelled operations.csv', sep=';', low_memory=False)

    # Restore datetime types for completed dataset
    for col in DATETIME_COLS_COMPLETE:
        if col in df_complete.columns:
            df_complete[col] = pd.to_datetime(df_complete[col], errors='coerce')

    # Restore datetime type for cancelled dataset
    if 'Dato og tid' in df_cancelled.columns:
        df_cancelled['Dato og tid'] = pd.to_datetime(df_cancelled['Dato og tid'], errors='coerce')

    return df_complete, df_cancelled

def get_dataframe_by_val_in_key(df,key_name,value):
    '''
    Parameters
    ----
    df : pandas dataframe
        Dataframe to sort
    key_name : string
        string of key name, that is to be sorted by
    value : ?
        the value of the key that we wish to extract

    Output: dataframe consisting of only entries with that value for the specific key
    '''
    return df[df[key_name] == value]

def df_of_Operationsgang_and_Dato(df, target_gang = None, target_dato = None):
    '''
    Parameters
    ---
    df : pandas dataframe
        Dataframe to sort
    target_gang : integer
        An integer representing the Operationsgang ID
    target_dato : pandas timestamp object
        A pandas timestamp defined only on the date (Example: pd.Timestamp("2024-03-07"))
    '''
    ops_id_num = pd.to_numeric(df["Operationsgang ID"], errors="coerce")
    dato_norm = pd.to_datetime(df["Dato"], errors="coerce").dt.normalize()

    mask = ((ops_id_num == target_gang) if target_gang != None else 1) & ((dato_norm == target_dato) if target_dato != None else 1)
    df_gang_dato = df.loc[mask].copy()
    return df_gang_dato

def df_of_Stue_and_Dato(df, target_stue=None, target_dato=None):
    '''
    Parameters
    ---
    df : pandas dataframe
        Dataframe to sort
    target_stue : string
        A string describing the name of a stue
    target_dato : pandas timestamp object
        A pandas timestamp defined only on the date (Example: pd.Timestamp("2024-03-07"))
    '''
    # Normalize types to avoid date/Timestamp mismatches
    stue_key = df["Stue"].astype(str).str.strip()
    dato_key = pd.to_datetime(df["Dato"], errors="coerce").dt.normalize() 

    target_stue_key = str(target_stue).strip() if target_stue != None else None
    target_dato_key = pd.to_datetime(target_dato, errors="coerce").normalize() if target_dato != None else None

    mask = ((stue_key == target_stue_key) if target_stue != None else 1) & ((dato_key == target_dato_key) if target_dato != None else 1)
    return df.loc[mask].copy()



def plot_forsinkelse_for_speciale(speciale):
    if speciale == "Alle":
        plot_df = tid_df
    else:
        plot_df = tid_df[tid_df["Speciale"] == speciale]

    stats = (
        plot_df.groupby("Start-time")["Individuel forsinkelse"]
        .agg(
            mean="mean",
            q1=lambda s: s.quantile(0.25),
            q3=lambda s: s.quantile(0.75)
        )
        .sort_index()
    )

    if stats.empty:
        print(f"Ingen data for Speciale = {speciale}")
        return

    timer = stats.index.to_numpy()
    mean_vals = stats["mean"].to_numpy()
    q1_vals = stats["q1"].to_numpy()
    q3_vals = stats["q3"].to_numpy()

    plot_to_index = 16

    plt.figure(figsize=(14, 5))
    plt.fill_between(timer[:plot_to_index], q1_vals[:plot_to_index], q3_vals[:plot_to_index], alpha=0.25, label="1. og 3. kvartil")
    plt.plot(timer[:plot_to_index], mean_vals[:plot_to_index], marker="o", linewidth=2, label="Gennemsnit")
    plt.title(f"Individuel forsinkelse som funktion af tidspunkt på dagen - {speciale}")
    plt.xlabel("Procedure start (time of day)")
    plt.ylabel("Individuel forsinkelse (minutter)")
    plt.xticks(timer[:plot_to_index], [f"{int(t):02d}:00" for t in timer[:plot_to_index]], rotation=45)
    plt.grid(axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_planned_operations_throughout_the_day_for_speciale(speciale):
    if speciale == "Alle":
        df_in_question = df_complete_NotAkut
    else:
        df_in_question = df_complete_NotAkut[df_complete_NotAkut["Speciale"] == speciale].copy()

    df_in_question = df_in_question.dropna(subset=["Procedure start"])
    df_in_question["Start-time"] = df_in_question["Procedure start"].dt.hour

    counts = (
        df_in_question["Start-time"]
        .value_counts()
        .reindex(range(24), fill_value=0)
        .sort_index()
    )

    counts_df = pd.DataFrame({
        "Time": [f"{h:02d}:00" for h in counts.index],
        "Count": counts.values,
    })
    counts_df["Share (%)"] = (counts_df["Count"] / counts_df["Count"].sum() * 100).round(2)

    plt.figure(figsize=(14, 4))
    plt.bar(counts_df["Time"], counts_df["Count"])
    plt.title("Øjenkirurgi operations by time of day")
    plt.xlabel("Procedure start (hour)")
    plt.ylabel("Number of operations")
    plt.xticks(rotation=45)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()
    return None