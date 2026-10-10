"""
Generates the interactive, standalone executive dashboard using Plotly.js.
Outputs:
  - index.html (Root entrypoint for GitHub Pages)
  - dashboard/index.html
"""

import os
import json
import pandas as pd
import numpy as np


def build_dashboard():
    os.makedirs('dashboard', exist_ok=True)

    df_ch = pd.read_csv('reports/Channel_Attribution_ROI_Summary.csv')
    df_paths = pd.read_csv('reports/Customer_Journey_Paths.csv')
    df_recs = pd.read_csv('reports/Budget_Optimization_Recommendations.csv')
    df_mat = pd.read_csv('reports/Markov_Transition_Matrix.csv', index_col=0)

    channels_json = json.dumps(df_ch.to_dict(orient='records'))
    paths_json = json.dumps(df_paths.head(15).to_dict(orient='records'))
    recs_json = json.dumps(df_recs.to_dict(orient='records'))
    matrix_json = json.dumps({
        'states': df_mat.index.tolist(),
        'matrix': df_mat.values.tolist()
    })

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Touch Marketing Attribution & ROI Executive Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        :root {{
            --primary: #1e40af;
            --primary-dark: #1e3a8a;
            --accent: #3b82f6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}

        body {{
            background-color: var(--bg);
            color: var(--text-main);
            padding: 24px;
            line-height: 1.5;
        }}

        .container {{
            max-width: 1440px;
            margin: 0 auto;
        }}

        .header {{
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
            color: white;
            padding: 32px 36px;
            border-radius: 18px;
            margin-bottom: 24px;
            box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .header-content h1 {{
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 8px;
        }}

        .header-content p {{
            font-size: 15px;
            opacity: 0.9;
            max-width: 800px;
        }}

        .badge {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 700;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}

        .toolbar {{
            background: var(--card-bg);
            padding: 18px 24px;
            border-radius: 14px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
            border: 1px solid var(--border);
        }}

        .toolbar-title {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .model-buttons {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .btn-model {{
            background: #f1f5f9;
            color: #475569;
            border: 1px solid var(--border);
            padding: 10px 18px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .btn-model:hover {{
            background: #e2e8f0;
            color: var(--text-main);
        }}

        .btn-model.active {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
            margin-bottom: 24px;
        }}

        .kpi-card {{
            background: var(--card-bg);
            padding: 22px 24px;
            border-radius: 14px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
            border: 1px solid var(--border);
            border-left: 5px solid var(--primary);
            transition: transform 0.2s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
        }}

        .kpi-card.green {{ border-left-color: var(--success); }}
        .kpi-card.purple {{ border-left-color: #8b5cf6; }}
        .kpi-card.amber {{ border-left-color: var(--warning); }}

        .kpi-label {{
            font-size: 13px;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--text-muted);
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-size: 28px;
            font-weight: 800;
            color: var(--text-main);
            letter-spacing: -0.5px;
        }}

        .kpi-sub {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
        }}

        .chart-card {{
            background: var(--card-bg);
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
            border: 1px solid var(--border);
            margin-bottom: 24px;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
        }}

        .card-title {{
            font-size: 18px;
            font-weight: 800;
            color: var(--text-main);
        }}

        .card-desc {{
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 2px;
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }}

        @media (max-width: 1024px) {{
            .grid-2 {{ grid-template-columns: 1fr; }}
        }}

        .sim-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}

        .sim-channel {{
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
        }}

        .sim-channel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .sim-channel-name {{
            font-weight: 700;
            font-size: 14px;
        }}

        .sim-channel-spend {{
            font-size: 13px;
            color: var(--primary);
            font-weight: 700;
        }}

        .sim-slider {{
            width: 100%;
            cursor: pointer;
        }}

        .sim-slider-val {{
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 4px;
        }}

        .table-wrap {{
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            text-align: right;
            background: white;
        }}

        th, td {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--border);
        }}

        th {{
            background: #f1f5f9;
            color: #334155;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }}

        tr:hover td {{
            background: #f8fafc;
        }}

        .status-pill {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
        }}

        .pill-green {{ background: #dcfce7; color: #15803d; }}
        .pill-blue {{ background: #dbeafe; color: #1e40af; }}
        .pill-red {{ background: #fee2e2; color: #b91c1c; }}

        footer {{
            text-align: center;
            color: var(--text-muted);
            font-size: 13px;
            padding: 32px 0 16px 0;
        }}
    </style>
</head>
<body>

    <div class="container">
        <div class="header">
            <div class="header-content">
                <span class="badge">Enterprise Analytics Engine</span>
                <h1 style="margin-top: 8px;">Multi-Touch Marketing Attribution & ROI Dashboard</h1>
                <p>Auditing 1,050 omnichannel interactions across 300 customers with 6 algorithmic attribution models, conversion path analysis, and budget optimization simulation.</p>
            </div>
            <div>
                <a href="https://github.com/addu91577-sketch/Multi-Touch-Marketing-Attribution-ROI-Dashboard-1" target="_blank" style="text-decoration: none;">
                    <span class="badge" style="background: white; color: #0f172a; cursor: pointer;">GitHub Repository ↗</span>
                </a>
            </div>
        </div>

        <div class="toolbar">
            <div class="toolbar-title">Active Attribution Model:</div>
            <div class="model-buttons" id="model-buttons">
                <button class="btn-model active" onclick="switchModel('Linear')">Linear Attribution</button>
                <button class="btn-model" onclick="switchModel('First_Touch')">First-Touch (FTA)</button>
                <button class="btn-model" onclick="switchModel('Last_Touch')">Last-Touch (LTA)</button>
                <button class="btn-model" onclick="switchModel('Position_Based')">Position-Based (U-Shaped)</button>
                <button class="btn-model" onclick="switchModel('Time_Decay')">Time-Decay (7-Day)</button>
                <button class="btn-model" onclick="switchModel('Markov')">Markov Chain (Data-Driven)</button>
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Total Marketing Spend</div>
                <div class="kpi-value" id="kpi-spend">$173,734.22</div>
                <div class="kpi-sub">Across 8 channels & 1,050 touchpoints</div>
            </div>
            <div class="kpi-card green">
                <div class="kpi-label"><span id="kpi-model-name">Linear</span> Attributed Revenue</div>
                <div class="kpi-value" id="kpi-rev">$1,926,331.12</div>
                <div class="kpi-sub">102 converting customer journeys</div>
            </div>
            <div class="kpi-card purple">
                <div class="kpi-label">Attributed ROAS</div>
                <div class="kpi-value" id="kpi-roas">11.09x</div>
                <div class="kpi-sub">Return on Ad Spend multiple</div>
            </div>
            <div class="kpi-card amber">
                <div class="kpi-label">Attributed Net Profit</div>
                <div class="kpi-value" id="kpi-profit">$1,752,596.90</div>
                <div class="kpi-sub">Portfolio Net ROI: +1,008.8%</div>
            </div>
            <div class="kpi-card green">
                <div class="kpi-label">Budget Optimization Uplift</div>
                <div class="kpi-value" id="kpi-uplift">+12.32%</div>
                <div class="kpi-sub">+$237.3K revenue with $0 extra spend</div>
            </div>
        </div>

        <div class="chart-card">
            <div class="card-header">
                <div>
                    <div class="card-title">Attributed Revenue by Channel (<span id="chart-model-label">Linear</span> vs Portfolio)</div>
                    <div class="card-desc">Compares channel revenue attribution under the selected model vs total marketing spend</div>
                </div>
            </div>
            <div id="chart-channel-revenue" style="height: 440px;"></div>
        </div>

        <div class="grid-2">
            <div class="chart-card">
                <div class="card-header">
                    <div>
                        <div class="card-title">Marketing Efficiency Matrix</div>
                        <div class="card-desc">Spend vs Return on Ad Spend (Bubble size = Attributed Conversions)</div>
                    </div>
                </div>
                <div id="chart-bubble" style="height: 420px;"></div>
            </div>

            <div class="chart-card">
                <div class="card-header">
                    <div>
                        <div class="card-title">Markov State Transition Matrix</div>
                        <div class="card-desc">Probabilistic movement across customer touchpoints and absorbing states</div>
                    </div>
                </div>
                <div id="chart-heatmap" style="height: 420px;"></div>
            </div>
        </div>

        <div class="chart-card">
            <div class="card-header">
                <div>
                    <div class="card-title">Interactive What-If Budget Simulator</div>
                    <div class="card-desc">Adjust channel marketing spend (-50% to +50%) and observe projected portfolio revenue uplift</div>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 13px; color: var(--text-muted);">Simulated Revenue: </span>
                    <span id="sim-total-rev" style="font-size: 20px; font-weight: 800; color: #10b981;">$1,926,331.12</span>
                    <span id="sim-uplift-badge" class="status-pill pill-green" style="margin-left: 8px;">+0.0%</span>
                </div>
            </div>
            <div class="sim-grid" id="sim-sliders-container"></div>
        </div>

        <div class="chart-card">
            <div class="card-header">
                <div>
                    <div class="card-title">Channel Performance & Multi-Touch Attribution Matrix</div>
                    <div class="card-desc">Spend, Conversions, Attributed Revenue, ROAS, ROI %, and CAC across all 8 channels</div>
                </div>
            </div>
            <div class="table-wrap">
                <table id="channel-table">
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
                    <tbody id="channel-table-body"></tbody>
                </table>
            </div>
        </div>

        <div class="chart-card">
            <div class="card-header">
                <div>
                    <div class="card-title">Top Converting Customer Journey Paths</div>
                    <div class="card-desc">Most frequent multi-touch sequences, customer cohorts, conversion rates, and revenue</div>
                </div>
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th style="text-align: left;">Customer Journey Sequence</th>
                            <th>Customers</th>
                            <th>Conversions</th>
                            <th>Conv. Rate (%)</th>
                            <th>Avg Touchpoints</th>
                            <th>Total Revenue</th>
                        </tr>
                    </thead>
                    <tbody id="paths-table-body"></tbody>
                </table>
            </div>
        </div>

        <footer>
            Multi-Touch Marketing Attribution & ROI Optimization Project &bull; Built with Plotly & Python &bull; Open Source under MIT License
        </footer>
    </div>

    <script>
        const channelData = {channels_json};
        const pathsData = {paths_json};
        const recsData = {recs_json};
        const matrixData = {matrix_json};

        let currentModel = 'Linear';

        const modelNames = {{
            'Linear': 'Linear',
            'First_Touch': 'First-Touch (FTA)',
            'Last_Touch': 'Last-Touch (LTA)',
            'Position_Based': 'Position-Based (U-Shaped)',
            'Time_Decay': 'Time-Decay (7-Day)',
            'Markov': 'Markov Chain (Data-Driven)'
        }};

        const fmtCur = (val) => '$' + Number(val).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
        const fmtNum = (val) => Number(val).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});

        function init() {{
            renderKPIs();
            renderRevenueChart();
            renderBubbleChart();
            renderHeatmap();
            renderChannelTable();
            renderPathsTable();
            renderSimulator();
        }}

        function switchModel(modelKey) {{
            currentModel = modelKey;
            const btns = document.querySelectorAll('.btn-model');
            btns.forEach(btn => {{
                if (btn.innerText.includes(modelKey.replace('_', '-')) || 
                   (modelKey === 'Linear' && btn.innerText.includes('Linear')) ||
                   (modelKey === 'Position_Based' && btn.innerText.includes('Position')) ||
                   (modelKey === 'Time_Decay' && btn.innerText.includes('Time')) ||
                   (modelKey === 'Markov' && btn.innerText.includes('Markov'))) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});

            document.getElementById('kpi-model-name').innerText = currentModel.replace('_', ' ');
            document.getElementById('chart-model-label').innerText = currentModel.replace('_', ' ');

            renderKPIs();
            renderRevenueChart();
        }}

        function renderKPIs() {{
            let totSpend = 0;
            let totRev = 0;
            channelData.forEach(d => {{
                totSpend += d.Spend;
                totRev += d[currentModel + '_Revenue'];
            }});
            const totProfit = totRev - totSpend;
            const roas = totRev / totSpend;

            document.getElementById('kpi-spend').innerText = fmtCur(totSpend);
            document.getElementById('kpi-rev').innerText = fmtCur(totRev);
            document.getElementById('kpi-roas').innerText = roas.toFixed(2) + 'x';
            document.getElementById('kpi-profit').innerText = fmtCur(totProfit);
        }}

        function renderRevenueChart() {{
            const channels = channelData.map(d => d.Channel);
            const revenues = channelData.map(d => d[currentModel + '_Revenue']);
            const spends = channelData.map(d => d.Spend);

            const traceRev = {{
                x: channels,
                y: revenues,
                name: modelNames[currentModel] + ' Revenue',
                type: 'bar',
                marker: {{ color: '#2563eb' }},
                hovertemplate: '<b>%{{x}}</b><br>Attributed Revenue: $%{{y:,.2f}}<extra></extra>'
            }};

            const traceSpend = {{
                x: channels,
                y: spends,
                name: 'Marketing Spend',
                type: 'bar',
                marker: {{ color: '#94a3b8' }},
                hovertemplate: '<b>%{{x}}</b><br>Spend: $%{{y:,.2f}}<extra></extra>'
            }};

            const layout = {{
                barmode: 'group',
                xaxis: {{ title: '<b>Marketing Channel</b>' }},
                yaxis: {{ title: '<b>Amount ($)</b>', tickprefix: '$', tickformat: ',.0f' }},
                margin: {{ t: 20, r: 20, l: 60, b: 60 }},
                legend: {{ orientation: 'h', y: 1.15, x: 1, xanchor: 'right' }},
                template: 'plotly_white'
            }};

            Plotly.newPlot('chart-channel-revenue', [traceRev, traceSpend], layout, {{ responsive: true }});
        }}

        function renderBubbleChart() {{
            const channels = channelData.map(d => d.Channel);
            const spends = channelData.map(d => d.Spend);
            const roas = channelData.map(d => d.Linear_ROAS);
            const convs = channelData.map(d => d.Linear_Conversions);

            const trace = {{
                x: spends,
                y: roas,
                text: channels,
                mode: 'markers+text',
                textposition: 'top center',
                marker: {{
                    size: convs.map(c => c * 3.5),
                    color: roas,
                    colorscale: 'Viridis',
                    showscale: true,
                    colorbar: {{ title: 'ROAS (x)' }},
                    line: {{ color: '#334155', width: 1.5 }}
                }},
                hovertemplate: '<b>%{{text}}</b><br>Spend: $%{{x:,.2f}}<br>Linear ROAS: %{{y:.2f}}x<br>Attributed Conversions: %{{marker.size:,.1f}}<extra></extra>'
            }};

            const layout = {{
                xaxis: {{ title: '<b>Channel Spend ($)</b>', tickprefix: '$', tickformat: ',.0f' }},
                yaxis: {{ title: '<b>Linear ROAS (Log Scale)</b>', type: 'log', tickformat: '.1f' }},
                margin: {{ t: 20, r: 20, l: 60, b: 60 }},
                template: 'plotly_white'
            }};

            Plotly.newPlot('chart-bubble', [trace], layout, {{ responsive: true }});
        }}

        function renderHeatmap() {{
            const trace = {{
                z: matrixData.matrix,
                x: matrixData.states,
                y: matrixData.states,
                type: 'heatmap',
                colorscale: 'Blues',
                showscale: true,
                colorbar: {{ title: 'Prob' }}
            }};

            const layout = {{
                xaxis: {{ title: '<b>Next State</b>', tickangle: -45 }},
                yaxis: {{ title: '<b>Current State</b>' }},
                margin: {{ t: 20, r: 20, l: 90, b: 90 }},
                template: 'plotly_white'
            }};

            Plotly.newPlot('chart-heatmap', [trace], layout, {{ responsive: true }});
        }}

        function renderChannelTable() {{
            const tbody = document.getElementById('channel-table-body');
            tbody.innerHTML = '';

            channelData.forEach(d => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="text-align: left; font-weight: 700;">${{d.Channel}}</td>
                    <td>${{fmtCur(d.Spend)}}</td>
                    <td>${{d.Spend_Share_Pct.toFixed(1)}}%</td>
                    <td>${{fmtCur(d.First_Touch_Revenue)}}</td>
                    <td>${{fmtCur(d.Last_Touch_Revenue)}}</td>
                    <td style="font-weight: 700; color: #16a34a;">${{fmtCur(d.Linear_Revenue)}}</td>
                    <td>${{fmtCur(d.Markov_Revenue)}}</td>
                    <td>${{d.First_Touch_ROAS.toFixed(2)}}x</td>
                    <td>${{d.Last_Touch_ROAS.toFixed(2)}}x</td>
                    <td style="font-weight: 700; color: #2563eb;">${{d.Linear_ROAS.toFixed(2)}}x</td>
                    <td>${{d.Markov_ROAS.toFixed(2)}}x</td>
                    <td>${{fmtCur(d.Linear_CAC)}}</td>
                `;
                tbody.appendChild(row);
            }});
        }}

        function renderPathsTable() {{
            const tbody = document.getElementById('paths-table-body');
            tbody.innerHTML = '';

            pathsData.forEach(d => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="text-align: left; font-weight: 600; color: #1e3a8a;">${{d.Path}}</td>
                    <td>${{d.Total_Customers}}</td>
                    <td style="font-weight: 700;">${{d.Conversions}}</td>
                    <td><span class="status-pill pill-blue">${{d.Conversion_Rate_Pct.toFixed(1)}}%</span></td>
                    <td>${{d.Avg_Path_Length.toFixed(1)}}</td>
                    <td style="font-weight: 700; color: #16a34a;">${{fmtCur(d.Total_Revenue)}}</td>
                `;
                tbody.appendChild(row);
            }});
        }}

        const simSpendMultipliers = {{}};
        channelData.forEach(d => simSpendMultipliers[d.Channel] = 1.0);

        function renderSimulator() {{
            const container = document.getElementById('sim-sliders-container');
            container.innerHTML = '';

            channelData.forEach(d => {{
                const ch = d.Channel;
                const div = document.createElement('div');
                div.className = 'sim-channel';
                div.innerHTML = `
                    <div class="sim-channel-header">
                        <span class="sim-channel-name">${{ch}}</span>
                        <span class="sim-channel-spend" id="sim-val-${{ch.replace(/\\s+/g, '-')}}">${{fmtCur(d.Spend)}}</span>
                    </div>
                    <input type="range" class="sim-slider" min="0.5" max="1.5" step="0.05" value="1.0"
                           id="slider-${{ch.replace(/\\s+/g, '-')}}"
                           oninput="updateSimulator('${{ch}}', this.value)">
                    <div class="sim-slider-val">
                        <span>-50%</span>
                        <span id="slider-pct-${{ch.replace(/\\s+/g, '-')}}">Current (0%)</span>
                        <span>+50%</span>
                    </div>
                `;
                container.appendChild(div);
            }});
            recalculateSimulation();
        }}

        function updateSimulator(channel, val) {{
            simSpendMultipliers[channel] = parseFloat(val);
            const deltaPct = ((parseFloat(val) - 1.0) * 100).toFixed(0);
            const chId = channel.replace(/\\s+/g, '-');
            const orig = channelData.find(d => d.Channel === channel).Spend;
            const newSpend = orig * parseFloat(val);

            document.getElementById('sim-val-' + chId).innerText = fmtCur(newSpend);
            document.getElementById('slider-pct-' + chId).innerText = (deltaPct >= 0 ? '+' : '') + deltaPct + '%';

            recalculateSimulation();
        }}

        function recalculateSimulation() {{
            let simTotalRev = 0;
            const baseRev = 1926331.12;

            channelData.forEach(d => {{
                const mult = simSpendMultipliers[d.Channel] || 1.0;
                simTotalRev += (d.Spend * mult) * d.Linear_ROAS;
            }});

            const upliftPct = ((simTotalRev - baseRev) / baseRev) * 100;
            document.getElementById('sim-total-rev').innerText = fmtCur(simTotalRev);
            const badge = document.getElementById('sim-uplift-badge');
            badge.innerText = (upliftPct >= 0 ? '+' : '') + upliftPct.toFixed(2) + '%';
            badge.className = 'status-pill ' + (upliftPct >= 0 ? 'pill-green' : 'pill-red');
        }}

        window.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    with open('dashboard/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("Successfully built index.html and dashboard/index.html!")


if __name__ == '__main__':
    build_dashboard()
