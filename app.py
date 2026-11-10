import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Nassau Candy Analytics",
    page_icon="🍬",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("Nassau Candy Distributor.csv")
    df.columns = df.columns.str.strip()

    for col in ["Sales", "Gross Profit", "Units", "Cost"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Order Date"] = pd.to_datetime(
        df["Order Date"], dayfirst=True, errors="coerce"
    )

    return df.drop_duplicates()

df = load_data()

st.title("🍬 Nassau Candy Distributor")
st.subheader("Product Line Profitability & Margin Performance Analysis")

st.sidebar.header("Dashboard Filters")

regions = ["All"] + sorted(df["Region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", regions)

divisions = ["All"] + sorted(df["Division"].dropna().unique().tolist())
selected_division = st.sidebar.selectbox("Select Division", divisions)

filtered_df = df.copy()

if selected_region != "All":
    filtered_df = filtered_df[
        filtered_df["Region"] == selected_region
    ]

if selected_division != "All":
    filtered_df = filtered_df[
        filtered_df["Division"] == selected_division
    ]

revenue = filtered_df["Sales"].sum()
profit = filtered_df["Gross Profit"].sum()
units = filtered_df["Units"].sum()
margin = (profit / revenue * 100) if revenue else 0

st.markdown("### Key Performance Indicators")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Revenue", f"{revenue:,.2f}")
c2.metric("Gross Profit", f"{profit:,.2f}")
c3.metric("Units Sold", f"{units:,.0f}")
c4.metric("Gross Margin", f"{margin:.2f}%")

st.divider()

st.subheader("Product-wise Gross Profit")

product_profit = (
    filtered_df.groupby("Product Name")["Gross Profit"]
    .sum().reset_index()
    .sort_values("Gross Profit", ascending=False)
)

fig1 = px.bar(
    product_profit,
    x="Product Name",
    y="Gross Profit",
    title="Product Profitability",
    color="Gross Profit"
)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Region-wise Sales")

region_sales = (
    filtered_df.groupby("Region")["Sales"]
    .sum().reset_index()
)

fig2 = px.pie(
    region_sales,
    names="Region",
    values="Sales",
    title="Sales Contribution by Region"
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Monthly Revenue Trend")

monthly = (
    filtered_df.dropna(subset=["Order Date"])
    .set_index("Order Date")["Sales"]
    .resample("ME").sum()
    .reset_index()
)

fig3 = px.line(
    monthly,
    x="Order Date",
    y="Sales",
    markers=True,
    title="Monthly Revenue"
)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Division-wise Gross Profit")

division_profit = (
    filtered_df.groupby("Division")["Gross Profit"]
    .sum().reset_index()
)

fig4 = px.bar(
    division_profit,
    x="Division",
    y="Gross Profit",
    color="Division",
    title="Division Performance"
)
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Pareto Analysis")

pareto = (
    filtered_df.groupby("Product Name")["Gross Profit"]
    .sum().sort_values(ascending=False)
    .reset_index()
)

total_profit = pareto["Gross Profit"].sum()

if total_profit > 0:
    pareto["Cumulative Percentage"] = (
        pareto["Gross Profit"].cumsum() / total_profit * 100
    )

    fig5 = px.bar(
        pareto,
        x="Product Name",
        y="Gross Profit",
        title="Product-wise Pareto Analysis"
    )

    fig5.add_scatter(
        x=pareto["Product Name"],
        y=pareto["Cumulative Percentage"],
        name="Cumulative Profit %",
        yaxis="y2"
    )

    fig5.add_hline(y=80, line_dash="dash", line_color="red",
                   yref="y2")

    fig5.update_layout(
        yaxis2=dict(
            overlaying="y",
            side="right",
            range=[0, 105],
            title="Cumulative Profit %"
        ),
        height=600
    )

    st.plotly_chart(fig5, use_container_width=True)

st.subheader("Detailed Dataset")
st.dataframe(filtered_df, use_container_width=True)

st.success("Nassau Candy Analytics Dashboard Loaded Successfully!")