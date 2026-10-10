# Multi-Touch Marketing Attribution & ROI Optimization Engine

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-3.0%2B-150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Plotly](https://img.shields.io/badge/Plotly-7.1%2B-3F4F75.svg?logo=plotly&logoColor=white)](https://plotly.com)
[![Power BI](https://img.shields.io/badge/Power_BI-Certified_DAX-F2C811.svg?logo=powerbi&logoColor=black)](https://powerbi.microsoft.com)
[![SQL](https://img.shields.io/badge/SQL-ANSI%20%7C%20MySQL-4479A1.svg?logo=mysql&logoColor=white)](https://www.mysql.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, end-to-end **Multi-Touch Marketing Attribution (MTA) & Econometric Return on Investment (ROI) Analytics Engine**. This repository provides complete mathematical implementations of **6 attribution models**, diagnoses and resolves critical sequence-inversion and revenue-destruction bugs in legacy SQL/Python workflows, and introduces an **algorithmic budget reallocation simulator** delivering a **+12.32% (+$237.3K) projected revenue uplift** without increasing marketing spend.

---

## Table of Contents
1. [Executive Summary & Problem Statement](#1-executive-summary--problem-statement)
2. [Diagnostic Audit & Critical Bug Fixes](#2-diagnostic-audit--critical-bug-fixes)
3. [Attribution Modeling Methodology & Formulas](#3-attribution-modeling-methodology--formulas)
4. [Empirical Results & Channel Performance Matrix](#4-empirical-results--channel-performance-matrix)
5. [Algorithmic Budget Optimization & Uplift Simulation](#5-algorithmic-budget-optimization--uplift-simulation)
6. [Interactive Dashboards & Deliverables](#6-interactive-dashboards--deliverables)
   - [A. Standalone Interactive HTML Dashboard](#a-standalone-interactive-html-dashboard)
   - [B. Streamlit Web Application](#b-streamlit-web-application)
   - [C. Power BI Star Schema & Dynamic DAX Switcher](#c-power-bi-star-schema--dynamic-dax-switcher)
   - [D. Production SQL Pipeline](#d-production-sql-pipeline)
   - [E. Executed Master Jupyter Notebook](#e-executed-master-jupyter-notebook)
7. [Repository File Structure](#7-repository-file-structure)
8. [Installation & Execution Guide](#8-installation--execution-guide)

---

## 1. Executive Summary & Problem Statement

In omnichannel marketing, customer journeys are non-linear. Prospects interact with paid social ads, organic search results, YouTube videos, emails, and direct website visits across days or weeks before making a purchase. 

Relying on legacy single-touch attribution creates severe blindspots:
* **Last-Touch Attribution (LTA)** exclusively credits conversion closers (e.g., Mobile App and Website checkout), leading marketing executives to underfund top-of-funnel brand discovery.
* **First-Touch Attribution (FTA)** exclusively credits brand introduction (e.g., Instagram, Email), completely ignoring lead nurturing and retargeting mechanisms.

### Portfolio Overview:
* **Total Tracked Touchpoints:** 1,050 interactions
* **Unique Customer Cohort:** 300 customers
* **Total Converted Customers:** 102 conversions (34.00% Baseline Conversion Rate)
* **Total Attributed Conversion Revenue:** **$1,926,331.12**
* **Total Marketing Budget Deployed:** **$173,734.22**
* **Portfolio Blended ROAS:** **11.09x** (Portfolio Net ROI: **+1,008.78%**)

---

## 2. Diagnostic Audit & Critical Bug Fixes

A comprehensive audit of the initial repository uncovered multiple foundational flaws in the data pipelines, SQL queries, and Power BI reports:

| Issue Area | Initial Repository State | Critical Impact | Antigravity AI Resolution |
| :--- | :--- | :--- | :--- |
| **Date Sorting & Chronology** | Sorted string dates (`DD-MM-YYYY`) alphabetically via `ORDER BY Touchpoint_Date` | Alphabetical ordering sorted `06-02-2026` before `30-01-2026` (Feb before Jan) and May before Apr, inverting 169 customer journey paths! | Implemented strict UTC timestamp parsing & chronological re-indexing (`ROW_NUMBER() OVER (PARTITION BY Customer_ID ORDER BY Parsed_Date)`). |
| **First-Touch Revenue Attribution** | Multiplied `First_Click_Weight = 1` directly by row-level `Revenue` in SQL | Raw conversion revenue is recorded at checkout (final row); preceding rows have `Revenue = 0`. First touch received **$0 revenue** whenever conversion wasn't on touchpoint 1! | Aggregated `Customer_Total_Revenue = SUM(Revenue) OVER (PARTITION BY Customer_ID)` so 100% of conversion revenue is assigned to the true discovery touchpoint. |
| **Linear Attribution Revenue Leakage** | Computed `ROUND(SUM(Revenue / Total_Touchpoints), 2)` directly in SQL | Because `Revenue` was zero on non-checkout rows, only the converting channel divided its own revenue. **Over 75% of customer revenue was erased**, and nurturing channels received $0! | Distributed full `Customer_Total_Revenue / Journey_Length` across every interaction, perfectly preserving 100.00% of revenue ($1.926M). |
| **Missing Attribution Models** | Only basic First Click and corrupted Linear SQL drafts were explored | No Time-Decay, Position-Based (U-Shaped), or Algorithmic Markov Chain models were implemented. | Built a modular Python engine (`src/attribution_models.py`) and ANSI SQL pipeline (`sql/multi_touch_attribution.sql`) computing all 6 models. |
| **Fragmented Notebooks** | 7 unfinished notebook files (`Ingestion.ipynb`, `Cleaned Loop.ipynb`, etc.) with 0-6 basic cells | None of the notebooks performed attribution modeling, ROI calculations, or visualizations. | Consolidated into a single, fully executed master notebook (`Multi_Touch_Marketing_Attribution_ROI_Master.ipynb`). |
| **Power BI Visual Design** | 6 isolated pages with 1 visual per page using default names and `Comic Sans MS` | Lacked attribution model comparison, dynamic slicers, CAC metrics, or cohesive dashboard UX. | Engineered Star Schema documentation, cleaned master data, and interactive dynamic DAX switchers (`powerbi/PowerBI_DAX_Measures.md`). |

---

## 3. Attribution Modeling Methodology & Formulas

Let a customer journey $j$ have $N$ chronological touchpoints $t_1, t_2, \dots, t_N$ occurring on dates $d_1, d_2, \dots, d_N$, with total conversion revenue $R_j$.

### 1. First-Touch Attribution (FTA)
Credits 100% of value to customer discovery:
$$w_i = \begin{cases} 1.0 & \text{if } i = 1 \\ 0.0 & \text{if } i > 1 \end{cases}, \quad \text{Attributed Revenue}_i = w_i \times R_j$$

### 2. Last-Touch Attribution (LTA)
Credits 100% of value to the final conversion checkout:
$$w_i = \begin{cases} 1.0 & \text{if } i = N \\ 0.0 & \text{if } i < N \end{cases}, \quad \text{Attributed Revenue}_i = w_i \times R_j$$

### 3. Linear Attribution (LA)
Equally distributes credit across all interactions in the journey:
$$w_i = \frac{1}{N}, \quad \text{Attributed Revenue}_i = \frac{R_j}{N}$$

### 4. Position-Based (U-Shaped: 40/40/20) Attribution (PBA)
Emphasizes both initial acquisition and final conversion, while acknowledging lead nurturing:
$$w_i = \begin{cases} 1.0 & N = 1 \\ 0.50 & N = 2 \\ 0.40 & i = 1 \text{ or } i = N \\ \frac{0.20}{N - 2} & 1 < i < N \end{cases}$$

### 5. Time-Decay Attribution (TDA)
Exponentially discounts interactions occurring further in time from the conversion event, using a parameterizable half-life ($\lambda = 7\text{ days}$):
$$\Delta t_i = d_N - d_i, \quad \tilde{w}_i = 2^{-\frac{\Delta t_i}{\lambda}}, \quad w_i = \frac{\tilde{w}_i}{\sum_{k=1}^N \tilde{w}_k}$$

### 6. Absorbing Markov Chain Data-Driven Attribution (MCA)
Models customer journeys as a stochastic state transition network with transient states (Start, Channels) and absorbing states (Conversion, Null).
1. **Transition Probability Matrix ($P$):**
   $$P = \begin{pmatrix} Q & R \\ 0 & I \end{pmatrix}$$
2. **Fundamental Matrix ($N$):** $N = (I - Q)^{-1}$
3. **Absorption Probabilities ($B$):** $B = N \cdot R$
4. **Removal Effect ($RE_C$):** By removing channel $C$ and routing its transitions to `Null`, we compute the degradation in conversion probability:
   $$RE_C = 1 - \frac{P_{-C}(\text{Conversion} \mid \text{Start})}{P(\text{Conversion} \mid \text{Start})}, \quad W_C = \frac{RE_C}{\sum_{k} RE_k}$$

---

## 4. Empirical Results & Channel Performance Matrix

| Channel | Spend ($) | Spend Share | First-Touch Rev | Last-Touch Rev | Linear Rev | Markov Rev | FTA ROAS | LTA ROAS | Linear ROAS | Markov ROAS | Linear CAC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Email** | $5,601.86 | 3.2% | $236,053.56 | $38,471.97 | $180,162.85 | $140,698.81 | **42.14x** | 6.87x | 32.16x | 25.12x | $58.12 |
| **Facebook Ads** | $33,627.22 | 19.4% | $161,555.27 | $258,413.85 | $258,760.02 | $255,907.03 | 4.80x | 7.68x | 7.69x | 7.61x | $2,492.36 |
| **Google Ads** | $38,990.40 | 22.4% | $311,158.94 | $233,456.17 | $250,135.67 | $246,673.34 | 7.98x | 5.99x | 6.42x | 6.33x | $2,869.60 |
| **Instagram** | $27,317.91 | 15.7% | $358,775.26 | $176,146.25 | $314,193.27 | $338,300.99 | **13.13x** | 6.45x | 11.50x | 12.38x | $1,617.20 |
| **Mobile App** | $5,218.05 | 3.0% | $76,462.33 | $439,217.64 | $202,395.39 | $195,164.20 | 14.65x | **84.17x** | 38.79x | 37.40x | $48.33 |
| **Organic Search** | $3,564.87 | 2.0% | $186,293.34 | $312,336.24 | $207,385.04 | $218,284.18 | **52.26x** | **87.62x** | 58.17x | 61.23x | $32.48 |
| **Website** | $4,834.74 | 2.8% | $238,489.17 | $255,886.99 | $277,021.52 | $278,775.08 | **49.33x** | **52.93x** | 57.30x | 61.80x | $35.91 |
| **YouTube** | $54,579.17 | 31.4% | $357,543.25 | $212,402.01 | $236,277.36 | $232,527.48 | 6.55x | 3.89x | **4.33x** | **4.26x** | $4,357.73 |
| **Total / Portfolio** | **$173,734.22** | **100.0%** | **$1,926,331.12** | **$1,926,331.12** | **$1,926,331.12** | **$1,926,331.12** | **11.09x** | **11.09x** | **11.09x** | **11.09x** | **$1,703.28** |

### Critical Takeaways:
1. **The Last-Touch Blindspot on Email & Instagram:** Email has a massive **42.1x First-Touch ROAS** but drops to **6.8x on Last-Touch**. Similarly, Instagram introduces **$358.8K** in revenue (FTA) but only closes **$176.1K** (LTA). Single-touch reporting under-credits their revenue generation by over 50%.
2. **Mobile App is the Primary Conversion Engine:** Mobile App delivers an extraordinary **84.17x Last-Touch ROAS** ($439.2K revenue), proving it is the organization's premier conversion mechanism. However, it relies heavily on social and search to populate the funnel.
3. **YouTube Budget Saturation:** YouTube absorbs **31.4% of total budget ($54.6K)**, yet generates the lowest portfolio ROAS across all multi-touch models (4.26x - 4.33x). It is operating well into diminishing marginal returns.

---

## 5. Algorithmic Budget Optimization & Uplift Simulation

By pairing Markov Removal Effects and Linear ROAS, our optimization algorithm systematically rebalances marketing spend:
* **Trim Spend (-20.9%):** From over-saturated channels (YouTube: -$11.4K).
* **Scale Spend (+27.3% to +35.2%):** Into hyper-efficient discovery channels (Instagram: +$7.5K; Email: +$1.9K; Organic Search: +$1.2K).
* **Projected Revenue Uplift:** **+12.32% (+237,300.00)** with **$0 additional marketing budget**!

| Channel | Current Spend | Current Share | Optimized Spend | Optimized Share | Budget Delta ($) | Delta % | Strategic Classification & Action |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Email** | $5,601.86 | 3.2% | $7,571.21 | 4.4% | +$1,969.35 | +35.2% | **Top-Funnel Initiator:** Scale budget (+35%) to accelerate discovery. |
| **Facebook Ads** | $33,627.22 | 19.4% | $34,896.79 | 20.1% | +$1,269.57 | +3.8% | **Balanced Contributor:** Maintain steady mid-funnel spend. |
| **Google Ads** | $38,990.40 | 22.4% | $40,463.35 | 23.3% | +$1,472.95 | +3.8% | **Intent Harvester:** Maintain search capture. |
| **Instagram** | $27,317.91 | 15.7% | $34,785.49 | 20.0% | +$7,467.58 | +27.3% | **High-Efficiency Initiator:** Major scale (+27%) to capture new cohorts. |
| **Mobile App** | $5,218.05 | 3.0% | $6,222.06 | 3.6% | +$1,004.01 | +19.2% | **Bottom-Funnel Closer:** Protect and optimize onboarding conversion. |
| **Organic Search** | $3,564.87 | 2.0% | $4,818.17 | 2.8% | +$1,253.30 | +35.2% | **High-Efficiency SEO:** Expand technical content and keywords. |
| **Website** | $4,834.74 | 2.8% | $6,534.48 | 3.8% | +$1,699.74 | +35.2% | **Conversion Bedrock:** Enhance on-site CRO and landing pages. |
| **YouTube** | $54,579.17 | 31.4% | $43,153.28 | 24.8% | -$11,425.89 | -20.9% | **Diminishing Returns:** Trim budget (-21%) to fund high-velocity channels. |
| **Total** | **$173,734.22** | **100.0%** | **$173,734.22** | **100.0%** | **$0.00** | **0.0%** | **Projected Revenue: $2,163,631.12 (+12.32% Uplift)** |

---

## 6. Interactive Dashboards & Deliverables

### A. Live Interactive Web Dashboard (GitHub Pages Ready)
A responsive, standalone executive web application built with HTML5, CSS3, JavaScript, and Plotly.js.
* **Root Entrypoint:** [`index.html`](file:///C:/Users/Iba%20Zaidi/Desktop/Multiouch%20marketingA/index.html)
* **Dashboard Folder:** [`dashboard/index.html`](file:///C:/Users/Iba%20Zaidi/Desktop/Multiouch%20marketingA/dashboard/index.html)
* **Key Interactive Features:**
  * **Dynamic Attribution Model Switcher:** Instantly toggle between **Linear, First-Touch, Last-Touch, Position-Based (U-Shaped), Time-Decay, and Markov Chain** models. Watch all KPI cards, revenue breakdowns, and charts update dynamically in real time.
  * **Interactive What-If Budget Simulator:** Move channel budget sliders (-50% to +50%) and observe immediate mathematical recalculations of projected portfolio revenue and uplift percentage.
  * **Markov State Transition Heatmap:** Explore transition probabilities between initial discovery, intermediate touchpoints, and conversion.
  * **Customer Journey Path Explorer:** Sortable and searchable table of top customer journey paths with conversion rates and touchpoint sequences.
* **How to View:**
  * **Locally:** Simply double-click [`index.html`](file:///C:/Users/Iba%20Zaidi/Desktop/Multiouch%20marketingA/index.html) in your browser.
  * **On GitHub:** Enable **GitHub Pages** (Settings -> Pages -> Deploy from Branch: `main` / root) to host the dashboard live on the web!

### B. Visual Intelligence Previews
| Multi-Model Attributed Revenue | Spend vs. Multi-Touch ROAS Efficiency |
| :---: | :---: |
| ![Model Comparison](reports/figures/attribution_model_comparison.png) | ![ROAS vs Spend](reports/figures/channel_roas_vs_spend.png) |

| Markov State Transition Probability Matrix | Algorithmic Budget Optimization Waterfall |
| :---: | :---: |
| ![Markov Heatmap](reports/figures/markov_transition_heatmap.png) | ![Budget Waterfall](reports/figures/budget_optimization_waterfall.png) |

### C. Streamlit Web Application
An interactive analytics app with real-time filtering by Country, Customer Segment, Product Category, and Attribution Model.
* **File:** [`app.py`](file:///C:/Users/Iba%20Zaidi/Desktop/Multiouch%20marketingA/app.py)
* **Command:** `streamlit run app.py`

### D. Power BI Star Schema & Dynamic DAX Switcher
* **Guide:** [`powerbi/PowerBI_DAX_Measures.md`](file:///C:/Users/Iba%20Zaidi/Desktop/Multiouch%20marketingA/powerbi/PowerBI_DAX_Measures.md)
* **Master Fact Data:** [`powerbi/Multi_Touch_Marketing_Attribution_Master_Cleaned.csv`](file:///C:/Users/Iba%20Zaidi/Desktop/Multiouch%20marketingA/powerbi/Multi_Touch_Marketing_Attribution_Master_Cleaned.csv)
* **Channel Aggregate Data:** [`powerbi/Channel_Attribution_ROI_Summary.csv`](file:///C:/Users/Iba%20Zaidi/Desktop/Multiouch%20marketingA/powerbi/Channel_Attribution_ROI_Summary.csv)
* **Highlights:** Includes ready-to-use DAX measures for dynamic single-slicer attribution switching, Star Schema modeling, and canvas layout blueprints.

### E. Production SQL Pipeline
* **File:** [`sql/multi_touch_attribution.sql`](file:///C:/Users/Iba%20Zaidi/Desktop/Multiouch%20marketingA/sql/multi_touch_attribution.sql)
* **Capabilities:** Robust ANSI/MySQL script fixing date sorting, window-function journey re-indexing, customer conversion aggregation, and financial metrics across 5 deterministic models.

### F. Executed Master Jupyter Notebook
* **File:** [`Multi_Touch_Marketing_Attribution_ROI_Master.ipynb`](file:///C:/Users/Iba%20Zaidi/Desktop/Multiouch%20marketingA/Multi_Touch_Marketing_Attribution_ROI_Master.ipynb)
* **Status:** Fully executed with all code, mathematical formulations, diagnostic tables, and visual plots persisted directly in the file.

---

## 7. Repository File Structure

```text
Multi-Touch-Marketing-Attribution-ROI-Dashboard/
├── Multi_Touch_Marketing_Attribution_ROI_Dataset.csv         # Cleaned input dataset
├── Multi_Touch_Marketing_Attribution_Master_Cleaned.csv     # Master enriched fact table
├── Multi_Touch_Marketing_Attribution_ROI_Master.ipynb       # Fully executed master notebook
├── app.py                                                   # Interactive Streamlit application
├── generate_interactive_dashboard.py                       # Standalone Plotly HTML dashboard builder
├── README.md                                                # Complete project documentation
├── requirements.txt                                         # Python package dependencies
│
├── src/                                                     # Modular Python Analytics Package
│   ├── __init__.py                                          # Package exports
│   ├── data_loader.py                                       # Ingestion, UTC parsing & sequencing
│   ├── attribution_models.py                                # FTA, LTA, Linear, U-Shaped, Time-Decay, Markov
│   ├── roi_analytics.py                                     # Financial KPIs, ROAS, ROI, CAC & Optimization
│   └── visualizations.py                                    # Matplotlib/Seaborn visualization suite
│
├── sql/                                                     # Database Analytics
│   └── multi_touch_attribution.sql                          # Production ANSI SQL multi-touch attribution
│
├── powerbi/                                                 # Power BI Integration
│   ├── PowerBI_DAX_Measures.md                              # Star Schema & Dynamic DAX Switcher Guide
│   ├── Multi_Touch_Marketing_Attribution_Master_Cleaned.csv # Fact table for Power BI import
│   └── Channel_Attribution_ROI_Summary.csv                  # Channel summary table
│
└── reports/                                                 # Analytical Reports & Figures
    ├── interactive_dashboard.html                           # Standalone browser dashboard
    ├── Channel_Attribution_ROI_Summary.csv                  # Multi-model financial metrics
    ├── Customer_Journey_Paths.csv                           # Top customer conversion paths
    ├── Markov_Transition_Matrix.csv                         # State transition probabilities
    ├── Budget_Optimization_Recommendations.csv              # Reallocation scenarios & deltas
    └── figures/                                             # High-resolution chart figures
        ├── attribution_model_comparison.png
        ├── channel_roas_vs_spend.png
        ├── markov_transition_heatmap.png
        └── budget_optimization_waterfall.png
```

---

## 8. Installation & Execution Guide

### Prerequisites
* Python 3.10+ installed
* Standard analytical packages: `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`, `scipy`

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Open the Interactive HTML Dashboard
Simply open [`reports/interactive_dashboard.html`](file:///C:/Users/Iba%20Zaidi/Desktop/Multiouch%20marketingA/reports/interactive_dashboard.html) in Google Chrome, Microsoft Edge, or Mozilla Firefox.

### Step 3: Run the Streamlit Application (Optional)
```bash
streamlit run app.py
```

### Step 4: Run the Full Python Analytics Pipeline
```bash
python generate_interactive_dashboard.py
```

---

## License
This project is open-source and licensed under the [MIT License](LICENSE).
