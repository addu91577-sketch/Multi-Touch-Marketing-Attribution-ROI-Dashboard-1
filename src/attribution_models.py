"""
Multi-Touch Marketing Attribution Modeling Engine
Implements:
1. First-Touch Attribution (FTA)
2. Last-Touch Attribution (LTA)
3. Linear Attribution (LA)
4. Time-Decay Attribution (TDA)
5. Position-Based (U-Shaped) Attribution (PBA)
6. Markov Chain Data-Driven Attribution (MCA)
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from typing import Tuple, Dict


def calculate_first_touch(df: pd.DataFrame) -> pd.DataFrame:
    """
    First-Touch Attribution:
    Assigns 100% of conversion credit and revenue to the initial touchpoint.
    """
    df = df.copy()
    is_first = (df['Journey_Step'] == 1) & (df['Customer_Converted_Flag'] == 1)
    df['Weight_First_Touch'] = np.where(is_first, 1.0, 0.0)
    df['Rev_First_Touch'] = df['Weight_First_Touch'] * df['Customer_Total_Revenue']
    df['Conv_First_Touch'] = df['Weight_First_Touch']
    return df


def calculate_last_touch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Last-Touch Attribution:
    Assigns 100% of conversion credit and revenue to the final converting touchpoint.
    """
    df = df.copy()
    is_last = (df['Journey_Step'] == df['Journey_Length']) & (df['Customer_Converted_Flag'] == 1)
    df['Weight_Last_Touch'] = np.where(is_last, 1.0, 0.0)
    df['Rev_Last_Touch'] = df['Weight_Last_Touch'] * df['Customer_Total_Revenue']
    df['Conv_Last_Touch'] = df['Weight_Last_Touch']
    return df


def calculate_linear(df: pd.DataFrame) -> pd.DataFrame:
    """
    Linear Attribution:
    Assigns equal credit to every touchpoint along the customer journey.
    """
    df = df.copy()
    df['Weight_Linear'] = np.where(
        df['Customer_Converted_Flag'] == 1,
        1.0 / df['Journey_Length'],
        0.0
    )
    df['Rev_Linear'] = df['Weight_Linear'] * df['Customer_Total_Revenue']
    df['Conv_Linear'] = df['Weight_Linear']
    return df


def calculate_position_based(
    df: pd.DataFrame,
    first_weight: float = 0.4,
    last_weight: float = 0.4
) -> pd.DataFrame:
    """
    Position-Based (U-Shaped) Attribution:
    Assigns first_weight (default 40%) to the first touch,
    last_weight (default 40%) to the last touch,
    and splits the remainder (20%) equally across middle touchpoints.
    """
    df = df.copy()
    middle_weight = max(0.0, 1.0 - (first_weight + last_weight))

    def get_weight(row):
        if row['Customer_Converted_Flag'] == 0:
            return 0.0
        n = row['Journey_Length']
        k = row['Journey_Step']
        if n == 1:
            return 1.0
        elif n == 2:
            return 0.5
        else:
            if k == 1:
                return first_weight
            elif k == n:
                return last_weight
            else:
                return middle_weight / (n - 2)

    df['Weight_Position_Based'] = df.apply(get_weight, axis=1)
    df['Rev_Position_Based'] = df['Weight_Position_Based'] * df['Customer_Total_Revenue']
    df['Conv_Position_Based'] = df['Weight_Position_Based']
    return df


def calculate_time_decay(
    df: pd.DataFrame,
    half_life_days: float = 7.0
) -> pd.DataFrame:
    """
    Time-Decay Attribution:
    Weights decay exponentially as the time distance from conversion increases.
    Formula: weight = 2^(-delta_days / half_life_days)
    Weights are normalized per customer to sum to 1.0.
    """
    df = df.copy()
    raw_decay = np.where(
        df['Customer_Converted_Flag'] == 1,
        2.0 ** (-df['Days_To_Conversion'] / half_life_days),
        0.0
    )
    df['Raw_Decay'] = raw_decay
    customer_decay_sum = df.groupby('Customer_ID')['Raw_Decay'].transform('sum')

    df['Weight_Time_Decay'] = np.where(
        customer_decay_sum > 0,
        df['Raw_Decay'] / customer_decay_sum,
        0.0
    )
    df = df.drop(columns=['Raw_Decay'])
    df['Rev_Time_Decay'] = df['Weight_Time_Decay'] * df['Customer_Total_Revenue']
    df['Conv_Time_Decay'] = df['Weight_Time_Decay']
    return df


def calculate_markov_chain_attribution(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Data-Driven Algorithmic Attribution using Absorbing Markov Chains:
    - Builds state transition graph across channels, start, and end states.
    - Calculates baseline conversion rate using fundamental matrix.
    - Computes Removal Effects for each channel by simulating channel removal.
    - Normalizes removal effects to compute Markov weights, conversions, and revenues.

    Returns:
    --------
    Tuple[pd.DataFrame, Dict[str, Any]]:
        - DataFrame containing channel Markov weights and metrics.
        - Transition matrix dictionary and diagnostic data.
    """
    channels = sorted(df['Channel'].unique())

    # Build sequence paths for each customer
    paths = []
    for _, group in df.groupby('Customer_ID'):
        ch_seq = list(group['Channel'])
        conv = group['Customer_Converted_Flag'].iloc[0]
        end_state = '(conversion)' if conv == 1 else '(null)'
        paths.append(['(start)'] + ch_seq + [end_state])

    def solve_markov(paths_list, removed_channel=None):
        counts = defaultdict(lambda: defaultdict(int))
        for p in paths_list:
            filtered_p = []
            for s in p:
                if s == removed_channel:
                    filtered_p.append('(null)')
                    break
                else:
                    filtered_p.append(s)
            for i in range(len(filtered_p) - 1):
                counts[filtered_p[i]][filtered_p[i+1]] += 1
                if filtered_p[i+1] in ['(conversion)', '(null)']:
                    break

            transient = ['(start)'] + [c for c in channels if c != removed_channel]
            absorbing = ['(conversion)', '(null)']

        Q = pd.DataFrame(0.0, index=transient, columns=transient)
        R = pd.DataFrame(0.0, index=transient, columns=absorbing)

        for s in transient:
            tot = sum(counts[s].values())
            if tot > 0:
                for nxt, cnt in counts[s].items():
                    if nxt in transient:
                        Q.loc[s, nxt] = cnt / tot
                    elif nxt in absorbing:
                        R.loc[s, nxt] = cnt / tot
            else:
                R.loc[s, '(null)'] = 1.0

        I = np.eye(len(transient))
        try:
            N = np.linalg.inv(I - Q.values)
            B = np.dot(N, R.values)
            B_df = pd.DataFrame(B, index=transient, columns=absorbing)
            return float(B_df.loc['(start)', '(conversion)'])
        except np.linalg.LinAlgError:
            return 0.0

    # 1. Baseline conversion probability
    baseline_conv = solve_markov(paths)

    # 2. Channel removal effects
    removal_effects = {}
    for c in channels:
        conv_without = solve_markov(paths, removed_channel=c)
        re = 1.0 - (conv_without / baseline_conv) if baseline_conv > 0 else 0.0
        removal_effects[c] = max(0.0, float(re))

    total_re = sum(removal_effects.values())
    markov_weights = {c: (re / total_re if total_re > 0 else 1.0 / len(channels))
                      for c, re in removal_effects.items()}

    total_conversions = float(df[df['Journey_Step'] == 1]['Customer_Converted_Flag'].sum())
    total_revenue = float(df[df['Journey_Step'] == 1]['Customer_Total_Revenue'].sum())

    markov_summary = []
    for c in channels:
        w = markov_weights[c]
        re = removal_effects[c]
        markov_summary.append({
            'Channel': c,
            'Removal_Effect': re,
            'Markov_Weight': w,
            'Conv_Markov': w * total_conversions,
            'Rev_Markov': w * total_revenue
        })

    markov_df = pd.DataFrame(markov_summary)

    # Calculate full transition probability matrix for visualization
    all_states = ['(start)'] + channels + ['(conversion)', '(null)']
    full_counts = defaultdict(lambda: defaultdict(int))
    for p in paths:
        for i in range(len(p) - 1):
            full_counts[p[i]][p[i+1]] += 1

    trans_matrix = pd.DataFrame(0.0, index=all_states, columns=all_states)
    for s1 in all_states:
        if s1 in full_counts:
            tot = sum(full_counts[s1].values())
            for s2, cnt in full_counts[s1].items():
                trans_matrix.loc[s1, s2] = cnt / tot if tot > 0 else 0.0
        elif s1 in ['(conversion)', '(null)']:
            trans_matrix.loc[s1, s1] = 1.0

    diagnostics = {
        'baseline_conversion_rate': baseline_conv,
        'transition_matrix': trans_matrix,
        'removal_effects': removal_effects,
        'markov_weights': markov_weights
    }

    return markov_df, diagnostics


def apply_all_attribution_models(
    df: pd.DataFrame,
    half_life_days: float = 7.0
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Executes and binds all 6 attribution models to the dataset.
    """
    df = calculate_first_touch(df)
    df = calculate_last_touch(df)
    df = calculate_linear(df)
    df = calculate_position_based(df)
    df = calculate_time_decay(df, half_life_days=half_life_days)

    markov_df, diagnostics = calculate_markov_chain_attribution(df)

    # Attach Markov revenue and conversions at row level proportional to linear share
    markov_weight_map = dict(zip(markov_df['Channel'], markov_df['Markov_Weight']))
    df['Markov_Channel_Weight'] = df['Channel'].map(markov_weight_map)

    # Normalize customer level Markov weights
    cust_m_sum = df.groupby('Customer_ID')['Markov_Channel_Weight'].transform('sum')
    df['Weight_Markov'] = np.where(
        (df['Customer_Converted_Flag'] == 1) & (cust_m_sum > 0),
        df['Markov_Channel_Weight'] / cust_m_sum,
        0.0
    )
    df['Rev_Markov'] = df['Weight_Markov'] * df['Customer_Total_Revenue']
    df['Conv_Markov'] = df['Weight_Markov']

    # Attributed profit and ROI columns for all models
    models = ['First_Touch', 'Last_Touch', 'Linear', 'Position_Based', 'Time_Decay', 'Markov']
    for m in models:
        df[f'Profit_{m}'] = df[f'Rev_{m}'] - df['Cost']
        df[f'ROI_{m}'] = np.where(
            df['Cost'] > 0,
            (df[f'Profit_{m}'] / df['Cost']) * 100.0,
            0.0
        )

    return df, markov_df, diagnostics
