import streamlit as st
import pandas as pd
import altair as alt

alt.data_transformers.enable('default')


@st.cache_resource
def load_data() -> pd.DataFrame:
    df = pd.read_csv("Cleaned Sales Data 2019.csv", index_col= 0)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df


@st.cache_data   
def display_df(df) -> pd.DataFrame:
    st.dataframe(df, 
                column_config= {"Price Each": st.column_config.NumberColumn("Price Each(in USD)",
                                                help="The price of 1 unit of product in USD", 
                                                disabled=True,
                                                format="$%f",),
                            "Sales": st.column_config.NumberColumn("Sales(in USD)",
                                                help="The price of quantiy ordered in USD", 
                                                disabled=True,
                                                format="$%f",),
                            "Order ID": st.column_config.DatetimeColumn(),
                            "Order ID": st.column_config.NumberColumn(format="%d"),
                            "Order Date": st.column_config.DatetimeColumn(),
                            "Month": st.column_config.NumberColumn(format="%d"),
                            "Day": st.column_config.NumberColumn(format="%d"),
                            "Hour": st.column_config.NumberColumn(format="%d"),
                            "Quantity Ordered": st.column_config.NumberColumn(format="%d"),
                            "Postal Code": st.column_config.NumberColumn(format="%d"),
                            }
             )


@st.cache_data
def filter_by_price_category(df, selection) -> pd.DataFrame:
    if selection  == "Expensive":
        df = df.loc[df["Price Each"] >= 400]
    if selection== "Moderate":
        df = df.loc[(df["Price Each"] >= 50) & (df["Price Each"] < 400)]
    if selection == "Low Priced":
        df = df.loc[df["Price Each"] < 50]
    
    return df


@st.cache_data
def filter_by_month(df, selection):
    return df.loc[df["Order Date"].dt.month_name() == selection]
    
@st.cache_data
def group_by_month(df) -> pd.DataFrame:
    return df.groupby('Month')[["Quantity Ordered", "Sales"]].agg('sum').reset_index()
    

@st.cache_data
def group_by_product(df) -> pd.DataFrame:
    prod = df.groupby('Product')[["Quantity Ordered", "Sales"]].agg('sum').reset_index()
    return prod

@st.cache_data
def group_by_day(df) -> pd.DataFrame:
    days = df.groupby('Day')[["Quantity Ordered", "Sales"]].agg('sum').reset_index()
    return days

@st.cache_data
def group_by_city(df) -> pd.DataFrame:
    return df.groupby('City')[["Quantity Ordered", "Sales"]].agg('sum').reset_index()
    

@st.cache_data
def filter_by_city(df, select_city) -> pd.DataFrame:
    return df.loc[df["City"] == select_city]

@st.cache_data
def line_chart(df, analysis, month):

    point = alt.OverlayMarkDef(size=80, filled= True, opacity=0.8)
                                                   
    base = alt.Chart(df, title=alt.Title(f"{analysis} in {month}", anchor="middle")).mark_line(
            point = point).interactive()
        
    c = (base.encode(
        x= alt.X("Day:N",title = "Day", axis=alt.Axis(labelAngle=0)) ,
        y=alt.Y(analysis).scale(zero=False),
        tooltip=["Day:N", analysis]).properties(height=400)
    )
    
    return c


@st.cache_data
def hbar_chart(df, analysis, month):
        
    colors = alt.Color("Product:N").scale(scheme="yellowgreenblue").legend(None)
    
    base = alt.Chart(df, title = alt.Title(f"{analysis} by Products in {month}", 
                                           anchor="middle")).interactive()
    
    c = (base.encode(
        x=analysis,
        y=alt.Y('Product:N', title="").axis(labelOverlap=False),
        color=colors,
        text = analysis,
        tooltip=["Product:N", analysis]).properties(height=400)
    )
    return c.mark_bar() + c.mark_text(align='left', dx=4) 
    
@st.cache_data
def vbar_chart(df, analysis, month):
    selection = alt.selection_point(fields=["City"])
    
    color = alt.Color("City:N", legend=None).scale(scheme="tealblues") 
    
    base = alt.Chart(df, title=alt.Title(f"{analysis} by cities in {month}", anchor="middle")).interactive()
    
    c = ( base.mark_bar()
            .encode(
                x= alt.X("City:N", title="", axis= alt.Axis(labelAngle=-40, labelOverlap=False)),
                y= analysis, 
                color= alt.condition(selection, color, alt.value("lightgray")),
                tooltip=["City:N", analysis],
                opacity=alt.value(1))
            .properties(
                height=350,
                )
            .add_params(selection)
    )
    return c 


@st.cache_data
def area_chart(df, analysis, city, month):
    title=alt.Title(f"{analysis} in {city} in {month}", anchor="middle", subtitle="Distribution by Days")  
    base = alt.Chart(df, title=title).properties(height=350).interactive()
    stops = [alt.GradientStop(color="white", offset=0),
            alt.GradientStop(color="darkgreen", offset=1)]
    
    c = (base.mark_area(
        line={"color": "darkgreen"},
        color=alt.Gradient(gradient="linear", 
                            stops=stops,
                            x1=1, 
                            x2=1,
                            y1=1,
                            y2=0.2))
         .encode(
                x=alt.X("Day:N",title = "Day", axis=alt.Axis(labelAngle=0, labelOverlap=True)),
                y= alt.Y(analysis).scale(zero=False),
                tooltip=["Day:N", analysis]
                )
    )
    
    return c


@st.cache_data
def pie_chart(df, analysis, city):
    
    if city != "All":
        title=alt.Title(f"Percentage of {analysis}", anchor="middle", subtitle="Distribution by Products")
        colors = alt.Color("Product:N").scale(scheme="tableau20").legend(None)
        tooltip = ["Product:N", alt.Tooltip("percentage:Q", format=".2f")]

    else:
        title = alt.Title(f"Percentage of {analysis}", anchor="middle", subtitle="Distribution by Cities")  
        colors = alt.Color("City:N").scale(scheme="tableau20").legend(None)
        tooltip = ["City:N", alt.Tooltip("percentage:Q", format=".2f")]
          
    
    base = alt.Chart(df, title=title).mark_arc(padAngle=0.02).properties(height=300)
    
    c = ( base.transform_joinaggregate(total= f"sum({analysis})",)
         .transform_calculate(
             percentage = (alt.datum[analysis] / alt.datum.total * 100))
         .encode(
             theta= 'percentage:Q',
             color= colors,
             tooltip= tooltip)
    )
    
    return c


@st.cache_data
def combine_chart(df, analysis):
    
    select_city = alt.selection_point(fields=["City"])
    select_product = alt.selection_point(fields=["Product"])
    
    base = alt.Chart(df)
    
    vbar = ( base.mark_bar()
            .transform_filter(select_product)
            .transform_aggregate(
                y = f"sum({analysis})",
                groupby= ["City"])
            .encode(
                x= alt.X("City:N", title="", axis= alt.Axis(labelAngle=-40, labelOverlap=False)),
                y= alt.Y("y:Q", title=analysis), 
                color= alt.condition(select_city, 
                           alt.Color("City:N", legend=None).scale(scheme="tealblues"),
                           alt.value("lightgray")),
                tooltip=["City:N", alt.Tooltip("y:Q", title=analysis, format=".0f")])
            .properties(
                height=250,
                width=350,
                title=alt.Title(f"{analysis} by City", anchor="middle"))
            .add_params(select_city)
    )
    
    line = ( base
             .encode(
                x=alt.X("Month:N", axis= alt.Axis(labelAngle=-40, labelOverlap=False)),
                tooltip=["Month", alt.Tooltip("y:Q", title=analysis, format=".0f")]
                    )
             .properties(
                 height=250, 
                 width=400, 
                 title=alt.Title(f"Total {analysis} by Month", anchor="middle")).interactive()
    )

    line1 = line.mark_line(point= alt.OverlayMarkDef(size=80,opacity=0.8)).transform_filter(select_city).transform_aggregate(
                 y = f"sum({analysis})",
                 groupby= ["Month"]).encode(
                     y=alt.Y("y:Q",title= f"{analysis} in City")
                     )
                 
    line2 = line.mark_line(point= alt.OverlayMarkDef(size=80,opacity=0.8,)).transform_filter(select_product).transform_aggregate(
                 y = f"sum({analysis})",
                 groupby= ["Month"]).encode(
                     y=alt.Y("y:Q", title= f"{analysis} of Product"),
                     color=alt.value("red")
                     )
        
    pie_base = ( base.transform_filter(select_city)
         .transform_aggregate(
        t=f"sum({analysis})",
        groupby=["Product"])
         .transform_joinaggregate(total= f"sum(t)")
         .transform_calculate(
             percentage = (alt.datum.t / alt.datum.total * 100)
             )
         .encode(
             theta= alt.Theta('percentage:Q').stack(True),
             color = alt.condition(select_product,
                               alt.Color("Product:N").scale(scheme="tableau20").legend(None),
                               alt.value("lightgray")),
             opacity = alt.condition(select_product, alt.value(1), alt.value(0.1)),
             tooltip=["Product:N", alt.Tooltip("percentage:Q", format=".2f")]
            )
         .properties(
            title=alt.Title(f"Percentage of {analysis}", anchor="middle", subtitle="Distribution by Products")).add_params(select_product)
         
    )
    arc = pie_base.mark_arc(padAngle=0.01,outerRadius=110)
    arc_text2 = ( pie_base.mark_text(outerRadius=130)
                 .encode(
                     text=alt.condition(select_product, alt.Text("percentage:Q", format=".2f"), alt.value("")),
                     opacity=alt.condition(select_product, alt.value(1), alt.value(0)),
                     size = alt.condition(select_product,alt.value(15), alt.value(0)),
                     )
                 )

    pie = arc + arc_text2
    layer = alt.layer(line1, line2).resolve_axis(y="independent")
    down_chart = alt.hconcat(layer, pie)
    
    bar = (base.transform_filter(select_city)
            .transform_aggregate(
                x = f"sum({analysis})",
                groupby= ["Product"])
            .encode(
                y= alt.Y("Product:N", title="", axis=alt.Axis(labelOverlap=False)),
                x= alt.X("x:Q", title=analysis),
                color= alt.condition(select_product, 
                                    alt.Color("Product:N", legend=None,scale = alt.Scale(scheme="yellowgreenblue")),
                                    alt.value("lightgray")),
                opacity=alt.condition(select_product, alt.value(1), alt.value(0.5)),
                tooltip=["Product:N", alt.Tooltip("x:Q", title=analysis, format=".0f")],
                text=alt.condition(select_product, "x:Q", alt.value(""))
                )
            .properties(
                height=275,
                width=400,
                title=alt.Title(f"{analysis} by Product", anchor="middle")).add_params(select_product)
    )
    
    hbar = (bar.mark_bar() + bar.mark_text(align='left', dx=5))
    
    return alt.hconcat(vbar, hbar).resolve_scale(color="independent") & down_chart
