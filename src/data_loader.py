"""
Data Ingestion, Cleansing, and Journey Sequencing Pipeline
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any


def load_and_preprocess_data(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads marketing touchpoint dataset, parses dates, validates sequences,
    and constructs chronological customer journeys.

    Parameters:
    -----------
    file_path : str
        Path to the CSV file.

    Returns:
    --------
    Tuple[pd.DataFrame, Dict[str, Any]]:
        - Cleaned and sequenced DataFrame with customer-level metrics.
        - Audit dictionary containing dataset health metrics and detected flaws.
    """
    df = pd.read_csv(file_path)
    initial_rows = len(df)

    # 1. Parse and standardize Touchpoint_Date to UTC Datetime
    df['Touchpoint_Date_Parsed'] = pd.to_datetime(df['Touchpoint_Date'], errors='coerce')
    if df['Touchpoint_Date_Parsed'].dt.tz is None:
        df['Touchpoint_Date_UTC'] = df['Touchpoint_Date_Parsed'].dt.tz_localize('UTC')
    else:
        df['Touchpoint_Date_UTC'] = df['Touchpoint_Date_Parsed'].dt.tz_convert('UTC')

    # 2. Check for sequence mismatches in original Touchpoint_Order
    order_mismatches = 0
    if 'Touchpoint_Order' in df.columns:
        for _, group in df.groupby('Customer_ID'):
            original_order = list(group['Touchpoint_Order'])
            sorted_order = list(group.sort_values('Touchpoint_Date_Parsed')['Touchpoint_Order'])
            if original_order != sorted_order:
                order_mismatches += 1

    # 3. Sort strictly chronologically per customer
    # If multiple touchpoints occur on the exact same date, maintain original index or cost order
    df = df.sort_values(by=['Customer_ID', 'Touchpoint_Date_Parsed']).reset_index(drop=True)

    # 4. Re-index true chronological order & journey metrics
    df['Journey_Step'] = df.groupby('Customer_ID').cumcount() + 1
    df['Journey_Length'] = df.groupby('Customer_ID')['Customer_ID'].transform('count')

    # 5. Customer level conversion and revenue aggregation
    # Standardize conversion flag and total revenue across all rows of the customer
    customer_revenue = df.groupby('Customer_ID')['Revenue'].transform('sum')
    customer_converted = df.groupby('Customer_ID')['Conversion_Flag'].transform('max')

    df['Customer_Total_Revenue'] = customer_revenue
    df['Customer_Converted_Flag'] = customer_converted

    # Journey duration in days
    first_dates = df.groupby('Customer_ID')['Touchpoint_Date_Parsed'].transform('min')
    last_dates = df.groupby('Customer_ID')['Touchpoint_Date_Parsed'].transform('max')
    df['Days_From_First_Touch'] = (df['Touchpoint_Date_Parsed'] - first_dates).dt.total_seconds() / (24 * 3600)
    df['Days_To_Conversion'] = (last_dates - df['Touchpoint_Date_Parsed']).dt.total_seconds() / (24 * 3600)
    df['Total_Journey_Days'] = (last_dates - first_dates).dt.total_seconds() / (24 * 3600)

    # Tracking clean-up: Ensure strings are properly capitalized & trimmed
    categorical_cols = ['Channel', 'Touchpoint_Type', 'Device', 'Country', 'Customer_Segment', 'Product_Category']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    audit_summary = {
        'total_rows': initial_rows,
        'unique_customers': df['Customer_ID'].nunique(),
        'total_conversions': int(df[df['Journey_Step'] == 1]['Customer_Converted_Flag'].sum()),
        'overall_conversion_rate': float(df[df['Journey_Step'] == 1]['Customer_Converted_Flag'].mean()),
        'total_revenue': float(df[df['Journey_Step'] == 1]['Customer_Total_Revenue'].sum()),
        'total_marketing_spend': float(df['Cost'].sum()),
        'sequence_mismatches_detected': order_mismatches,
        'unique_channels': df['Channel'].unique().tolist(),
        'date_range': (df['Touchpoint_Date_Parsed'].min().strftime('%Y-%m-%d'),
                       df['Touchpoint_Date_Parsed'].max().strftime('%Y-%m-%d'))
    }

    return df, audit_summary


if __name__ == '__main__':
    df, audit = load_and_preprocess_data('Multi_Touch_Marketing_Attribution_ROI_Dataset.csv')
    print("Preprocessing successful!")
    print("Audit Summary:", audit)
