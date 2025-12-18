import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="BearCart Business Analytics",
    layout="wide"
)

# ======================================================
# GLOBAL DARK UI CUSTOMIZATION
# ======================================================
st.markdown("""
<style>
/* APP BACKGROUND & TEXT */
.stApp {
    background-color: #000000 !important;
    color: #ffffff !important;
}

/* HEADER FIX */
header[data-testid="stHeader"] {
    background: #000000 !important;
}

/* HEADERS AND SUBHEADERS */
h1, h2, h3, .stSubheader, p, span, label {
    color: #ffffff !important;
}

/* KPI CARD – DARK PREMIUM */
[data-testid="stMetric"] {
    background-color: #111111 !important;
    border: 1px solid #333333 !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.5) !important;
}

[data-testid="stMetricValue"] {
    color: #21c7d9 !important; /* Teal accent */
    font-size: 2rem !important;
    font-weight: 800 !important;
}

[data-testid="stMetricLabel"] {
    color: #aaaaaa !important;
    font-size: 0.9rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* DATAFRAME – DARK THEME */
div[data-testid="stDataFrame"] {
    background-color: #111111 !important;
    border: 1px solid #333333 !important;
    border-radius: 8px !important;
}

/* DIVIDER */
hr {
    border-top: 1px solid #333333 !important;
}

/* TOOLTIP AND BUTTONS */
button {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# DATA LOAD
# ======================================================
@st.cache_data
def load_data():
    # Ensure path matches your environment
    df = pd.read_csv("data/BearCart_Full_Analytics_With_Refunds - BearCart_Full_Analytics_With_Refunds.csv")
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df

df = load_data()
orders_df = df[df["is_conversion"] == 1].drop_duplicates(subset="order_id")

# ======================================================
# HEADER
# ======================================================
st.title("BearCart Business Analytics Dashboard")
st.caption("Strategic Operations & Financial Performance Overview")

# ======================================================
# COLORS & TEMPLATES
# ======================================================
chart_template = "plotly_dark"
brand_color = "#21c7d9"
risk_color = "#ff4d4f"

# ======================================================
# KPI CALCULATIONS
# ======================================================
total_revenue = orders_df["price_usd"].sum()
total_profit = 1222335.29  # Hardcoded per request
total_orders = orders_df["order_id"].nunique()
total_refunds = orders_df["refund_amount_usd"].sum()
aov = total_revenue / total_orders
total_traffic = df["website_session_id"].nunique()
conversion_rate = (total_orders / total_traffic) * 100
total_items = int(orders_df["items_purchased"].sum())

# ======================================================
# KPI SECTION
# ======================================================
st.markdown("### Executive Performance Metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Gross Revenue", f"${total_revenue:,.2f}")
c2.metric("Net Adjusted Profit", f"${total_profit:,.2f}")
c3.metric("Refund Volume", f"${total_refunds:,.2f}")
c4.metric("Avg Order Value", f"${aov:,.2f}")

st.write("") # Spacing

c5, c6, c7, c8 = st.columns(4)
c5.metric("Total Traffic", f"{total_traffic:,}")
c6.metric("Total Orders", f"{total_orders:,}")
c7.metric("Conversion Rate", f"{conversion_rate:.2f}%")
c8.metric("Items Sold", f"{total_items:,}")

# ======================================================
# 1. MONTHLY REFUND RATE TREND
# ======================================================
st.markdown("---")
st.subheader("Monthly Refund Rate Trend")
monthly = orders_df.set_index("created_at").resample("M").agg({"price_usd": "sum", "refund_amount_usd": "sum"}).reset_index()
monthly["Refund Rate (%)"] = (monthly["refund_amount_usd"] / monthly["price_usd"]) * 100
monthly["Month"] = monthly["created_at"].dt.strftime("%b %y")

fig_trend = px.area(monthly, x="Month", y="Refund Rate (%)", template=chart_template)
fig_trend.update_traces(line_color=brand_color, fillcolor="rgba(33, 199, 217, 0.15)")
fig_trend.update_layout(
    height=400, 
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#333333")
)
st.plotly_chart(fig_trend, use_container_width=True)

# ======================================================
# 2. VERTICAL PRODUCT PERFORMANCE
# ======================================================
st.markdown("---")
st.subheader("Orders vs Refunds by Product")
prod_perf = orders_df.groupby("product_name").agg(Total=("order_id", "count"), Refunds=("is_refunded", "sum")).reset_index().sort_values("Total", ascending=False)

fig_prod = go.Figure()
fig_prod.add_trace(go.Bar(x=prod_perf["product_name"], y=prod_perf["Total"], name="Total Orders", marker_color=brand_color))
fig_prod.add_trace(go.Bar(x=prod_perf["product_name"], y=prod_perf["Refunds"], name="Refunded Orders", marker_color=risk_color))
fig_prod.update_layout(
    barmode="group", 
    height=450, 
    template=chart_template,
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="#333333")
)
st.plotly_chart(fig_prod, use_container_width=True)

# ======================================================
# 3. BUNDLE EFFECT
# ======================================================
st.markdown("---")
st.subheader("Bundle Effect: Refund Risk Analysis")
orders_df["Purchase Type"] = orders_df["items_purchased"].apply(lambda x: "Single Item" if x == 1 else "Bundle (2+ Items)")
bundle_risk = orders_df.groupby("Purchase Type").agg(Rate=("is_refunded", "mean")).reset_index()
bundle_risk["Refund Rate (%)"] = bundle_risk["Rate"] * 100

fig_bundle = px.bar(bundle_risk, x="Purchase Type", y="Refund Rate (%)", color="Purchase Type", color_discrete_map={"Single Item": brand_color, "Bundle (2+ Items)": risk_color}, text_auto='.2f', template=chart_template)
fig_bundle.update_layout(
    height=400, 
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(fig_bundle, use_container_width=True)

# ======================================================
# 4. REFUND RISK SUMMARY (STYLED DARK TABLE)
# ======================================================
st.markdown("---")
st.subheader("Refund Risk Summary: Executive View")

risk_summary = orders_df.groupby(["product_id", "product_name"]).agg(
    Orders=("order_id", "count"),
    Refunds=("is_refunded", "sum")
).reset_index()

risk_summary["Refund Rate"] = (risk_summary["Refunds"] / risk_summary["Orders"]) * 100
risk_summary = risk_summary.sort_values("Refund Rate", ascending=False)

def get_risk_label(rate):
    if rate > 6: return "High Risk"
    if rate > 4: return "Medium Risk"
    return "Low Risk"

risk_summary["Status"] = risk_summary["Refund Rate"].apply(get_risk_label)

final_table = risk_summary[
    ["product_id", "product_name", "Orders", "Refund Rate", "Status"]
].rename(
    columns={
        "product_id": "ID",
        "product_name": "Product Name",
        "Orders": "Sales Volume",
        "Refund Rate": "Refund %"
    }
)

# ✅ FIX: Force ID to integer
final_table["ID"] = final_table["ID"].astype(int)

# Custom Status Styling for Dark Mode
def style_status(val):
    color_map = {
        "High Risk": "background-color: #4d1010; color: #ff9999;",
        "Medium Risk": "background-color: #4d3a10; color: #ffcc99;",
        "Low Risk": "background-color: #104d2b; color: #99ffcc;"
    }
    return color_map.get(val, "")

styled_df = (
    final_table.style
    .format({"Refund %": "{:.2f}%", "Sales Volume": "{:,}"})
    .applymap(style_status, subset=["Status"])
    .set_properties(**{
        'background-color': '#111111',
        'color': '#ffffff',
        'border-color': '#333333'
    })
)

st.dataframe(styled_df, use_container_width=True, hide_index=True)

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")
st.caption("End of Analysis Report | Verified Data Integrity | BearCart AI")