# Power BI Multi-Touch Marketing Attribution: DAX Measures & Data Model Guide

This guide provides the complete **Star Schema Data Architecture**, **DAX Formulas**, and **Dashboard Visual Specifications** for importing `Multi_Touch_Marketing_Attribution_Master_Cleaned.csv` and creating an interactive Power BI report.

---

## 1. Data Model Architecture (Star Schema)

### Tables
1. **Fact Table (`Fact_Touchpoints`)**:
   - File: `powerbi/Multi_Touch_Marketing_Attribution_Master_Cleaned.csv`
   - Granularity: 1 row per customer touchpoint interaction.
   - Keys: `Customer_ID`, `Touchpoint_Date_Parsed`, `Channel`, `Product_Category`.
2. **Dimension Table (`Dim_Attribution_Model`)**:
   - Create a disconnected disconnected table using DAX:
   ```dax
   Dim_Attribution_Model = DATATABLE(
       "ModelID", INTEGER,
       "ModelName", STRING,
       "SortOrder", INTEGER,
       {
           {1, "First-Touch", 1},
           {2, "Last-Touch", 2},
           {3, "Linear", 3},
           {4, "Position-Based (U-Shaped)", 4},
           {5, "Time-Decay", 5},
           {6, "Markov Chain", 6}
       }
   )
   ```

---

## 2. Core DAX Measures

### A. Marketing Spend & Volume
```dax
Total Marketing Spend = 
SUM(Fact_Touchpoints[Cost])
```

```dax
Total Touchpoint Interactions = 
COUNTROWS(Fact_Touchpoints)
```

```dax
Total Converting Customers = 
CALCULATE(
    DISTINCTCOUNT(Fact_Touchpoints[Customer_ID]),
    Fact_Touchpoints[Customer_Converted_Flag] = 1
)
```

---

### B. Static Model Revenue Measures
```dax
First-Touch Revenue = 
SUM(Fact_Touchpoints[Rev_First_Touch])
```

```dax
Last-Touch Revenue = 
SUM(Fact_Touchpoints[Rev_Last_Touch])
```

```dax
Linear Revenue = 
SUM(Fact_Touchpoints[Rev_Linear])
```

```dax
Position-Based Revenue = 
SUM(Fact_Touchpoints[Rev_Position_Based])
```

```dax
Time-Decay Revenue = 
SUM(Fact_Touchpoints[Rev_Time_Decay])
```

```dax
Markov Revenue = 
SUM(Fact_Touchpoints[Rev_Markov])
```

---

### C. Dynamic Model Switching (Single Slicer Interactivity)
This measure enables users to select any attribution model from a slicer on the canvas, dynamically updating all cards, charts, and tables simultaneously.

```dax
Dynamic Attributed Revenue = 
VAR SelectedModel = SELECTEDVALUE(Dim_Attribution_Model[ModelName], "Linear")
RETURN
SWITCH(
    SelectedModel,
    "First-Touch", [First-Touch Revenue],
    "Last-Touch", [Last-Touch Revenue],
    "Linear", [Linear Revenue],
    "Position-Based (U-Shaped)", [Position-Based Revenue],
    "Time-Decay", [Time-Decay Revenue],
    "Markov Chain", [Markov Revenue],
    [Linear Revenue]
)
```

```dax
Dynamic Attributed Conversions = 
VAR SelectedModel = SELECTEDVALUE(Dim_Attribution_Model[ModelName], "Linear")
RETURN
SWITCH(
    SelectedModel,
    "First-Touch", SUM(Fact_Touchpoints[Conv_First_Touch]),
    "Last-Touch", SUM(Fact_Touchpoints[Conv_Last_Touch]),
    "Linear", SUM(Fact_Touchpoints[Conv_Linear]),
    "Position-Based (U-Shaped)", SUM(Fact_Touchpoints[Conv_Position_Based]),
    "Time-Decay", SUM(Fact_Touchpoints[Conv_Time_Decay]),
    "Markov Chain", SUM(Fact_Touchpoints[Conv_Markov]),
    SUM(Fact_Touchpoints[Conv_Linear])
)
```

```dax
Dynamic Net Profit = 
[Dynamic Attributed Revenue] - [Total Marketing Spend]
```

```dax
Dynamic ROAS = 
DIVIDE([Dynamic Attributed Revenue], [Total Marketing Spend], 0)
```

```dax
Dynamic ROI % = 
DIVIDE([Dynamic Net Profit], [Total Marketing Spend], 0) * 100
```

```dax
Dynamic CAC = 
DIVIDE([Total Marketing Spend], [Dynamic Attributed Conversions], 0)
```

---

## 3. Recommended Visual Layout in Power BI

### Page 1: Multi-Touch Attribution Executive Overview
- **Top Banner**: Title, Slicers for `Date`, `Product_Category`, `Country`, and `Attribution Model` (using `Dim_Attribution_Model[ModelName]`).
- **KPI Cards**: `Dynamic Attributed Revenue`, `Total Marketing Spend`, `Dynamic ROAS`, `Dynamic Net Profit`, `Total Converting Customers`.
- **Visual 1 (Clustered Column Chart)**: Channel on X-axis, `First-Touch Revenue`, `Last-Touch Revenue`, `Linear Revenue`, `Markov Revenue` on Y-axis.
- **Visual 2 (Scatter / Bubble Chart)**: X = `Total Marketing Spend`, Y = `Dynamic ROAS` (Log scale), Size = `Dynamic Attributed Conversions`, Legend = `Channel`.

### Page 2: Channel Acquisition vs Closer Dynamics
- **Visual 1 (Diverging Bar Chart)**: Difference between `First-Touch ROAS` and `Last-Touch ROAS` to highlight Initiators vs Closers.
- **Visual 2 (Table Matrix)**: Channels with Spend, Conversions, Revenue, ROAS, ROI %, and CAC across all models.

### Page 3: Algorithmic Budget Optimization
- Use table `reports/Budget_Optimization_Recommendations.csv`.
- **Visual 1 (Waterfall Chart)**: Current Spend vs Proposed Spend Shifts ($ Delta).
- **KPI Card**: Projected Revenue Uplift (`+12.32%`, `+$237,300.00`).
