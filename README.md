Cross-Channel Ads Dashboard
A unified analytics dashboard that integrates advertising data from Facebook, Google, and TikTok into a single interactive view. Built with Python and Streamlit.

Live Dashboard
🔗 View Live Dashboard 

Overview
This project was built as part of a multi-channel advertising analysis assignment. It takes raw campaign data from three ad platforms, unifies them into a common data model, and visualizes key performance metrics on a single-page dashboard.
Data period: January 1–30, 2024
Platforms: Facebook Ads, Google Ads, TikTok Ads
Campaigns: 12 total across all platforms

Key Metrics Covered
MetricDescriptionImpressionsNumber of times an ad was displayedClicksNumber of times an ad was clickedCTRClick-Through Rate — clicks ÷ impressionsSpendTotal money spent on adsCPCCost Per Click — spend ÷ clicksConversionsDesired actions completed (purchases, sign-ups, etc.)CVRConversion Rate — conversions ÷ clicksCPACost Per Acquisition — spend ÷ conversions

Dashboard Sections

KPI Cards — Top-level summary: 40.5M impressions, 688K clicks, $130K spend, 13,363 conversions, $9.75 blended CPA
Platform Overview — Side-by-side comparison of Facebook, Google, and TikTok across all 6 core metrics
Daily Spend Trend — 30-day spend line chart by platform
Daily Conversions — 30-day conversion trend by platform
CPA vs CVR — Dual-axis bar chart comparing efficiency across platforms
Spend & Conversion Mix — Donut charts showing budget and result distribution
Campaign Breakdown Table — All 12 campaigns with impressions, clicks, spend, conversions, CPA, CTR, and CVR
TikTok Video Funnel — Watch completion rates from 25% to 100%
Key Insights — 5 data-driven findings with recommendations
Impressions vs CTR — Combo chart showing reach vs. engagement quality per campaign


Project Structure
├── streamlit_dashboard.py   # Main Streamlit app
├── 01_facebook_ads.csv      # Facebook Ads raw data
├── 02_google_ads.csv        # Google Ads raw data
├── 03_tiktok_ads.csv        # TikTok Ads raw data
├── bigquery_setup.sql       # BigQuery DDL + unified view SQL
├── requirements.txt         # Python dependencies
└── README.md

Data Model
Each source table has a slightly different schema. The unified model normalizes them into common columns:
ColumnDescriptiondateDate of the recordplatformFacebook / Google / TikTokcampaign_idOriginal platform campaign IDcampaign_nameCampaign namead_group_idAd set / ad group / adgroup IDad_group_nameAd set / ad group nameimpressionsTotal impressionsclicksTotal clicksspendTotal spend (USD)conversionsTotal conversionsctrComputed: clicks ÷ impressionscpcComputed: spend ÷ clickscvrComputed: conversions ÷ clickscpaComputed: spend ÷ conversions
Platform-specific columns (reach, frequency, quality score, video watch %, likes, shares, etc.) are retained as nullable columns in the BigQuery unified view.

Running Locally
1. Clone the repository
bashgit clone https://github.com/your-username/ads-dashboard.git
cd ads-dashboard
2. Install dependencies
bashpip install -r requirements.txt
3. Run the app
bashstreamlit run streamlit_dashboard.py
4. Open in browser
http://localhost:8501

Deploying to Streamlit Cloud

Push this repository to GitHub (must be public)
Go to share.streamlit.io
Sign in with GitHub
Click New app → select this repo
Set main file path to streamlit_dashboard.py
Click Deploy


BigQuery Setup
The bigquery_setup.sql file contains:

CREATE TABLE statements for all three source tables
LOAD DATA statements to import CSVs from Google Cloud Storage
A CREATE VIEW for the unified unified_ads view
Sample analytical queries

To use it:

Create a BigQuery dataset named ads_data
Upload the three CSV files to a GCS bucket
Update the gs://YOUR_BUCKET/ paths in the SQL file
Run the script in the BigQuery console


Key Findings

Facebook is the most efficient platform at $7.64 CPA, despite receiving only 14% of total budget
Google Search Brand is the top-performing campaign at $5.10 CPA and 5.22% CTR
Facebook Retargeting achieves 6.26% CVR — 3× the blended average
TikTok absorbs 57% of budget but returns only 50% of conversions at $11 CPA
Google Generic Search is the biggest inefficiency at $24.80 CPA — 2.5× the blended rate


Tech Stack

Python — data processing and app logic
Streamlit — dashboard framework
Plotly — interactive charts
Pandas — data aggregation
BigQuery — cloud database and unified data model
SQL — unified view and analytical queries
