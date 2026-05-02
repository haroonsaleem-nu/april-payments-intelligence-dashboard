import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="April Payments Intelligence Dashboard", layout="wide")

# Load data
df = pd.read_excel("April Payments.xlsx")
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
df = df.dropna(how="all")
df.columns = ["Date", "Customer", "Agent", "Amount", "Bank", "Type"]

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df = df.dropna(subset=["Date", "Amount"])

# Filter April 2026
df = df[(df["Date"].dt.year == 2026) & (df["Date"].dt.month == 4)]

st.title("April Payments Intelligence Dashboard")
st.caption("Revenue performance, customer behavior, agent productivity, and payment channel insights.")

# Sidebar filters
st.sidebar.header("Filters")
agents = st.sidebar.multiselect("Select Agent", sorted(df["Agent"].dropna().unique()), default=sorted(df["Agent"].dropna().unique()))
banks = st.sidebar.multiselect("Select Bank", sorted(df["Bank"].dropna().unique()), default=sorted(df["Bank"].dropna().unique()))
types = st.sidebar.multiselect("Select Type", sorted(df["Type"].dropna().unique()), default=sorted(df["Type"].dropna().unique()))

filtered = df[
    (df["Agent"].isin(agents)) &
    (df["Bank"].isin(banks)) &
    (df["Type"].isin(types))
]

# KPIs
total_revenue = filtered["Amount"].sum()
transactions = len(filtered)
avg_payment = filtered["Amount"].mean()
top_agent = filtered.groupby("Agent")["Amount"].sum().idxmax() if not filtered.empty else "N/A"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"{total_revenue:,.2f}")
c2.metric("Transactions", transactions)
c3.metric("Average Payment", f"{avg_payment:,.2f}")
c4.metric("Top Agent", top_agent)

st.divider()

# Charts
daily = filtered.groupby("Date", as_index=False)["Amount"].sum()
agent_perf = filtered.groupby("Agent", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False)
bank_perf = filtered.groupby("Bank", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False)
type_perf = filtered.groupby("Type", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False)
customer_perf = filtered.groupby("Customer", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False).head(10)

col1, col2 = st.columns(2)

with col1:
    fig = px.line(daily, x="Date", y="Amount", markers=True, title="Daily Revenue Trend")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(agent_perf, x="Agent", y="Amount", title="Agent Performance")
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig = px.pie(bank_perf, names="Bank", values="Amount", title="Revenue by Bank")
    st.plotly_chart(fig, use_container_width=True)

with col4:
    fig = px.bar(type_perf, x="Type", y="Amount", title="Revenue by Payment Type")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Top 10 Customers by Revenue")
fig = px.bar(customer_perf, x="Customer", y="Amount", title="Top Customers")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Business Insights")
st.write("""
- Revenue is concentrated across limited banking channels, creating operational dependency risk.
- Top-performing agents contribute significantly to total revenue.
- Initial payments dominate the revenue mix, showing strong new-client inflow.
- Remaining payments represent a conversion opportunity for improving cash recovery.
- High-value customers have strong impact on overall revenue performance.
""")

st.subheader("Filtered Dataset")
st.dataframe(filtered, use_container_width=True)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download Filtered Data", csv, "filtered_april_payments.csv", "text/csv")