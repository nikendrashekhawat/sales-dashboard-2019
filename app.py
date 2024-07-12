import streamlit as st
import pandas as pd
from funcs import load_data, display_df
from funcs import filter_by_price_category, filter_by_city, filter_by_month
from funcs import group_by_city, group_by_day, group_by_product
from funcs import combine_chart
from funcs import line_chart, hbar_chart, pie_chart, area_chart, vbar_chart

st.set_page_config(layout="wide")


st.title(":blue[Sales]  and :blue[Quantity Ordered] Analysis Dashboard")
st.markdown('''Analysis of sales and quantity ordered
            of electronics goods sold in 2019.''')
    
df = load_data()

cities = list(pd.unique(df["City"]))

cities.insert(0, "All")

months = {0: "All", 1: "January", 2: "February", 3:"March", 4:"April",
          5:"May", 6:"June", 7:"July", 8:"August", 9:"September",
          10:"October", 11:"November", 12:"December"}


with st.sidebar:
    selected_product = st.radio(label="Category of products:",
                                options=["All", "Expensive", "Moderate", "Low Priced"],
                                help = "Products are categorised on the basis of unit price") 
    
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    analysis_on = st.selectbox("Analysis on:", ["Sales", "Quantity Ordered"], index=1)


if selected_product != "All":
    df = filter_by_price_category(df, selected_product)
    
toggle = st.toggle("Show DataFrame")

if toggle:
    st.subheader("Data:")
    display_df(df)

df = df[['Product',"Order Date", "Month", "Day", "City", "Quantity Ordered", "Sales"]]
st.divider()

col1 , col2 = st.columns(2, gap="large")
    
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True) 

chart_col1, chart_col2= st.columns(2, gap='medium')

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)   

chart_col3, chart_col4 = st.columns([0.6,0.4], gap="medium")

with col1: 
    selected_month = st.selectbox(label="Month",
                            options=months.values(),
                            key="month")

if selected_month != "All":
    with col2:
        selected_city = st.selectbox(label = "City",
                                options=cities,
                                key='city') 
    
    filtered_by_months = filter_by_month(df, selected_month)
    
    with chart_col1:
        filtered_by_days = group_by_day(filtered_by_months)
        st.altair_chart(line_chart(filtered_by_days, analysis_on, selected_month), use_container_width=True)
    
    with chart_col2:
        filtered_by_prod = group_by_product(filtered_by_months)
        st.altair_chart(hbar_chart(filtered_by_prod, analysis_on, selected_month), use_container_width=True)
    
    with chart_col3:
        if selected_city != "All":
            filtered_by_city = filter_by_city(filtered_by_months, selected_city)
            filtered_by_city_days = group_by_day(filtered_by_city)
            st.altair_chart(area_chart(filtered_by_city_days, analysis_on, selected_city, selected_month),
                            use_container_width=True)
        else:
            filtered_by_city = group_by_city(filtered_by_months)
            st.altair_chart(vbar_chart(filtered_by_city, analysis_on, selected_month), use_container_width=True)
        
           
    with chart_col4:
        if selected_city != "All":
            filtered_by_city = filter_by_city(filtered_by_months, selected_city)
            filtered_by_city_prod = group_by_product(filtered_by_city)
            st.altair_chart(pie_chart(filtered_by_city_prod, analysis_on, selected_city), 
                            use_container_width=True)
            
        else:
            filtered_by_city = group_by_city(filtered_by_months)
            st.altair_chart(pie_chart(filtered_by_city, analysis_on, selected_city),
                            use_container_width=True)
           
else:
    with st.container():
        st.altair_chart(combine_chart(df, analysis_on))

st.divider() 

    
