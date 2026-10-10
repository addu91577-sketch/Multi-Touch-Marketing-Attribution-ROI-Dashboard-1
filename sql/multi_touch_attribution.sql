-- =======================================================================================
-- PRODUCTION MULTI-TOUCH MARKETING ATTRIBUTION & ROI ANALYTICS SCRIPT
-- =======================================================================================
-- Project: Multi-Touch Marketing Attribution ROI Dashboard
-- Description:
--   Resolves date-sorting, sequence inversion, and revenue distribution flaws found
--   in raw SQL queries. Implements 5 deterministic attribution models:
--     1. First-Touch Attribution (FTA)
--     2. Last-Touch Attribution (LTA)
--     3. Linear Attribution (LA)
--     4. Position-Based / U-Shaped Attribution (PBA: 40% First, 40% Last, 20% Middle)
--     5. Time-Decay Attribution (TDA: 7-Day Exponential Half-Life)
--   Also aggregates channel Spend, Conversions, Revenue, Profit, ROAS, ROI %, and CAC.
-- =======================================================================================

-- STEP 1: Parse Timestamps, Re-sequence Journeys Chronologically & Aggregate Customer Metrics
WITH ParsedJourneys AS (
    SELECT
        Customer_ID,
        -- Correctly parse date string to Date object to eliminate alphabetical string sorting errors
        CASE 
            WHEN Touchpoint_Date LIKE '____-__-__%' THEN STR_TO_DATE(SUBSTRING(Touchpoint_Date, 1, 10), '%Y-%m-%d')
            WHEN Touchpoint_Date LIKE '__-__-____%' THEN STR_TO_DATE(SUBSTRING(Touchpoint_Date, 1, 10), '%d-%m-%Y')
            ELSE CAST(Touchpoint_Date AS DATE)
        END AS Parsed_Date,
        Channel,
        Touchpoint_Type,
        Device,
        Country,
        Customer_Segment,
        Product_Category,
        Cost,
        Conversion_Flag,
        Revenue,
        -- Aggregate full customer conversion value across journey
        SUM(Revenue) OVER (PARTITION BY Customer_ID) AS Customer_Total_Revenue,
        MAX(Conversion_Flag) OVER (PARTITION BY Customer_ID) AS Customer_Converted_Flag,
        -- True chronological journey order
        ROW_NUMBER() OVER (
            PARTITION BY Customer_ID 
            ORDER BY 
                CASE 
                    WHEN Touchpoint_Date LIKE '____-__-__%' THEN STR_TO_DATE(SUBSTRING(Touchpoint_Date, 1, 10), '%Y-%m-%d')
                    WHEN Touchpoint_Date LIKE '__-__-____%' THEN STR_TO_DATE(SUBSTRING(Touchpoint_Date, 1, 10), '%d-%m-%Y')
                    ELSE CAST(Touchpoint_Date AS DATE)
                END ASC,
                Cost DESC
        ) AS Journey_Step,
        COUNT(*) OVER (PARTITION BY Customer_ID) AS Journey_Length,
        MAX(CASE 
            WHEN Touchpoint_Date LIKE '____-__-__%' THEN STR_TO_DATE(SUBSTRING(Touchpoint_Date, 1, 10), '%Y-%m-%d')
            WHEN Touchpoint_Date LIKE '__-__-____%' THEN STR_TO_DATE(SUBSTRING(Touchpoint_Date, 1, 10), '%d-%m-%Y')
            ELSE CAST(Touchpoint_Date AS DATE)
        END) OVER (PARTITION BY Customer_ID) AS Last_Touch_Date
    FROM Multi_Touch_Marketing_Attribution_ROI_Dataset
),

-- STEP 2: Compute Multi-Touch Attribution Weights and Attributed Revenues
AttributionCalculations AS (
    SELECT
        Customer_ID,
        Parsed_Date,
        Channel,
        Cost,
        Customer_Total_Revenue,
        Customer_Converted_Flag,
        Journey_Step,
        Journey_Length,
        DATEDIFF(Last_Touch_Date, Parsed_Date) AS Days_To_Conversion,

        -- 1. First-Touch Attribution Weight & Revenue
        CASE 
            WHEN Customer_Converted_Flag = 1 AND Journey_Step = 1 THEN 1.0 
            ELSE 0.0 
        END AS Weight_First_Touch,

        -- 2. Last-Touch Attribution Weight & Revenue
        CASE 
            WHEN Customer_Converted_Flag = 1 AND Journey_Step = Journey_Length THEN 1.0 
            ELSE 0.0 
        END AS Weight_Last_Touch,

        -- 3. Linear Attribution Weight (Equally distributes total customer revenue across all touchpoints)
        CASE 
            WHEN Customer_Converted_Flag = 1 THEN 1.0 / Journey_Length 
            ELSE 0.0 
        END AS Weight_Linear,

        -- 4. Position-Based (U-Shaped: 40% First, 40% Last, 20% Middle)
        CASE
            WHEN Customer_Converted_Flag = 0 THEN 0.0
            WHEN Journey_Length = 1 THEN 1.0
            WHEN Journey_Length = 2 THEN 0.5
            WHEN Journey_Step = 1 THEN 0.40
            WHEN Journey_Step = Journey_Length THEN 0.40
            ELSE 0.20 / (Journey_Length - 2)
        END AS Weight_Position_Based,

        -- 5. Time-Decay Attribution Weight (7-Day Half-Life: Weight = 2^(-Days / 7))
        CASE
            WHEN Customer_Converted_Flag = 1 THEN POW(2.0, -1.0 * DATEDIFF(Last_Touch_Date, Parsed_Date) / 7.0)
            ELSE 0.0
        END AS Raw_Time_Decay_Weight
    FROM ParsedJourneys
),

-- STEP 3: Normalize Time-Decay Weights per Customer
NormalizedAttributions AS (
    SELECT
        a.*,
        SUM(a.Raw_Time_Decay_Weight) OVER (PARTITION BY a.Customer_ID) AS Total_Decay_Weight_Per_Customer,
        CASE 
            WHEN SUM(a.Raw_Time_Decay_Weight) OVER (PARTITION BY a.Customer_ID) > 0 
            THEN a.Raw_Time_Decay_Weight / SUM(a.Raw_Time_Decay_Weight) OVER (PARTITION BY a.Customer_ID)
            ELSE 0.0 
        END AS Weight_Time_Decay
    FROM AttributionCalculations a
),

FinalAttributedTouchpoints AS (
    SELECT
        Customer_ID,
        Parsed_Date,
        Channel,
        Cost,
        Customer_Converted_Flag,
        Journey_Step,
        Journey_Length,
        -- Attributed Revenues
        ROUND(Weight_First_Touch * Customer_Total_Revenue, 2) AS Rev_First_Touch,
        ROUND(Weight_Last_Touch * Customer_Total_Revenue, 2) AS Rev_Last_Touch,
        ROUND(Weight_Linear * Customer_Total_Revenue, 2) AS Rev_Linear,
        ROUND(Weight_Position_Based * Customer_Total_Revenue, 2) AS Rev_Position_Based,
        ROUND(Weight_Time_Decay * Customer_Total_Revenue, 2) AS Rev_Time_Decay,
        -- Attributed Conversions
        Weight_First_Touch AS Conv_First_Touch,
        Weight_Last_Touch AS Conv_Last_Touch,
        Weight_Linear AS Conv_Linear,
        Weight_Position_Based AS Conv_Position_Based,
        Weight_Time_Decay AS Conv_Time_Decay
    FROM NormalizedAttributions
)

-- STEP 4: Executive Channel Performance & ROI Comparison Summary
SELECT
    Channel,
    ROUND(SUM(Cost), 2) AS Total_Spend,
    COUNT(*) AS Total_Touchpoints,
    
    -- First Touch Metrics
    ROUND(SUM(Conv_First_Touch), 2) AS First_Touch_Conversions,
    ROUND(SUM(Rev_First_Touch), 2) AS First_Touch_Revenue,
    ROUND(SUM(Rev_First_Touch) / SUM(Cost), 2) AS First_Touch_ROAS,
    ROUND(((SUM(Rev_First_Touch) - SUM(Cost)) / SUM(Cost)) * 100, 2) AS First_Touch_ROI_Pct,
    ROUND(SUM(Cost) / NULLIF(SUM(Conv_First_Touch), 0), 2) AS First_Touch_CAC,

    -- Last Touch Metrics
    ROUND(SUM(Conv_Last_Touch), 2) AS Last_Touch_Conversions,
    ROUND(SUM(Rev_Last_Touch), 2) AS Last_Touch_Revenue,
    ROUND(SUM(Rev_Last_Touch) / SUM(Cost), 2) AS Last_Touch_ROAS,
    ROUND(((SUM(Rev_Last_Touch) - SUM(Cost)) / SUM(Cost)) * 100, 2) AS Last_Touch_ROI_Pct,
    ROUND(SUM(Cost) / NULLIF(SUM(Conv_Last_Touch), 0), 2) AS Last_Touch_CAC,

    -- Linear Attribution Metrics
    ROUND(SUM(Conv_Linear), 2) AS Linear_Conversions,
    ROUND(SUM(Rev_Linear), 2) AS Linear_Revenue,
    ROUND(SUM(Rev_Linear) / SUM(Cost), 2) AS Linear_ROAS,
    ROUND(((SUM(Rev_Linear) - SUM(Cost)) / SUM(Cost)) * 100, 2) AS Linear_ROI_Pct,
    ROUND(SUM(Cost) / NULLIF(SUM(Conv_Linear), 0), 2) AS Linear_CAC,

    -- Position-Based (U-Shaped) Metrics
    ROUND(SUM(Conv_Position_Based), 2) AS Position_Based_Conversions,
    ROUND(SUM(Rev_Position_Based), 2) AS Position_Based_Revenue,
    ROUND(SUM(Rev_Position_Based) / SUM(Cost), 2) AS Position_Based_ROAS,
    ROUND(((SUM(Rev_Position_Based) - SUM(Cost)) / SUM(Cost)) * 100, 2) AS Position_Based_ROI_Pct,

    -- Time-Decay Metrics
    ROUND(SUM(Conv_Time_Decay), 2) AS Time_Decay_Conversions,
    ROUND(SUM(Rev_Time_Decay), 2) AS Time_Decay_Revenue,
    ROUND(SUM(Rev_Time_Decay) / SUM(Cost), 2) AS Time_Decay_ROAS,
    ROUND(((SUM(Rev_Time_Decay) - SUM(Cost)) / SUM(Cost)) * 100, 2) AS Time_Decay_ROI_Pct
FROM FinalAttributedTouchpoints
GROUP BY Channel
ORDER BY Linear_Revenue DESC;
