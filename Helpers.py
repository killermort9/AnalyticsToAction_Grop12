import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
try:
    import ipywidgets as widgets
except ImportError:
    widgets = None

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