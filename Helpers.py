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
    df_complete  = pd.read_csv(f'{base_path}/clean_complete.csv',  sep=';', low_memory=False)
    df_cancelled = pd.read_csv(f'{base_path}/clean_cancelled.csv', sep=';', low_memory=False)

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

def df_of_Operationsgang_and_Dato(df, target_gang, target_dato):
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

    mask = (ops_id_num == target_gang) & (dato_norm == target_dato)
    df_gang_dato = df.loc[mask].copy()
    return df_gang_dato

def df_of_Stue_and_Dato(df, target_stue, target_dato):
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

    target_stue_key = str(target_stue).strip()
    target_dato_key = pd.to_datetime(target_dato, errors="coerce").normalize()

    mask = (stue_key == target_stue_key) & (dato_key == target_dato_key)
    return df.loc[mask].copy()