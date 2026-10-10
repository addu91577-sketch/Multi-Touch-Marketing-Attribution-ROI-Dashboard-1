"""
Multi-Touch Marketing Attribution & ROI Interactive Streamlit Application
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="Multi-Touch Marketing Attribution & ROI Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 30px;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 4px;
    }
    .sub-title {
        font-size: 15px;
        color: #64748b;
        margin-bottom: 24px;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 16px 20px;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv('Multi_Touch_Marketing_Attribution_Master_Cleaned.csv')
    df['Touchpoint_Date_Parsed'] = pd.to_datetime(df['Touchpoint_Date_Parsed'])
    summary = pd.read_csv('reports/Channel_Attribution_ROI_Summary.csv')
    paths = pd.read_csv('reports/Customer_Journey_Paths.csv')
    matrix = pd.read_csv('reports/Markov_Transition_Matrix.csv', index_col=0)
    recs = pd.read_csv('reports/Budget_Optimization_Recommendations.csv')
    return df, summary, paths, matrix, recs


df, summary, paths, matrix, recs = load_data()

# Header
st.markdown('<div class="main-title">Multi-Touch Marketing Attribution & ROI Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Algorithmic Attribution Modeling (FTA, LTA, Linear, U-Shaped, Time-Decay, Markov Chain) & Budget Optimization</div>', unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.header("🕹️ Executive Controls & Filters")

all_countries = ['All'] + sorted(df['Country'].unique().tolist())
selected_country = st.sidebar.selectbox("Country", all_countries)

all_categories = ['All'] + sorted(df['Product_Category'].unique().tolist())
selected_category = st.sidebar.selectbox("Product Category", all_categories)

all_segments = ['All'] + sorted(df['Customer_Segment'].unique().tolist())
selected_segment = st.sidebar.selectbox("Customer Segment", all_segments)

model_options = {
    'Linear': 'Rev_Linear',
    'First-Touch': 'Rev_First_Touch',
    'Last-Touch': 'Rev_Last_Touch',
    'Position-Based (U-Shaped)': 'Rev_Position_Based',
    'Time-Decay': 'Rev_Time_Decay',
    'Markov Chain': 'Rev_Markov'
}
selected_model_name = st.sidebar.selectbox("Active Attribution Model", list(model_options.keys()))
active_rev_col = model_options[selected_model_name]

# Filter Dataset
filtered_df = df.copy()
if selected_country != 'All':
    filtered_df = filtered_df[filtered_df['Country'] == selected_country]
if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['Product_Category'] == selected_category]
if selected_segment != 'All':
    filtered_df = filtered_df[filtered_df['Customer_Segment'] == selected_segment]

# High-Level Metrics
tot_spend = filtered_df['Cost'].sum()
tot_rev = filtered_df[active_rev_col].sum()
tot_profit = tot_rev - tot_spend
blended_roas = tot_rev / tot_spend if tot_spend > 0 else 0
blended_roi = (tot_profit / tot_spend) * 100 if tot_spend > 0 else 0
conv_count = filtered_df[filtered_df['Journey_Step'] == 1]['Customer_Converted_Flag'].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Marketing Spend", f"${tot_spend:,.2f}")
col2.metric(f"{selected_model_name} Revenue", f"${tot_rev:,.2f}")
col3.metric("Blended ROAS", f"{blended_roas:.2f}x")
col4.metric("Blended Net ROI", f"+{blended_roi:,.1f}%")
col5.metric("Conversions", f"{int(conv_count)}")

st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Attribution Model Comparison",
    "🎯 Channel Efficiency Matrix",
    "🧭 Customer Journey Explorer",
    "💡 Budget Optimization Simulator"
])

with tab1:
    st.subheader("Cross-Model Revenue Attribution by Channel")
    models = ['First_Touch', 'Last_Touch', 'Linear', 'Position_Based', 'Time_Decay', 'Markov']
    display_names = ['First-Touch', 'Last-Touch', 'Linear', 'Position-Based (U)', 'Time-Decay', 'Markov']

    fig_comp = go.Figure()
    for m, dname in zip(models, display_names):
        ch_rev = filtered_df.groupby('Channel')[f'Rev_{m}'].sum().reset_index()
        fig_comp.add_trace(go.Bar(
            x=ch_rev['Channel'],
            y=ch_rev[f'Rev_{m}'],
            name=dname
        ))

    fig_comp.update_layout(
        barmode='group',
        xaxis_title="Marketing Channel",
        yaxis_title="Attributed Revenue ($)",
        yaxis_tickprefix="$",
        height=480,
        template="plotly_white"
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    st.subheader("Channel Attribution Summary Table")
    ch_agg = filtered_df.groupby('Channel').agg(
        Spend=('Cost', 'sum'),
        Conversions=('Conv_Linear', 'sum'),
        FTA_Rev=('Rev_First_Touch', 'sum'),
        LTA_Rev=('Rev_Last_Touch', 'sum'),
        Linear_Rev=('Rev_Linear', 'sum'),
        Markov_Rev=('Rev_Markov', 'sum')
    ).reset_index()
    ch_agg['Linear_ROAS'] = ch_agg['Linear_Rev'] / ch_agg['Spend']
    ch_agg['Linear_CAC'] = ch_agg['Spend'] / ch_agg['Conversions']
    st.dataframe(ch_agg.style.format({
        'Spend': '${:,.2f}',
        'Conversions': '{:.2f}',
        'FTA_Rev': '${:,.2f}',
        'LTA_Rev': '${:,.2f}',
        'Linear_Rev': '${:,.2f}',
        'Markov_Rev': '${:,.2f}',
        'Linear_ROAS': '{:.2f}x',
        'Linear_CAC': '${:,.2f}'
    }), use_container_width=True)

with tab2:
    st.subheader("Marketing Efficiency Matrix: Spend vs Linear ROAS")
    ch_perf = filtered_df.groupby('Channel').agg(
        Spend=('Cost', 'sum'),
        Conversions=('Conv_Linear', 'sum'),
        Revenue=(active_rev_col, 'sum')
    ).reset_index()
    ch_perf['ROAS'] = ch_perf['Revenue'] / ch_perf['Spend']

    fig_bubble = px.scatter(
        ch_perf,
        x='Spend',
        y='ROAS',
        size='Conversions',
        color='Channel',
        text='Channel',
        log_y=True,
        title="Spend vs Return on Ad Spend (Bubble Size = Attributed Conversions)"
    )
    fig_bubble.update_traces(textposition='top center')
    fig_bubble.update_layout(height=500, template="plotly_white", yaxis_tickformat=".1f")
    st.plotly_chart(fig_bubble, use_container_width=True)

with tab3:
    st.subheader("Markov State Transition Probability Matrix")
    fig_heat = px.imshow(
        matrix.values,
        labels=dict(x="Next State", y="Current State", color="Transition Prob"),
        x=matrix.columns.tolist(),
        y=matrix.index.tolist(),
        color_continuous_scale="Blues",
        text_auto=".2f"
    )
    fig_heat.update_layout(height=520)
    st.plotly_chart(fig_heat, use_container_width=True)

    st.subheader("Top Customer Journey Conversion Paths")
    st.dataframe(paths.style.format({
        'Total_Revenue': '${:,.2f}',
        'Conversion_Rate_Pct': '{:.1f}%',
        'Revenue_Per_Customer': '${:,.2f}',
        'Avg_Path_Length': '{:.1f}',
        'Avg_Journey_Days': '{:.1f}'
    }), use_container_width=True)

with tab4:
    st.subheader("Algorithmic Budget Optimization & Scenario Planner")
    st.markdown("""
    **Optimization Logic:** Analyzes channel roles across the full conversion lifecycle (Initiators vs Closers vs Nurturers).
    Reallocates marginal spend from channels experiencing diminishing returns (e.g. YouTube) to high-velocity discovery channels (e.g. Instagram & Email).
    """)

    col_a, col_b = st.columns([2, 1])
    with col_a:
        waterfall_colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in recs['Spend_Delta']]
        fig_rec = go.Figure(go.Bar(
            x=recs['Channel'],
            y=recs['Spend_Delta'],
            marker_color=waterfall_colors,
            text=[f"{pct:+.1f}%" for pct in recs['Spend_Delta_Pct']],
            textposition='outside'
        ))
        fig_rec.update_layout(
            title="Recommended Budget Shift ($ Delta)",
            yaxis_title="Budget Delta ($)",
            yaxis_tickprefix="$",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig_rec, use_container_width=True)

    with col_b:
        st.metric("Projected Revenue Uplift", "+12.32%", "+$237,300.00")
        st.info("Zero additional marketing spend required. Pure reallocation of current $173.7k budget.")

    st.dataframe(recs[['Channel', 'Current_Spend', 'Optimized_Spend', 'Spend_Delta_Pct', 'Status', 'Recommended_Action', 'Rationale']].style.format({
        'Current_Spend': '${:,.2f}',
        'Optimized_Spend': '${:,.2f}',
        'Spend_Delta_Pct': '{:+.1f}%'
    }), use_container_width=True)
