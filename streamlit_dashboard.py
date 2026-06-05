import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
 
# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cross-Channel Ads Dashboard",
    page_icon="📊",
    layout="wide",
)
 
# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    [data-testid="metric-container"] {
        background: #1a1d27;
        border: 1px solid #2e3348;
        border-radius: 10px;
        padding: 14px 16px;
    }
    [data-testid="metric-container"] label { color: #8892aa !important; font-size: 11px !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 22px !important; }
    .insight-good  { background:#0d2e1a; border-left:4px solid #22c55e; padding:10px 14px; border-radius:6px; margin-bottom:8px; font-size:13px; line-height:1.6 }
    .insight-warn  { background:#2e2005; border-left:4px solid #f59e0b; padding:10px 14px; border-radius:6px; margin-bottom:8px; font-size:13px; line-height:1.6 }
    .insight-bad   { background:#2e0d0d; border-left:4px solid #ef4444; padding:10px 14px; border-radius:6px; margin-bottom:8px; font-size:13px; line-height:1.6 }
    .plat-card     { border-radius:10px; padding:16px 18px; margin-bottom:4px }
    .plat-card-fb  { background:#1877f210; border:1px solid #1877f240 }
    .plat-card-gg  { background:#ea433510; border:1px solid #ea433540 }
    .plat-card-tt  { background:#ff005010; border:1px solid #ff005040 }
    h1 { font-size: 22px !important; }
    .stDataFrame { font-size: 12px; }
</style>
""", unsafe_allow_html=True)
 
# ── COLORS ────────────────────────────────────────────────────────────────────
FB  = "#1877f2"
GG  = "#ea4335"
TT  = "#ff0050"
PLAT_COLORS = {"Facebook": FB, "Google": GG, "TikTok": TT}
 
# rgba fill helpers (Plotly requires rgba(), not 8-digit hex)
FB_FILL  = "rgba(24,119,242,0.12)"
GG_FILL  = "rgba(234,67,53,0.12)"
TT_FILL  = "rgba(255,0,80,0.12)"
PLAT_FILL = {"Facebook": FB_FILL, "Google": GG_FILL, "TikTok": TT_FILL}
 
FB_FILL2  = "rgba(24,119,242,0.08)"
GG_FILL2  = "rgba(234,67,53,0.08)"
TT_FILL2  = "rgba(255,0,80,0.08)"
PLAT_FILL2 = {"Facebook": FB_FILL2, "Google": GG_FILL2, "TikTok": TT_FILL2}
 
# Bar colors with opacity
FB_BAR  = "rgba(24,119,242,0.80)"
GG_BAR  = "rgba(234,67,53,0.80)"
TT_BAR  = "rgba(255,0,80,0.80)"
PLAT_BAR = {"Facebook": FB_BAR, "Google": GG_BAR, "TikTok": TT_BAR}
 
FB_BAR2  = "rgba(24,119,242,0.33)"
GG_BAR2  = "rgba(234,67,53,0.33)"
TT_BAR2  = "rgba(255,0,80,0.33)"
PLAT_BAR2 = {"Facebook": FB_BAR2, "Google": GG_BAR2, "TikTok": TT_BAR2}
 
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#1a1d27",
    font=dict(color="#8892aa", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
)
LEGEND = dict(bgcolor="rgba(0,0,0,0)", borderwidth=0)
 
# Default axis styles — applied individually per chart to avoid key conflicts
XAXIS = dict(gridcolor="rgba(46,51,72,0.12)", linecolor="#2e3348")
YAXIS = dict(gridcolor="rgba(46,51,72,0.25)", linecolor="#2e3348")
 
# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    fb = pd.read_csv("01_facebook_ads.csv", parse_dates=["date"])
    gg = pd.read_csv("02_google_ads.csv",   parse_dates=["date"])
    tt = pd.read_csv("03_tiktok_ads.csv",   parse_dates=["date"])
 
    # Rename spend columns to a common name
    gg = gg.rename(columns={"cost": "spend"})
    tt = tt.rename(columns={"cost": "spend"})
 
    # Add platform column
    fb["platform"] = "Facebook"
    gg["platform"] = "Google"
    tt["platform"] = "TikTok"
 
    # Unified columns present in all three
    common = ["date", "platform", "campaign_id", "campaign_name",
              "impressions", "clicks", "spend", "conversions"]
 
    unified = pd.concat([fb[common], gg[common], tt[common]], ignore_index=True)
 
    # Computed metrics
    unified["ctr"] = unified["clicks"]       / unified["impressions"]
    unified["cpc"] = unified["spend"]        / unified["clicks"]
    unified["cvr"] = unified["conversions"]  / unified["clicks"]
    unified["cpa"] = unified["spend"]        / unified["conversions"]
 
    return fb, gg, tt, unified
 
fb, gg, tt, unified = load_data()
 
# ── DERIVED AGGREGATES ────────────────────────────────────────────────────────
plat_totals = (
    unified.groupby("platform")
    .agg(impressions=("impressions","sum"), clicks=("clicks","sum"),
         spend=("spend","sum"), conversions=("conversions","sum"))
    .assign(
        ctr  = lambda d: d.clicks / d.impressions * 100,
        cpc  = lambda d: d.spend  / d.clicks,
        cvr  = lambda d: d.conversions / d.clicks * 100,
        cpa  = lambda d: d.spend  / d.conversions,
    )
    .reset_index()
)
 
grand = dict(
    impressions = unified.impressions.sum(),
    clicks      = unified.clicks.sum(),
    spend       = unified.spend.sum(),
    conversions = unified.conversions.sum(),
)
grand["ctr"] = grand["clicks"] / grand["impressions"] * 100
grand["cvr"] = grand["conversions"] / grand["clicks"] * 100
grand["cpa"] = grand["spend"] / grand["conversions"]
 
daily = (
    unified.groupby(["date","platform"])
    .agg(spend=("spend","sum"), conversions=("conversions","sum"))
    .reset_index()
)
 
camp = (
    unified.groupby(["platform","campaign_name"])
    .agg(impressions=("impressions","sum"), clicks=("clicks","sum"),
         spend=("spend","sum"), conversions=("conversions","sum"))
    .assign(
        ctr = lambda d: d.clicks       / d.impressions * 100,
        cvr = lambda d: d.conversions  / d.clicks * 100,
        cpa = lambda d: d.spend        / d.conversions,
    )
    .reset_index()
    .sort_values("conversions", ascending=False)
)
 
video_views_fb = int(fb.video_views.sum())
video_views_tt = int(tt.video_views.sum())
w25  = int(tt.video_watch_25.sum())
w50  = int(tt.video_watch_50.sum())
w75  = int(tt.video_watch_75.sum())
w100 = int(tt.video_watch_100.sum())
 
# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Cross-Channel Ads Dashboard")
st.caption("Facebook · Google · TikTok  |  January 2024 (30 days)  |  3 Platforms · 12 Campaigns")
st.divider()
 
# ── KPI CARDS ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Impressions",   f"{grand['impressions']/1e6:.1f}M")
k2.metric("Clicks",        f"{grand['clicks']/1e3:.0f}K")
k3.metric("Total Spend",   f"${grand['spend']:,.0f}")
k4.metric("Conversions",   f"{grand['conversions']:,}")
k5.metric("Blended CPA",   f"${grand['cpa']:.2f}")
k6.metric("Video Views",   f"{(video_views_fb+video_views_tt)/1e6:.1f}M")
 
st.divider()
 
# ── PLATFORM SUMMARY CARDS ────────────────────────────────────────────────────
st.subheader("Platform Overview")
p1, p2, p3 = st.columns(3)
 
def plat_card(col, row, emoji, cls):
    with col:
        st.markdown(f"""
        <div class="plat-card {cls}">
          <b>{emoji} {row['platform']}</b><br><br>
          <table width="100%" style="font-size:13px">
            <tr><td style="color:#8892aa">Spend</td>       <td align="right"><b>${row['spend']:,.0f}</b></td>
                <td style="color:#8892aa">Conversions</td> <td align="right"><b>{row['conversions']:,}</b></td></tr>
            <tr><td style="color:#8892aa">CPA</td>         <td align="right"><b>${row['cpa']:.2f}</b></td>
                <td style="color:#8892aa">CVR</td>         <td align="right"><b>{row['cvr']:.2f}%</b></td></tr>
            <tr><td style="color:#8892aa">CTR</td>         <td align="right"><b>{row['ctr']:.2f}%</b></td>
                <td style="color:#8892aa">CPC</td>         <td align="right"><b>${row['cpc']:.2f}</b></td></tr>
          </table>
        </div>
        """, unsafe_allow_html=True)
 
fb_row = plat_totals[plat_totals.platform=="Facebook"].iloc[0]
gg_row = plat_totals[plat_totals.platform=="Google"].iloc[0]
tt_row = plat_totals[plat_totals.platform=="TikTok"].iloc[0]
 
plat_card(p1, fb_row, "📘", "plat-card-fb")
plat_card(p2, gg_row, "🔍", "plat-card-gg")
plat_card(p3, tt_row, "🎵", "plat-card-tt")
 
st.divider()
 
# ── DAILY SPEND LINE CHART ────────────────────────────────────────────────────
st.subheader("Daily Spend by Platform")
fig_spend = go.Figure()
for plat, color in PLAT_COLORS.items():
    d = daily[daily.platform == plat].sort_values("date")
    fig_spend.add_trace(go.Scatter(
        x=d.date, y=d.spend, name=plat,
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=PLAT_FILL[plat],
        mode="lines", hovertemplate=f"<b>{plat}</b><br>%{{x|%b %d}}<br>Spend: $%{{y:,.0f}}<extra></extra>"
    ))
fig_spend.update_layout(**PLOTLY_LAYOUT, height=280, hovermode="x unified",
    legend=LEGEND, xaxis=XAXIS, yaxis=dict(**YAXIS, tickprefix="$"))
st.plotly_chart(fig_spend, use_container_width=True)
 
# ── DAILY CONVERSIONS + CPA vs CVR ───────────────────────────────────────────
col_conv, col_cpa = st.columns(2)
 
with col_conv:
    st.subheader("Daily Conversions")
    fig_conv = go.Figure()
    for plat, color in PLAT_COLORS.items():
        d = daily[daily.platform == plat].sort_values("date")
        fig_conv.add_trace(go.Scatter(
            x=d.date, y=d.conversions, name=plat,
            line=dict(color=color, width=2),
            fill="tozeroy", fillcolor=PLAT_FILL2[plat],
            mode="lines", hovertemplate=f"<b>{plat}</b><br>%{{x|%b %d}}<br>Conversions: %{{y:,}}<extra></extra>"
        ))
    fig_conv.update_layout(**PLOTLY_LAYOUT, height=260, hovermode="x unified",
        legend=LEGEND, xaxis=XAXIS, yaxis=YAXIS)
    st.plotly_chart(fig_conv, use_container_width=True)
 
with col_cpa:
    st.subheader("CPA vs CVR by Platform")
    fig_cpa = make_subplots(specs=[[{"secondary_y": True}]])
    platforms = plat_totals.platform.tolist()
    colors    = [PLAT_COLORS[p] for p in platforms]
    fig_cpa.add_trace(go.Bar(
        x=platforms, y=plat_totals.cpa, name="CPA ($)",
        marker_color=[PLAT_BAR[p] for p in platforms],
        marker_cornerradius=4,
        hovertemplate="CPA: $%{y:.2f}<extra></extra>"
    ), secondary_y=False)
    fig_cpa.add_trace(go.Bar(
        x=platforms, y=plat_totals.cvr, name="CVR (%)",
        marker_color=[PLAT_BAR2[p] for p in platforms],
        marker_cornerradius=4,
        hovertemplate="CVR: %{y:.2f}%<extra></extra>"
    ), secondary_y=True)
    fig_cpa.update_layout(**PLOTLY_LAYOUT, height=260,
        legend=LEGEND, barmode="group", xaxis=XAXIS)
    fig_cpa.update_yaxes(tickprefix="$", secondary_y=False,
        gridcolor="rgba(46,51,72,0.25)", linecolor="#2e3348")
    fig_cpa.update_yaxes(ticksuffix="%", secondary_y=True,
        gridcolor="rgba(0,0,0,0)", linecolor="#2e3348")
    st.plotly_chart(fig_cpa, use_container_width=True)
 
# ── SPEND MIX + CONVERSION MIX ───────────────────────────────────────────────
col_sp, col_cv = st.columns(2)
 
def donut(title, values, col):
    with col:
        st.subheader(title)
        fig = go.Figure(go.Pie(
            labels=plat_totals.platform,
            values=values,
            hole=0.65,
            marker=dict(colors=list(PLAT_COLORS.values()), line=dict(width=0)),
            hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
            textinfo="none",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=240,
            legend=dict(**LEGEND, orientation="h", yanchor="bottom", y=-0.15,
                        xanchor="center", x=0.5))
        st.plotly_chart(fig, use_container_width=True)
 
donut("Spend Mix",      plat_totals.spend,       col_sp)
donut("Conversion Mix", plat_totals.conversions, col_cv)
 
st.divider()
 
# ── CAMPAIGN TABLE ────────────────────────────────────────────────────────────
st.subheader("Campaign Performance Breakdown")
 
def color_cpa(val):
    if val <= 7:   return "color: #22c55e"
    if val <= 12:  return "color: #e8eaf0"
    return "color: #ef4444"
 
def color_cvr(val):
    if val >= 4:  return "color: #22c55e"
    if val >= 2:  return "color: #e8eaf0"
    return "color: #f59e0b"
 
display = camp.copy()
display["impressions"] = display["impressions"].apply(lambda v: f"{v/1e6:.2f}M")
display["clicks"]      = display["clicks"].apply(lambda v: f"{v:,}")
display["spend"]       = display["spend"].apply(lambda v: f"${v:,.0f}")
display["conversions"] = display["conversions"].apply(lambda v: f"{v:,}")
display["ctr"]         = display["ctr"].apply(lambda v: f"{v:.2f}%")
display["cpa_raw"]     = camp["cpa"]
display["cvr_raw"]     = camp["cvr"]
display["cpa"]         = display["cpa"].apply(lambda v: f"${v:.2f}")
display["cvr"]         = display["cvr"].apply(lambda v: f"{v:.2f}%")
display = display.rename(columns={
    "platform":"Platform","campaign_name":"Campaign",
    "impressions":"Impressions","clicks":"Clicks",
    "spend":"Spend","conversions":"Conversions","cpa":"CPA","ctr":"CTR","cvr":"CVR"
})[["Platform","Campaign","Impressions","Clicks","Spend","Conversions","CPA","CTR","CVR"]]
 
st.dataframe(
    display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Platform":    st.column_config.TextColumn(width="small"),
        "Campaign":    st.column_config.TextColumn(width="medium"),
        "Impressions": st.column_config.TextColumn(width="small"),
        "Clicks":      st.column_config.TextColumn(width="small"),
        "Spend":       st.column_config.TextColumn(width="small"),
        "Conversions": st.column_config.TextColumn(width="small"),
        "CPA":         st.column_config.TextColumn(width="small"),
        "CTR":         st.column_config.TextColumn(width="small"),
        "CVR":         st.column_config.TextColumn(width="small"),
    }
)
 
st.divider()
 
# ── TIKTOK VIDEO FUNNEL + KEY INSIGHTS ───────────────────────────────────────
col_funnel, col_insights = st.columns(2)
 
with col_funnel:
    st.subheader("TikTok Video View Funnel")
    funnel_labels  = ["Video Views", "Watched 25%", "Watched 50%", "Watched 75%", "Watched 100%"]
    funnel_values  = [video_views_tt, w25, w50, w75, w100]
    funnel_pcts    = [v / video_views_tt * 100 for v in funnel_values]
 
    fig_funnel = go.Figure()
    fig_funnel.add_trace(go.Bar(
        x=funnel_values,
        y=funnel_labels,
        orientation="h",
        marker=dict(
            color=[f"rgba(255,0,80,{0.9 - i*0.15})" for i in range(5)],
            cornerradius=4,
        ),
        text=[f"{v/1e6:.1f}M  ({p:.0f}%)" for v, p in zip(funnel_values, funnel_pcts)],
        textposition="outside",
        hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
    ))
    fig_funnel.update_layout(
        **PLOTLY_LAYOUT, height=300, showlegend=False,
        xaxis=dict(showticklabels=False, gridcolor="rgba(0,0,0,0)", linecolor="#2e3348"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", linecolor="#2e3348",
                   categoryorder="array", categoryarray=funnel_labels[::-1]),
    )
    st.plotly_chart(fig_funnel, use_container_width=True)
    st.caption(f"Facebook video views: {video_views_fb/1e6:.1f}M (brand awareness + video campaigns)")
 
with col_insights:
    st.subheader("Key Insights")
    st.markdown("""
    <div class="insight-good">
      <b>Google Search Brand wins on CPA.</b> Search Brand Terms converts at <b>$5.10 CPA</b>
      with a 5.22% CTR — the highest intent, lowest cost channel in the account.
    </div>
    <div class="insight-good">
      <b>Facebook Retargeting punches above its weight.</b> Conversions Retargeting achieves
      <b>6.26% CVR</b> — 3× the blended average — on just 14% of total spend.
    </div>
    <div class="insight-warn">
      <b>TikTok drives volume, not efficiency.</b> 57% of budget delivers 50% of conversions
      at a <b>$11 CPA</b>, above the $9.75 blended rate. Strong for awareness, not for ROI.
    </div>
    <div class="insight-bad">
      <b>Google Generic Search is expensive.</b> $24.80 CPA — 2.5× the blended rate.
      Needs keyword pruning or bid reduction immediately.
    </div>
    <div class="insight-good">
      <b>TikTok video retention is strong.</b> 26% of viewers watch to 100% completion —
      signals high creative quality on Influencer and Dance Challenge ad sets.
    </div>
    """, unsafe_allow_html=True)
 
st.divider()
 
# ── IMPRESSIONS vs CTR ────────────────────────────────────────────────────────
st.subheader("Impressions vs CTR by Campaign")
 
fig_imp = make_subplots(specs=[[{"secondary_y": True}]])
 
bar_colors = [PLAT_BAR[p] for p in camp.platform]
 
fig_imp.add_trace(go.Bar(
    x=camp.campaign_name.str.replace("_", " "),
    y=camp.impressions,
    name="Impressions",
    marker=dict(color=bar_colors, cornerradius=4),
    hovertemplate="<b>%{x}</b><br>Impressions: %{y:,.0f}<extra></extra>",
), secondary_y=False)
 
fig_imp.add_trace(go.Scatter(
    x=camp.campaign_name.str.replace("_", " "),
    y=camp.ctr,
    name="CTR (%)",
    line=dict(color="#f59e0b", width=2),
    marker=dict(size=7, color="#f59e0b"),
    mode="lines+markers",
    hovertemplate="<b>%{x}</b><br>CTR: %{y:.2f}%<extra></extra>",
), secondary_y=True)
 
fig_imp.update_layout(
    **PLOTLY_LAYOUT, height=320, hovermode="x unified",
    legend=LEGEND,
    xaxis=dict(tickangle=-30, gridcolor="rgba(46,51,72,0.12)", linecolor="#2e3348"),
)
fig_imp.update_yaxes(
    secondary_y=False,
    gridcolor="rgba(46,51,72,0.25)", linecolor="#2e3348",
    tickvals=[2e6, 4e6, 6e6, 8e6, 10e6],
    ticktext=["2M","4M","6M","8M","10M"],
)
fig_imp.update_yaxes(
    ticksuffix="%",
    secondary_y=True,
    gridcolor="rgba(0,0,0,0)", linecolor="#2e3348",
)
st.plotly_chart(fig_imp, use_container_width=True)
 
# ── FOOTER ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Data: Facebook Ads · Google Ads · TikTok Ads  |  Period: January 1–30, 2024")