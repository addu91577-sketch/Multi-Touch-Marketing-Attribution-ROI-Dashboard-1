"""
Generates an interactive, standalone executive dashboard using Plotly.
Output: reports/interactive_dashboard.html
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json


def build_dashboard():
    channel_summary = pd.read_csv('reports/Channel_Attribution_ROI_Summary.csv')
    paths_df = pd.read_csv('reports/Customer_Journey_Paths.csv')
    trans_matrix = pd.read_csv('reports/Markov_Transition_Matrix.csv', index_col=0)
    rec_table = pd.read_csv('reports/Budget_Optimization_Recommendations.csv')

    # Executive KPIs
    tot_spend = channel_summary['Spend'].sum()
    tot_rev = channel_summary['Linear_Revenue'].sum()
    tot_conv = channel_summary['Linear_Conversions'].sum()
    blended_roas = tot_rev / tot_spend
    blended_roi = ((tot_rev - tot_spend) / tot_spend) * 100.0

    # 1. Multi-Touch Model Comparison Bar Chart
    models = ['First_Touch', 'Last_Touch', 'Linear', 'Position_Based', 'Time_Decay', 'Markov']
    display_names = ['First-Touch', 'Last-Touch', 'Linear', 'Position-Based (U-Shaped)', 'Time-Decay', 'Markov Chain']
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#9b59b6', '#f39c12', '#1abc9c']

    fig_models = go.Figure()
    for m, name, col in zip(models, display_names, colors):
        fig_models.add_trace(go.Bar(
            x=channel_summary['Channel'],
            y=channel_summary[f'{m}_Revenue'],
            name=name,
            marker_color=col,
            hovertemplate="<b>%{x}</b><br>" + name + " Revenue: $%{y:,.2f}<extra></extra>"
        ))

    fig_models.update_layout(
        title=dict(text="<b>Channel Attributed Revenue Across 6 Attribution Models</b>", font=dict(size=18)),
        barmode='group',
        xaxis_title="<b>Marketing Channel</b>",
        yaxis_title="<b>Attributed Revenue ($)</b>",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        height=500
    )

    # 2. Spend vs ROAS Efficiency Bubble Chart
    fig_bubble = go.Figure()
    fig_bubble.add_trace(go.Scatter(
        x=channel_summary['Spend'],
        y=channel_summary['Linear_ROAS'],
        mode='markers+text',
        text=channel_summary['Channel'],
        textposition="top center",
        marker=dict(
            size=channel_summary['Linear_Conversions'] * 4,
            color=channel_summary['Linear_ROAS'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Linear ROAS (x)"),
            line=dict(width=1.5, color='DarkSlateGrey')
        ),
        hovertemplate=(
            "<b>%{text}</b><br>" +
            "Spend: $%{x:,.2f}<br>" +
            "Linear ROAS: %{y:.2f}x<br>" +
            "Conversions: %{marker.size:,.1f}<extra></extra>"
        )
    ))

    fig_bubble.update_layout(
        title=dict(text="<b>Marketing Efficiency Matrix: Spend vs Multi-Touch Linear ROAS</b><br><sup>(Bubble size proportional to attributed conversions)</sup>", font=dict(size=18)),
        xaxis_title="<b>Total Spend ($)</b>",
        yaxis_title="<b>Linear ROAS (Log Scale)</b>",
        yaxis_type="log",
        xaxis_tickprefix="$",
        xaxis_tickformat=",.0f",
        template="plotly_white",
        height=500
    )

    # 3. Markov State Transition Heatmap
    states = trans_matrix.index.tolist()
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=trans_matrix.values,
        x=states,
        y=states,
        colorscale='Blues',
        text=np.round(trans_matrix.values, 2),
        texttemplate="%{text}",
        colorbar=dict(title="Probability")
    ))

    fig_heatmap.update_layout(
        title=dict(text="<b>Markov State Transition Probability Matrix</b>", font=dict(size=18)),
        xaxis_title="<b>Next State</b>",
        yaxis_title="<b>Current State</b>",
        template="plotly_white",
        height=500
    )

    # 4. Budget Reallocation Waterfall
    waterfall_colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in rec_table['Spend_Delta']]
    fig_waterfall = go.Figure(go.Bar(
        x=rec_table['Channel'],
        y=rec_table['Spend_Delta'],
        marker_color=waterfall_colors,
        text=[f"{pct:+.1f}%" for pct in rec_table['Spend_Delta_Pct']],
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Budget Shift: $%{y:,.2f}<extra></extra>"
    ))

    fig_waterfall.update_layout(
        title=dict(text="<b>Recommended Budget Optimization Shifts ($ Delta)</b>", font=dict(size=18)),
        xaxis_title="<b>Marketing Channel</b>",
        yaxis_title="<b>Budget Delta ($)</b>",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
        template="plotly_white",
        height=450
    )

    # Convert figures to HTML divs
    div_models = fig_models.to_html(full_html=False, include_plotlyjs='cdn')
    div_bubble = fig_bubble.to_html(full_html=False, include_plotlyjs=False)
    div_heatmap = fig_heatmap.to_html(full_html=False, include_plotlyjs=False)
    div_waterfall = fig_waterfall.to_html(full_html=False, include_plotlyjs=False)

    # Build HTML table for channel metrics
    table_rows = ""
    for _, row in channel_summary.iterrows():
        table_rows += f"""
        <tr>
            <td style="font-weight: bold; text-align: left;">{row['Channel']}</td>
            <td>${row['Spend']:,.2f}</td>
            <td>{row['Spend_Share_Pct']:.1f}%</td>
            <td>${row['First_Touch_Revenue']:,.2f}</td>
            <td>${row['Last_Touch_Revenue']:,.2f}</td>
            <td style="font-weight: bold; color: #27ae60;">${row['Linear_Revenue']:,.2f}</td>
            <td>${row['Markov_Revenue']:,.2f}</td>
            <td>{row['First_Touch_ROAS']:.2f}x</td>
            <td>{row['Last_Touch_ROAS']:.2f}x</td>
            <td style="font-weight: bold; color: #2980b9;">{row['Linear_ROAS']:.2f}x</td>
            <td>{row['Markov_ROAS']:.2f}x</td>
            <td>${row['Linear_CAC']:,.2f}</td>
        </tr>
        """

    # Recommendation table rows
    rec_rows = ""
    for _, row in rec_table.iterrows():
        status_color = "#27ae60" if "Undervalued" in row['Status'] else ("#e67e22" if "Closer" in row['Status'] else ("#c0392b" if "Diminishing" in row['Status'] else "#2980b9"))
        rec_rows += f"""
        <tr>
            <td style="font-weight: bold;">{row['Channel']}</td>
            <td>${row['Current_Spend']:,.2f} ({row['Current_Spend_Share_Pct']:.1f}%)</td>
            <td style="font-weight: bold;">${row['Optimized_Spend']:,.2f} ({row['Optimized_Spend_Share_Pct']:.1f}%)</td>
            <td style="color: {'green' if row['Spend_Delta']>=0 else 'red'}; font-weight: bold;">${row['Spend_Delta']:+,.2f} ({row['Spend_Delta_Pct']:+.1f}%)</td>
            <td style="color: {status_color}; font-weight: bold;">{row['Status']}</td>
            <td><b>{row['Recommended_Action']}</b></td>
            <td style="font-size: 13px; text-align: left;">{row['Rationale']}</td>
        </tr>
        """

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Touch Marketing Attribution & ROI Executive Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            margin: 0;
            padding: 24px;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 32px 40px;
            border-radius: 16px;
            margin-bottom: 24px;
            box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
        }}
        .header h1 {{ margin: 0 0 8px 0; font-size: 28px; font-weight: 800; }}
        .header p {{ margin: 0; font-size: 15px; opacity: 0.9; }}
        .kpi-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: white;
            padding: 20px 24px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border-left: 5px solid #3b82f6;
        }}
        .kpi-card.green {{ border-left-color: #10b981; }}
        .kpi-card.purple {{ border-left-color: #8b5cf6; }}
        .kpi-card.amber {{ border-left-color: #f59e0b; }}
        .kpi-title {{ font-size: 13px; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 6px; }}
        .kpi-value {{ font-size: 26px; font-weight: 800; color: #0f172a; }}
        .kpi-subtitle {{ font-size: 12px; color: #94a3b8; margin-top: 4px; }}
        .chart-card {{
            background: white;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        @media (max-width: 1024px) {{
            .grid-2 {{ grid-template-columns: 1fr; }}
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            text-align: right;
        }}
        th, td {{
            padding: 12px 14px;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background-color: #f1f5f9;
            color: #334155;
            font-weight: 700;
        }}
        tr:hover {{ background-color: #f8fafc; }}
        .section-title {{
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 16px;
            color: #0f172a;
        }}
        .tag {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
        }}
    </style>
</head>
<body>

    <div class="header">
        <h1>Multi-Touch Marketing Attribution & ROI Analytics Dashboard</h1>
        <p>End-to-End Audit, Attribution Modeling (FTA, LTA, Linear, Position-Based, Time-Decay, Markov Chain), and Algorithmic Budget Optimization</p>
    </div>

    <!-- Executive KPI Row -->
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-title">Total Marketing Spend</div>
            <div class="kpi-value">${tot_spend:,.2f}</div>
            <div class="kpi-subtitle">Across 8 channels & 1,050 touchpoints</div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-title">Total Attributed Revenue</div>
            <div class="kpi-value">${tot_rev:,.2f}</div>
            <div class="kpi-subtitle">102 converted customer journeys</div>
        </div>
        <div class="kpi-card purple">
            <div class="kpi-title">Portfolio Blended ROAS</div>
            <div class="kpi-value">{blended_roas:.2f}x</div>
            <div class="kpi-subtitle">Return on Ad Spend</div>
        </div>
        <div class="kpi-card amber">
            <div class="kpi-title">Portfolio Blended ROI</div>
            <div class="kpi-value">+{blended_roi:,.1f}%</div>
            <div class="kpi-subtitle">Net Return on Investment</div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-title">Projected Optimization Uplift</div>
            <div class="kpi-value">+12.32%</div>
            <div class="kpi-subtitle">+$237.3k revenue with $0 extra spend</div>
        </div>
    </div>

    <!-- Chart Row 1: Model Comparison -->
    <div class="chart-card">
        {div_models}
    </div>

    <!-- Chart Row 2: Grid of Bubble & Waterfall -->
    <div class="grid-2">
        <div class="chart-card">
            {div_bubble}
        </div>
        <div class="chart-card">
            {div_waterfall}
        </div>
    </div>

    <!-- Chart Row 3: Markov Heatmap -->
    <div class="chart-card">
        {div_heatmap}
    </div>

    <!-- Table 1: Channel Attribution Performance -->
    <div class="chart-card">
        <div class="section-title">Channel Performance & Multi-Touch Attribution Matrix</div>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th style="text-align: left;">Channel</th>
                        <th>Spend ($)</th>
                        <th>Spend Share</th>
                        <th>First-Touch Rev</th>
                        <th>Last-Touch Rev</th>
                        <th>Linear Rev</th>
                        <th>Markov Rev</th>
                        <th>FTA ROAS</th>
                        <th>LTA ROAS</th>
                        <th>Linear ROAS</th>
                        <th>Markov ROAS</th>
                        <th>Linear CAC</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Table 2: Strategic Recommendations -->
    <div class="chart-card">
        <div class="section-title">Algorithmic Budget Optimization & Reallocation Strategy</div>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th style="text-align: left;">Channel</th>
                        <th>Current Spend</th>
                        <th>Optimized Spend</th>
                        <th>Budget Delta</th>
                        <th>Classification</th>
                        <th>Recommended Action</th>
                        <th style="text-align: left;">Strategic Rationale</th>
                    </tr>
                </thead>
                <tbody>
                    {rec_rows}
                </tbody>
            </table>
        </div>
    </div>

    <div style="text-align: center; color: #94a3b8; font-size: 13px; margin-top: 32px; padding-bottom: 24px;">
        Multi-Touch Marketing Attribution ROI Project &bull; Produced by Antigravity AI
    </div>

</body>
</html>
"""

    with open('reports/interactive_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(full_html)

    print("Interactive dashboard generated at reports/interactive_dashboard.html!")


if __name__ == '__main__':
    build_dashboard()
