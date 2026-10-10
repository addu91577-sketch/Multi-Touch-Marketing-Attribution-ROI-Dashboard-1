"""
Financial Performance, ROI, ROAS, CAC, and Budget Optimization Analytics
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List


MODELS = ['First_Touch', 'Last_Touch', 'Linear', 'Position_Based', 'Time_Decay', 'Markov']


def calculate_channel_performance(
    df: pd.DataFrame,
    markov_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Computes comprehensive channel-level performance metrics across all 6 attribution models.

    Metrics computed per channel & model:
    - Total Spend (Cost)
    - Touchpoint Count (Volume)
    - Attributed Conversions
    - Attributed Revenue
    - Attributed Net Profit (Revenue - Spend)
    - ROAS (Revenue / Spend)
    - ROI % ((Net Profit / Spend) * 100)
    - CAC (Spend / Attributed Conversions)
    """
    summary = df.groupby('Channel').agg(
        Spend=('Cost', 'sum'),
        Touchpoints=('Journey_Step', 'count')
    ).reset_index()

    # Calculate model metrics
    for m in MODELS:
        conv_col = f'Conv_{m}'
        rev_col = f'Rev_{m}'

        model_agg = df.groupby('Channel').agg(
            **{
                f'{m}_Conversions': (conv_col, 'sum'),
                f'{m}_Revenue': (rev_col, 'sum')
            }
        ).reset_index()

        summary = summary.merge(model_agg, on='Channel', how='left')

        # Financial derived metrics
        summary[f'{m}_Net_Profit'] = summary[f'{m}_Revenue'] - summary['Spend']
        summary[f'{m}_ROAS'] = summary[f'{m}_Revenue'] / summary['Spend']
        summary[f'{m}_ROI_Pct'] = (summary[f'{m}_Net_Profit'] / summary['Spend']) * 100.0
        summary[f'{m}_CAC'] = np.where(
            summary[f'{m}_Conversions'] > 0,
            summary['Spend'] / summary[f'{m}_Conversions'],
            0.0
        )

    # Calculate share of total budget
    total_spend = summary['Spend'].sum()
    summary['Spend_Share_Pct'] = (summary['Spend'] / total_spend) * 100.0

    return summary


def calculate_journey_path_performance(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Analyzes customer journey paths, conversion rates, and total revenue by path sequence.
    """
    paths_data = []
    for cid, group in df.groupby('Customer_ID'):
        path_str = " -> ".join(group['Channel'])
        conv = group['Customer_Converted_Flag'].iloc[0]
        rev = group['Customer_Total_Revenue'].iloc[0]
        length = group['Journey_Length'].iloc[0]
        days = group['Total_Journey_Days'].iloc[0]
        paths_data.append({
            'Customer_ID': cid,
            'Path': path_str,
            'Converted': conv,
            'Revenue': rev,
            'Path_Length': length,
            'Journey_Days': days
        })

    paths_df = pd.DataFrame(paths_data)

    agg_paths = paths_df.groupby('Path').agg(
        Total_Customers=('Customer_ID', 'count'),
        Conversions=('Converted', 'sum'),
        Total_Revenue=('Revenue', 'sum'),
        Avg_Path_Length=('Path_Length', 'mean'),
        Avg_Journey_Days=('Journey_Days', 'mean')
    ).reset_index()

    agg_paths['Conversion_Rate_Pct'] = (agg_paths['Conversions'] / agg_paths['Total_Customers']) * 100.0
    agg_paths['Revenue_Per_Customer'] = agg_paths['Total_Revenue'] / agg_paths['Total_Customers']

    return agg_paths.sort_values(by=['Conversions', 'Total_Customers'], ascending=False).head(top_n)


def generate_budget_optimization_recommendations(
    channel_summary: pd.DataFrame
) -> Dict[str, Any]:
    """
    Evaluates marketing channels by comparing First-Touch, Last-Touch, Linear, and Markov ROI.
    Generates strategic budget reallocation recommendations and simulates potential revenue impact.
    """
    rec_list = []
    total_budget = channel_summary['Spend'].sum()

    for _, row in channel_summary.iterrows():
        channel = row['Channel']
        spend = row['Spend']
        spend_share = row['Spend_Share_Pct']
        last_roas = row['Last_Touch_ROAS']
        linear_roas = row['Linear_ROAS']
        markov_roas = row['Markov_ROAS']
        first_roas = row['First_Touch_ROAS']

        # Discrepancy analysis: Last Touch vs Multi-Touch / First Touch
        lta_vs_linear_diff = ((linear_roas - last_roas) / last_roas) * 100.0
        first_vs_last_diff = ((first_roas - last_roas) / last_roas) * 100.0

        if first_roas > 20.0 and last_roas < 10.0:
            status = "Heavily Undervalued (Top-Funnel Initiator)"
            action = "Scale Budget (+25% to +40%)"
            rationale = (f"Drives substantial customer acquisition (First-Touch ROAS {first_roas:.1f}x) "
                         f"that is obscured by single-touch Last-Click models ({last_roas:.1f}x).")
            proposed_multiplier = 1.30
        elif last_roas > 40.0 and first_roas < 15.0:
            status = "Conversion Closer (Bottom-Funnel Accelerator)"
            action = "Protect / Optimize Retention Flow"
            rationale = (f"Dominant closer with {last_roas:.1f}x Last-Touch ROAS. Maintain seamless conversion "
                         f"funnels while relying on top-funnel channels for feeder traffic.")
            proposed_multiplier = 1.15
        elif spend_share > 25.0 and markov_roas < 5.0:
            status = "Over-budgeted / Marginal Diminishing Returns"
            action = "Reallocate / Trim Budget (-15% to -25%)"
            rationale = (f"Absorbs {spend_share:.1f}% of budget, but multi-touch Markov ROAS is {markov_roas:.1f}x. "
                         f"Shift marginal dollars to higher-ROAS top-funnel channels.")
            proposed_multiplier = 0.80
        elif linear_roas > 10.0 and spend_share < 10.0:
            status = "High-Efficiency Nurturer (Under-invested)"
            action = "Scale Budget (+15% to +30%)"
            rationale = (f"Exceptional multi-touch efficiency (Linear ROAS {linear_roas:.1f}x) with only "
                         f"{spend_share:.1f}% budget share.")
            proposed_multiplier = 1.25
        else:
            status = "Balanced Performer"
            action = "Maintain Budget with Creative Optimization"
            rationale = f"Steady cross-funnel contributor with {linear_roas:.1f}x multi-touch ROAS."
            proposed_multiplier = 1.00

        rec_list.append({
            'Channel': channel,
            'Current_Spend': spend,
            'Current_Spend_Share_Pct': spend_share,
            'Status': status,
            'Recommended_Action': action,
            'Rationale': rationale,
            'Proposed_Multiplier': proposed_multiplier,
            'Proposed_Spend': spend * proposed_multiplier
        })

    rec_df = pd.DataFrame(rec_list)

    # Normalize proposed spend to keep overall budget constant
    proposed_total = rec_df['Proposed_Spend'].sum()
    rec_df['Optimized_Spend'] = (rec_df['Proposed_Spend'] / proposed_total) * total_budget
    rec_df['Optimized_Spend_Share_Pct'] = (rec_df['Optimized_Spend'] / total_budget) * 100.0
    rec_df['Spend_Delta'] = rec_df['Optimized_Spend'] - rec_df['Current_Spend']
    rec_df['Spend_Delta_Pct'] = ((rec_df['Optimized_Spend'] - rec_df['Current_Spend']) / rec_df['Current_Spend']) * 100.0

    # Projected revenue under multi-touch linear/markov efficiency
    blended_roas_map = dict(zip(channel_summary['Channel'], channel_summary['Linear_ROAS']))
    rec_df['Projected_Revenue'] = rec_df['Optimized_Spend'] * rec_df['Channel'].map(blended_roas_map)
    current_linear_revenue = (channel_summary['Spend'] * channel_summary['Linear_ROAS']).sum()
    projected_total_revenue = rec_df['Projected_Revenue'].sum()
    projected_uplift = projected_total_revenue - current_linear_revenue
    projected_uplift_pct = (projected_uplift / current_linear_revenue) * 100.0

    return {
        'recommendations_table': rec_df[[
            'Channel', 'Current_Spend', 'Current_Spend_Share_Pct',
            'Optimized_Spend', 'Optimized_Spend_Share_Pct', 'Spend_Delta',
            'Spend_Delta_Pct', 'Status', 'Recommended_Action', 'Rationale'
        ]],
        'current_revenue': current_linear_revenue,
        'projected_revenue': projected_total_revenue,
        'projected_uplift': projected_uplift,
        'projected_uplift_pct': projected_uplift_pct
    }
