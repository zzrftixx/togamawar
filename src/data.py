import pandas as pd
import os
from datetime import datetime

DATA_FILE = "attendance_data.csv"

def load_data():
    """Loads the attendance data from CSV. Creates it if it doesn't exist."""
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=[
            "date", "month_name", "week_number", "day_name", 
            "name", "is_present", "notes", "fine", "timestamp"
        ])
    try:
        return pd.read_csv(DATA_FILE)
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=[
            "date", "month_name", "week_number", "day_name", 
            "name", "is_present", "notes", "fine", "timestamp"
        ])

def save_entry(entries):
    """
    Saves a list of entries to the CSV file.
    entries: list of dictionaries
    """
    df = load_data()
    new_df = pd.DataFrame(entries)
    
    # Simple append approach for now, usually we might want to overwrite if same day/person exists
    # But for simplicity, we just append and user can manage downstream or we clean up later
    # Better approach: remove existing entries for the same context if replacing
    
    # We essentially want to update: if date + name exists, update it.
    
    combined_df = pd.concat([df, new_df], ignore_index=True)
    
    # Deduplicate: keep last entry for (date, name)
    combined_df.drop_duplicates(subset=["date", "name"], keep="last", inplace=True)
    
    combined_df.to_csv(DATA_FILE, index=False)
    return True

def get_monthly_summary(month_name):
    """Returns a filtered dataframe for the given month."""
    df = load_data()
    if df.empty:
        return df
    return df[df["month_name"] == month_name]
