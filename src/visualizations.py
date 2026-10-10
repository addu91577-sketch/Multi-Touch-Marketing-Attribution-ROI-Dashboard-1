"""
Visualization Suite for Multi-Touch Attribution and Marketing Analytics
Generates Matplotlib/Seaborn and Plotly figures for reporting and dashboarding.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

# Set consistent visual theme
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12


def plot_attribution_model_comparison(
    channel_summary: pd.DataFrame,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plots a multi-model comparison of Attributed Revenue across channels.
    """
    models = ['First_Touch', 'Last_Touch', 'Linear', 'Position_Based', 'Time_Decay', 'Markov']
    display_names = ['First-Touch', 'Last-Touch', 'Linear', 'Position-Based (U)', 'Time-Decay', 'Markov Chain']

    plot_data = []
    for _, row in channel_summary.iterrows():
        ch = row['Channel']
        for m, name in zip(models, display_names):
            plot_data.append({
                'Channel': ch,
                'Model': name,
                'Revenue': row[f'{m}_Revenue']
            })

    pdf = pd.DataFrame(plot_data)

    fig, ax = plt.subplots(figsize=(14, 7))
    palette = sns.color_palette("deep", len(display_names))
    sns.barplot(data=pdf, x='Channel', y='Revenue', hue='Model', palette=palette, ax=ax)

    ax.set_title("Attributed Revenue by Channel Across 6 Multi-Touch Attribution Models", fontweight='bold', pad=15)
    ax.set_ylabel("Attributed Revenue ($)", fontweight='bold')
    ax.set_xlabel("Marketing Channel", fontweight='bold')
    ax.yaxis.set_major_formatter('${x:,.0f}')
    plt.xticks(rotation=20, ha='right')
    ax.legend(title="Attribution Model", bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    return fig


def plot_channel_roas_vs_spend(
    channel_summary: pd.DataFrame,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Bubble chart showing Marketing Spend vs Linear ROAS, with size proportional to conversions.
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    spend = channel_summary['Spend']
    roas = channel_summary['Linear_ROAS']
    conv = channel_summary['Linear_Conversions']
    channels = channel_summary['Channel']

    scatter = ax.scatter(
        spend,
        roas,
        s=conv * 60,
        c=roas,
        cmap='viridis',
        alpha=0.8,
        edgecolors='black',
        linewidth=1.5
    )

    for i, ch in enumerate(channels):
        ax.annotate(
            f"{ch}\n({roas.iloc[i]:.1f}x ROAS)",
            (spend.iloc[i], roas.iloc[i]),
            xytext=(10, 8),
            textcoords='offset points',
            fontsize=10,
            fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)
        )

    ax.set_title("Marketing Efficiency Matrix: Spend vs Multi-Touch Linear ROAS", fontweight='bold', pad=15)
    ax.set_xlabel("Total Channel Spend ($)", fontweight='bold')
    ax.set_ylabel("Return on Ad Spend (ROAS - Multiple)", fontweight='bold')
    ax.xaxis.set_major_formatter('${x:,.0f}')
    ax.set_yscale('log')
    ax.set_yticks([5, 10, 20, 50, 100])
    ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())
    ax.axhline(10, color='red', linestyle='--', alpha=0.5, label='High Efficiency Threshold (10x)')
    ax.legend(loc='upper right')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    return fig


def plot_markov_transition_heatmap(
    transition_matrix: pd.DataFrame,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Heatmap of Markov Chain channel state transition probabilities.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        transition_matrix,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        cbar_kws={'label': 'Transition Probability'},
        linewidths=.5,
        ax=ax
    )
    ax.set_title("Markov State Transition Probability Matrix", fontweight='bold', pad=15)
    ax.set_xlabel("Next State (Destination)", fontweight='bold')
    ax.set_ylabel("Current State (Source)", fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    return fig


def plot_budget_optimization_waterfall(
    rec_table: pd.DataFrame,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plots the proposed spend shifts across channels.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in rec_table['Spend_Delta']]
    bars = ax.bar(rec_table['Channel'], rec_table['Spend_Delta'], color=colors, edgecolor='black', alpha=0.85)

    for bar, pct in zip(bars, rec_table['Spend_Delta_Pct']):
        height = bar.get_height()
        va = 'bottom' if height >= 0 else 'top'
        ax.annotate(f"{pct:+.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3 if height >= 0 else -12),
                    textcoords="offset points",
                    ha='center', va=va, fontweight='bold', fontsize=10)

    ax.axhline(0, color='black', linewidth=1)
    ax.set_title("Recommended Marketing Spend Shift by Channel ($ Delta)", fontweight='bold', pad=15)
    ax.set_ylabel("Budget Delta ($)", fontweight='bold')
    ax.set_xlabel("Marketing Channel", fontweight='bold')
    ax.yaxis.set_major_formatter('${x:,.0f}')
    plt.xticks(rotation=25, ha='right')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    return fig
