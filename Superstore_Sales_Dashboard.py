import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt

st.set_page_config(
    page_title="Superstore Sales Intelligence",
    page_icon="🏬",
    layout="wide"
)

def load_data():
    df = pd.read_csv("Superstore_Data.csv")  # Make sure this matches your file name
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed", errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="mixed", errors="coerce")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Error: 'Superstore_Data.csv' not found. Please place it in the same directory.")
    st.stop()

sidebar = st.sidebar

def show_home():
    st.title("🏬 Superstore Sales Intelligence")
    st.markdown("""
    <p style='font-size:17px; color:gray;'>
    An interactive business intelligence dashboard built on 4 years of US Superstore 
    retail transaction data. Explore sales performance across product categories, 
    customer segments, regions, and shipping behavior — with dynamic filters to 
    drill down into the data and surface actionable business insights.
    </p>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("**Dataset**: US Superstore Sales (Rohit Sahoo · Kaggle)")
    st.markdown("**Style**: Business Intelligence Report")
    st.markdown("**Tools**: Python · Pandas · Plotly · Altair · Streamlit")
    st.header("🎯 Objective")
    st.write("Analyze 4 years of retail transaction data to uncover patterns in **sales performance**, **customer segments**, and **regional trends** — and surface actionable business insights")
    st.header("Executive Summary")
    st.write("This analysis of Superstore sales data reveals a business driven primarily by the Consumer segment, which accounts for over half of total revenue, followed by Corporate (30.4%) and Home Office (18.8%). The Technology category leads in average sales per order, with Copiers and Machines standing out as the top-performing sub-categories. Geographically, sales are concentrated in a few key markets — Florida leads among all states while Jacksonville tops the city rankings — and the South region generates the highest overall sales volume, though with notable variability compared to other regions. Shipping behavior reveals an interesting gap: while Standard Class is overwhelmingly the most used shipping mode, Same Day delivery consistently yields the highest average order value, suggesting an untapped opportunity to promote faster shipping options to high-value customers. Finally, sales follow a strong and consistent seasonal pattern, peaking every September and November — likely driven by back-to-school and holiday demand — with predictable dips in February and October. These seasonal trends offer clear signals for inventory planning, promotional timing, and marketing campaigns.")
    st.divider()
    st.header("Dataset Overview")
    st.dataframe(df.head(50))
    data_col1, data_col2, data_col3 = st.columns([2,2,3])
    with data_col1:
        st.metric(label="**Total Rows**", value=f"{df.shape[0]:,}")
    with data_col2:
        st.metric(label="**Total Columns**", value=f"{df.shape[1]:,}")
    with data_col3:
        st.metric(label="**Date Range**", value=f"{df['Order Date'].min().date()} to {df['Order Date'].max().date()}")
    st.divider()
    st.header("📌 Quick KPIs")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="💰**Total Revenue**", value=f"${df['Sales'].sum():,.2f}")
    with col2:
        st.metric(label="📦**Total Orders**", value=f"{df['Order ID'].nunique():,}")
    with col3:
        st.metric(label="📊**Average Order Value**", value=f"${df['Sales'].mean():,.2f}")
    with col4:
        st.metric(label="🏆**Most Popular Category**", value=f"{df['Category'].mode()[0]}")


def show_overview():
    st.title("📊 Sales Overview")
    st.markdown("High-level performance indicators and transactional health metrics.")
    category_select = sidebar.multiselect("Filter by Category", options=df["Category"].unique(),default=df['Category'].unique(), key="Category_filter")
    segment_select = sidebar.multiselect("Filter by Segment", options=df['Segment'].unique(), default=df['Segment'].unique(), key="Segment_filter")
    sub_category_select = sidebar.multiselect("Filter by Sub-Category", options=df["Sub-Category"].unique(),default=df['Sub-Category'].unique(), key="Sub-Category_filter")
    filtered_df = df[df["Category"].isin(category_select) & df["Segment"].isin(segment_select) & df["Sub-Category"].isin(sub_category_select)]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰**Total Sales**", value=f"${filtered_df['Sales'].sum():,.2f}")
    with col2:
        st.metric(label="📦**Total Orders**", value=f"{filtered_df['Order ID'].nunique():,}")
    with col3:
        st.metric(label="📊**Average Order Value**", value=f"${filtered_df['Sales'].mean():,.2f}")
    st.divider()
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("Sales by Category")
        if not category_select:
            st.warning("Please select at least one category.")
        else:
            filtered_df = df[df["Category"].isin(category_select)]
            sales_by_category = filtered_df.groupby("Category", as_index=False)["Sales"].sum()
            st.bar_chart(data= sales_by_category, x="Category", y="Sales")
    with chart_col2:
        st.subheader("Sales by Segment")
        if not segment_select:
            st.warning("Please select at least one segment.")
        else:
            filtered_df = df[df["Segment"].isin(segment_select)]
            sales_by_segment = filtered_df.groupby("Segment", as_index=False)["Sales"].sum()
            if not sales_by_segment.empty:
                fig = px.pie(sales_by_segment, values="Sales", names="Segment")
                fig.update_traces(textinfo="percent+label", hoverinfo="label+value+percent")
                st.plotly_chart(fig, width='stretch')
    st.divider()
    st.subheader("Sales by Sub-Category")
    if not sub_category_select:
        st.warning("Please select at least one sub-category.")
    else:
        filtered_df = df[df["Sub-Category"].isin(sub_category_select)]
        sales_by_sub_category = filtered_df.groupby("Sub-Category")["Sales"].sum().reset_index().sort_values(by="Sales", ascending=False).reset_index(drop=True)
        st.bar_chart(data=sales_by_sub_category, x="Sub-Category", y="Sales", sort="-Sales")
    st.divider()
    st.info("Technology leads all categories in average sales per order, while Office Supplies drives the highest transaction volume. Phones and Chairs are the standout sub-categories. The Consumer segment accounts for the majority of revenue across all filters.")


def show_region_analytics():
    st.title("🌍 Regional Analysis")
    top_10_states = df.groupby("State")["Sales"].sum().nlargest(10).index.tolist()
    bottom_10_states = df.groupby("State")["Sales"].sum().nsmallest(10).index.tolist()
    top_10_cities = df.groupby("City")["Sales"].sum().nlargest(10).index.tolist()
    bottom_10_cities = df.groupby("City")["Sales"].sum().nsmallest(10).index.tolist()
    if "State_filter" not in st.session_state:
        st.session_state.State_filter = top_10_states
    if "City_filter" not in st.session_state:
        st.session_state.City_filter = top_10_cities
    region_select = sidebar.multiselect("Filter by Region", options=df["Region"].unique(), default=df['Region'].unique(), key="Region_filter")
    sidebar.markdown("**State Shortcuts:**")
    sc_col1, sc_col2 = sidebar.columns(2)
    with sc_col1:
        if sidebar.button("🏆 Top 10 States", key="btn_st_top10"):
            st.session_state.State_filter = top_10_states
    with sc_col2:
        if sidebar.button("📉 Bottom 10 States", key="btn_st_bot10"):
            st.session_state.State_filter = bottom_10_states
    state_select = sidebar.multiselect("Filter by State", options=sorted(df['State'].unique()), max_selections=10, key="State_filter")
    sidebar.markdown("**City Shortcuts:**")
    with sc_col1:
        if sidebar.button("🏆 Top 10 Cities", key="btn_ci_top10"):
            st.session_state.City_filter = top_10_cities
    with sc_col2:
        if sidebar.button("📉 Bottom 10 Cities", key="btn_ci_bot10"):
            st.session_state.City_filter = bottom_10_cities
    city_select = sidebar.multiselect("Filter by City", options=df['City'].unique(), max_selections=10, key="City_filter")
    st.subheader("Sales by Region")
    if not region_select:
        st.warning("Please select at least region.")
    else:
        filtered_df = df[df["Region"].isin(region_select)]
        sales_by_region = filtered_df.groupby("Region")["Sales"].sum().reset_index().sort_values(by="Sales", ascending=False).reset_index(drop=True)
        st.bar_chart(data=sales_by_region, x="Region", y="Sales")
    st.divider()
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("Sales by State")
        if not state_select:
            st.warning("Please select at least one state.")
        else:
            filtered_df = df[df["State"].isin(state_select)]
            sales_by_state = filtered_df.groupby("State", as_index=False)["Sales"].sum().sort_values(by="Sales", ascending=False).reset_index(drop=True)
            chart = alt.Chart(sales_by_state).mark_bar().encode(x='Sales:Q', y=alt.Y('State:N', sort='-x'))
            st.altair_chart(chart)         
    with chart_col2:
        st.subheader("Sales by City")
        if not city_select:
            st.warning("Please select at least one city.")
        else:
            filtered_df = df[df["City"].isin(city_select)]
            sales_by_city = filtered_df.groupby("City", as_index=False)["Sales"].sum().sort_values(by="Sales", ascending=False).reset_index(drop=True)
            chart = alt.Chart(sales_by_city).mark_bar().encode(x='Sales:Q', y=alt.Y('City:N', sort='-x'))
            st.altair_chart(chart)  
    st.divider()
    st.info("The West region generates the highest overall sales volume. California leads all states in total sales, with New York City topping the city rankings. Sales are heavily concentrated in a small number of markets, suggesting potential for geographic expansion.")


def show_shipping_analytics():
    st.title("🚢 Shipping Analysis")
    shipmode_select = sidebar.multiselect("Filter by Ship Mode", options=df["Ship Mode"].unique(),default=df['Ship Mode'].unique(), key="shipmode_filter")
    avg_shipping_duration = round(df["Shipping Duration"].mean(), 2)
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("Sales by Ship Mode")
        if not shipmode_select:
            st.warning("Please select at least one Ship Mode.")
        else:
            filtered_df = df[df["Ship Mode"].isin(shipmode_select)]
            sales_by_shipmode = filtered_df.groupby("Ship Mode", as_index=False)["Sales"].sum()
            st.bar_chart(data= sales_by_shipmode, x="Ship Mode", y="Sales")
    with chart_col2:
        st.subheader("Ship Mode count")
        if not shipmode_select:
            st.warning("Please select at least one Ship Mode.")
        else:
            filtered_df = df[df["Ship Mode"].isin(shipmode_select)]
            st.bar_chart(filtered_df['Ship Mode'].value_counts())
    st.divider()
    dchart_col1, dchart_col2 = st.columns(2)
    with dchart_col1:
        st.subheader("Shipping Duration Distribution")
        fig = px.histogram(df, x="Shipping Duration", nbins=8)
        st.plotly_chart(fig, width='stretch')
    with dchart_col2:
        st.subheader("Avg Shipping Duration by Ship Mode")
        if not shipmode_select:
            st.warning("Please select at least one Ship Mode.")
        else:
            filtered_df = df[df["Ship Mode"].isin(shipmode_select)]
            fig = px.histogram(filtered_df, x="Ship Mode", color="Shipping Duration", barmode="group", color_discrete_sequence=px.colors.sequential.Blues)
            st.plotly_chart(fig, width='stretch')
    st.divider()
    st.info(f"Standard Class is overwhelmingly the most used shipping mode, accounting for the majority of all orders. However, Same Day delivery consistently yields the highest average order value, suggesting an untapped opportunity to promote faster shipping options to high-value customers. Most orders are shipped within {avg_shipping_duration} days on average.")


def show_sales_trends():
    st.title("📈 Sales Trends")
    monthly_sales = (df.groupby([df['Order Date'].dt.year.rename("Year"), df['Order Date'].dt.month.rename("Month")])['Sales'].sum().reset_index())
    month_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    monthly_sales["Month Name"] = monthly_sales["Month"].map(month_map)
    pivoted_sales = monthly_sales.pivot(index="Month Name", columns="Year", values="Sales")
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pivoted_sales.index = pd.CategoricalIndex(pivoted_sales.index, categories=month_order, ordered=True)
    pivoted_sales = pivoted_sales.sort_index()
    available_years = list(pivoted_sales.columns)
    selected_years = st.sidebar.multiselect(label="Choose Years to Display", options=available_years, default=available_years)
    if selected_years:
        st.line_chart(pivoted_sales[selected_years], width='stretch')
    else:
        st.warning("Please select at least one year to display the chart.")
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        best_row = monthly_sales.loc[monthly_sales['Sales'].idxmax()]
        best_month_label = f"{best_row['Month Name']} {best_row['Year']}"
        best_month_value = f"${best_row['Sales']:,.0f}"
        st.metric(label="📈**Best Month**", value=best_month_label, delta=best_month_value)
    with c2:
        worst_row = monthly_sales.loc[monthly_sales['Sales'].idxmin()]
        worst_month_label = f"{worst_row['Month Name']} {worst_row['Year']}"
        worst_month_value = f"${worst_row['Sales']:,.0f}"
        st.metric(label="📉**Worst Month**", value=worst_month_label, delta=worst_month_value, delta_color="inverse")
    with c3:
        yearly_sales = monthly_sales.groupby("Year")["Sales"].sum()
        best_year = yearly_sales.idxmax()
        best_year_sales = f"${yearly_sales.max():,.0f}"
        st.metric(label="📈**Best Year**", value=str(best_year), delta=best_year_sales)
    st.divider()
    st.info(f"Sales peak consistently every September and November across all years, likely driven by back-to-school and holiday demand. February and October show predictable dips. {best_year} was the strongest year overall, and {best_month_label} was the single highest-performing month in the dataset.")


def show_customer_analysis():
    st.title("👥 Customer Analysis")
    total_customers = df["Customer ID"].nunique()
    top_customer = df.groupby("Customer Name")["Sales"].sum().idxmax()
    top_segment = df.groupby("Segment")["Sales"].sum().idxmax()
    orders_per_customer = df.groupby("Customer ID")["Order ID"].nunique()
    avg_orders = orders_per_customer.mean()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥**Total Unique Customers**", f"{total_customers:,}")
    col2.metric("🏆**Top Customer**", top_customer)
    col3.metric("💼**Top Segment**", top_segment)
    col4.metric("📦**Avg Orders per Customer**", f"{round(avg_orders)}")
    st.divider()
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        customer_view = st.sidebar.radio("Customer Rankings", options=["🏆**Top 10 Customers**", "📉**Bottom 10 Customers**"], index=0)
        customer_sales = df.groupby("Customer Name")["Sales"].sum().reset_index()
        if customer_view == "🏆**Top 10 Customers**":
            customer_data = customer_sales.sort_values("Sales", ascending=False).head(10)
            chart_title = "Top 10 Customers by Sales"
        else:
            customer_data = customer_sales.sort_values("Sales", ascending=True).head(10)
            chart_title = "Bottom 10 Customers by Sales"
        st.subheader(chart_title)
        chart = alt.Chart(customer_data).mark_bar().encode(x='Sales:Q', y=alt.Y('Customer Name:N', sort='-x'))
        st.altair_chart(chart)
    segment_select = sidebar.multiselect("Filter by Segment", options=df['Segment'].unique(), default=df['Segment'].unique(), key="Segment_filter")
    with chart_col2:
        st.subheader("Most Sold Segment")
        if not segment_select:
            st.warning("Please select at least one segment.")
        else:
            filtered_df = df[df["Segment"].isin(segment_select)]
            st.bar_chart(filtered_df['Segment'].value_counts())
    st.divider()
    st.info(f"The store serves {total_customers} unique customers, with the Consumer segment driving the majority of revenue. On average, each customer places {round(avg_orders)} orders, suggesting a moderately loyal customer base.")
        

home_page = st.Page(show_home, title="Home", icon="🏠", default=True)
dashboard_page = st.Page(show_overview, title="Sales Overview", icon="📊")
region_page = st.Page(show_region_analytics, title="Regional Analysis", icon="🌍")
shipping_page = st.Page(show_shipping_analytics, title="Shipping Analysis", icon="🚢")
sales_trends_page = st.Page(show_sales_trends, title="Sales Trends", icon="📈")
customer_page = st.Page(show_customer_analysis, title="Customer Analysis", icon="👥")

navigation_structure = {
    "Welcome": [home_page],
    "Core Applications": [dashboard_page, region_page, shipping_page, sales_trends_page, customer_page]
}

pg = st.navigation(navigation_structure)
pg.run()

