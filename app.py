import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load your data
@st.cache_data
def load_data():
    # Load the cleaned Superstore data
    df = pd.read_csv('Superstore.csv')
    
    # Apply the same data cleaning you did in your analysis
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['Profit Margin'] = (df['Profit'] / df['Sales']).replace([np.inf, -np.inf], 0).fillna(0)
    df['Order Year'] = df['Order Date'].dt.year
    df['Order Month'] = df['Order Date'].dt.month
    df['Shipping Days'] = (df['Ship Date'] - df['Order Date']).dt.days
    
    return df

df = load_data()

# Title and description
st.title("🚀 Superstore Sales Analysis Dashboard")
st.markdown("""
This interactive dashboard provides insights into Superstore sales performance from 2015-2018.
**Key Findings from Analysis:** Furniture category profitability issues, Central region negative margins, and discount erosion.
""")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Year filter
years = sorted(df['Order Year'].unique())
selected_years = st.sidebar.multiselect(
    "Select Years:",
    options=years,
    default=years
)

# Region filter
regions = df['Region'].unique()
selected_regions = st.sidebar.multiselect(
    "Select Regions:",
    options=regions,
    default=regions
)

# Category filter
categories = df['Category'].unique()
selected_categories = st.sidebar.multiselect(
    "Select Categories:",
    options=categories,
    default=categories
)

# Apply filters
filtered_df = df[
    (df['Order Year'].isin(selected_years)) &
    (df['Region'].isin(selected_regions)) &
    (df['Category'].isin(selected_categories))
]

# Key Metrics Row
st.header("📈 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_df['Sales'].sum()
    st.metric("Total Sales", f"${total_sales:,.0f}")

with col2:
    total_profit = filtered_df['Profit'].sum()
    st.metric("Total Profit", f"${total_profit:,.0f}")

with col3:
    avg_margin = (filtered_df['Profit'].sum() / filtered_df['Sales'].sum()) * 100
    st.metric("Average Margin", f"{avg_margin:.1f}%")

with col4:
    total_orders = filtered_df['Order ID'].nunique()
    st.metric("Total Orders", f"{total_orders:,}")

# Main Dashboard Layout
st.header("📊 Performance Analysis")

# First Row: Category and Regional Analysis
col1, col2 = st.columns(2)

with col1:
    category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
    fig1 = px.bar(category_sales, x='Category', y='Sales', 
                  title='Sales by Product Category',
                  color='Category')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    region_profit = filtered_df.groupby('Region')['Profit'].sum().reset_index()
    fig2 = px.bar(region_profit, x='Region', y='Profit', 
                  title='Profit by Region',
                  color='Region')
    st.plotly_chart(fig2, use_container_width=True)

# Second Row: Segments and Correlation
col3, col4 = st.columns(2)

with col3:
    segment_profit = filtered_df.groupby('Segment')['Profit'].sum().reset_index()
    fig3 = px.pie(segment_profit, values='Profit', names='Segment',
                  title='Profit Distribution by Customer Segment')
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    # Discount vs Profit Margin scatter plot
    sample_df = filtered_df[filtered_df['Discount'] > 0].sample(min(1000, len(filtered_df)))
    fig4 = px.scatter(sample_df, x='Discount', y='Profit Margin',
                      title='Discount Impact on Profit Margin',
                      color='Category',
                      trendline='lowess')
    st.plotly_chart(fig4, use_container_width=True)

# Third Row: Time Series and Shipping
col5, col6 = st.columns(2)

with col5:
    # Monthly trend
    monthly_data = filtered_df.groupby(['Order Year', 'Order Month']).agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    monthly_data['Date'] = pd.to_datetime(
        monthly_data['Order Year'].astype(str) + '-' + 
        monthly_data['Order Month'].astype(str) + '-01'
    )
    fig5 = px.line(monthly_data, x='Date', y='Sales', 
                   title='Monthly Sales Trend')
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    shipping_analysis = filtered_df.groupby('Ship Mode').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Shipping Days': 'mean'
    }).reset_index()
    shipping_analysis['Margin'] = (shipping_analysis['Profit'] / shipping_analysis['Sales']) * 100
    
    fig6 = px.bar(shipping_analysis, x='Ship Mode', y='Margin',
                  title='Profit Margin by Shipping Mode',
                  color='Ship Mode')
    st.plotly_chart(fig6, use_container_width=True)

# Insights Section
st.header("💡 Key Business Insights")

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.subheader("🚨 Critical Issues")
    st.markdown("""
    - **Furniture Category**: High sales but low profitability
    - **Central Region**: Negative profit margins
    - **Discount Erosion**: High discounts destroy margins
    - **1,871 orders** are loss-making
    """)

with insight_col2:
    st.subheader("🎯 Growth Opportunities")
    st.markdown("""
    - **Home Office Segment**: Highest profit margins
    - **Technology Products**: Most profitable category  
    - **West Region**: Best performing region
    - **Premium Shipping**: Better margins
    """)

# Footer
st.markdown("---")
st.markdown("""
**Dashboard Created with Streamlit** | Based on Superstore Sales Data (2015-2018)
| **Analysis by:** [Your Name]
""")
