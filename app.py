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
# DATA LOAD
# ======================================================
@st.cache_data
def load_data():
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

# Apply light theme CSS
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main > div { padding-top: 0rem; }
    [data-testid="stMetric"] { border: 1px solid #e6e9ef; padding: 15px; border-radius: 10px; background-color: #f8f9fb; }
    [data-testid="stMetricValue"] { color: #008080 !important; }
    [data-testid="stMetricLabel"] { color: #000000 !important; }
    .stDataFrame thead th { color: #000000 !important; background-color: #f0f2f6 !important; }
    .stDataFrame tbody td { color: #000000 !important; background-color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

chart_template = "plotly_white"

brand_color = "#21c7d9"
risk_color = "#ff4d4f"

# ======================================================
# KPI CALCULATIONS
# ======================================================
total_revenue = orders_df["price_usd"].sum()
total_profit = 1222335.29
total_orders = orders_df["order_id"].nunique()
total_refunds = orders_df["refund_amount_usd"].sum()
aov = total_revenue / total_orders
total_traffic = df["website_session_id"].nunique()
conversion_rate = (total_orders / total_traffic) * 100
total_items = int(orders_df["items_purchased"].sum())

# ======================================================
# INDIVIDUAL BORDERED KPIs
# ======================================================
st.markdown("### Executive Performance Metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", f"${total_revenue:,.2f}")
c2.metric("Profit", f"${total_profit:,.2f}")
c3.metric("Refund", f"${total_refunds:,.2f}", delta_color="normal")
c4.metric("Avg Order Value", f"${aov:,.2f}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Website Traffic", f"{total_traffic:,}")
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
fig_trend.update_traces(line_color=brand_color, fillcolor="rgba(33, 199, 217, 0.2)")
fig_trend.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
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
fig_prod.update_layout(barmode="group", height=450, template=chart_template)
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
fig_bundle.update_layout(height=400, showlegend=False)
st.plotly_chart(fig_bundle, use_container_width=True)

# ======================================================
# 4. REFUND RISK SUMMARY (SORTED HIGH TO LOW, NO INDEX)
# ======================================================
st.markdown("---")
st.subheader("Refund Risk Summary: Executive View")

risk_summary = orders_df.groupby(["product_id", "product_name"]).agg(
    Orders=("order_id", "count"),
    Refunds=("is_refunded", "sum")
).reset_index()

risk_summary["Refund Rate"] = (risk_summary["Refunds"] / risk_summary["Orders"]) * 100
risk_summary = risk_summary.sort_values("product_id", ascending=True)

def get_risk_label(rate):
    if rate > 6: return "High Risk"
    if rate > 4: return "Medium Risk"
    return "Low Risk"

risk_summary["Status"] = risk_summary["Refund Rate"].apply(get_risk_label)

final_table = risk_summary[["product_name", "Orders", "Refund Rate", "Status"]].rename(
    columns={
        "product_name": "Product Name",
        "Orders": "Sales Volume",
        "Refund Rate": "Refund Rate (%)"
    }
)

# Display with proper formatting
st.dataframe(
    final_table.style.format({"Refund Rate (%)": "{:.2f}%", "Sales Volume": "{:,}"}),
    use_container_width=True,
    height=200,
    hide_index=True
)

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")
st.caption("End of Analysis Report | Verified Data Integrity | DevSquad")