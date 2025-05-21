import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ========== CONFIGURATIONS ==========
st.set_page_config(layout="wide", page_title="Interactive KPI Dashboard")
st.markdown("""<style>.metric-label { font-size: 16px !important; }</style>""", unsafe_allow_html=True)

# ========== LOAD DATA ==========
overall_df = pd.read_csv("Overall_BU.csv")
bu1_df = pd.read_csv("BU1.csv")

# ========== DATE PARSING ==========
overall_df['Bulan Quality'] = pd.to_datetime(overall_df['Bulan Quality'], dayfirst=True)
bu1_df['Bulan'] = pd.to_datetime(bu1_df['Bulan'], dayfirst=True)

# ========== FILTER FEBRUARY AND JANUARY DATA ==========
def get_month_data(df, col, month):
    return df[df[col].dt.month == month]

overall_feb = get_month_data(overall_df, 'Bulan Quality', 2)
overall_jan = get_month_data(overall_df, 'Bulan Quality', 1)

bu1_feb = get_month_data(bu1_df, 'Bulan', 2)
bu1_jan = get_month_data(bu1_df, 'Bulan', 1)

# ========== TABS ==========
tabs = st.tabs(["Overall BU", "BU1", "BU2", "BU3"])

# ========== TAB 1: OVERALL BU ==========
with tabs[0]:
    st.title("Overview: All Business Units")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.expander("Financial"):
            st.subheader("Budget vs Expense (Feb)")
            fig1 = px.pie(overall_feb, names='BU', values='Expense Finance', title='Expense per BU')
            st.plotly_chart(fig1, use_container_width=True)

            avg_usage = overall_feb['Usage Finance'].mean()
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avg_usage,
                gauge={'axis': {'range': [None, 100]}},
                title={"text": "Avg Usage %"}
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)

            st.metric("Total Revenue (Feb)", overall_feb['Revenue Finance'].sum(), delta=overall_feb['Revenue Finance'].sum() - overall_jan['Revenue Finance'].sum())
            st.metric("Total Profit (Feb)", overall_feb['Profit Finance'].sum(), delta=overall_feb['Profit Finance'].sum() - overall_jan['Profit Finance'].sum())

    with col2:
        with st.expander("Customer n Service"):
            st.subheader("# of Customer (Feb)")
            fig2 = px.pie(overall_feb, names='BU', values='#of customer Customer', title='# of Customers')
            st.plotly_chart(fig2, use_container_width=True)

            avg_sat_feb = overall_feb['Customer satisfaction Customer'].mean()
            avg_sat_jan = overall_jan['Customer satisfaction Customer'].mean()
            st.metric("Avg Satisfaction (Feb)", round(avg_sat_feb,2), delta=round(avg_sat_feb - avg_sat_jan, 2))

            df_line = pd.DataFrame({
                'BU': overall_feb['BU'],
                'Feb': overall_feb['Customer satisfaction Customer'].values,
                'Jan': overall_jan['Customer satisfaction Customer'].values
            })
            fig_line = px.line(df_line.melt(id_vars='BU', var_name='Month', value_name='Satisfaction'), x='BU', y='Satisfaction', color='Month')
            st.plotly_chart(fig_line, use_container_width=True)

    with col3:
        with st.expander("Quality"):
            st.subheader("Target vs Real Quality (Feb)")
            st.dataframe(overall_feb[['BU','Target vs Real Quality']])
            st.metric("Avg Velocity", round(overall_feb['Velocity Quality'].mean(), 2))
            st.metric("Avg Quality", round(overall_feb['Quality'].mean(), 2))

    with col4:
        with st.expander("Employee"):
            st.subheader("Manpower & Competency")
            overall_feb['MP_Gap'] = overall_feb['Needed MP Employee'] - overall_feb['Current MP Employee']
            st.dataframe(overall_feb[['BU','Current MP Employee','Needed MP Employee','MP_Gap']])

            fig3 = px.pie(overall_feb, names='BU', values='Competency Employee', title='Competency')
            st.plotly_chart(fig3, use_container_width=True)

            st.markdown(f"**Average Competency:** {round(overall_feb['Competency Employee'].mean(),2)}")
            st.metric("Turnover Ratio", round(overall_feb['Turnover ratio Employee'].mean(), 2))

# ========== TAB 2: BU1 ==========
with tabs[1]:
    st.title("Detail: Business Unit 1")

    subdiv_list = bu1_df['Subdiv'].unique()
    subdiv = st.selectbox("Pilih Subdiv", subdiv_list)

    subdiv_feb = bu1_feb[bu1_feb['Subdiv'] == subdiv]
    subdiv_jan = bu1_jan[bu1_jan['Subdiv'] == subdiv]

    tabbu1 = st.tabs(["Financial", "Customer", "Quality", "Employee"])

    with tabbu1[0]:
        st.subheader("Financial")
        st.bar_chart(subdiv_feb[['Budget', 'Expense']].set_index(pd.Index([subdiv])))

        usage = subdiv_feb['Usage'].mean()
        fig_gauge2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=usage,
            gauge={'axis': {'range': [None, 100]}},
            title={"text": "Usage %"}
        ))
        st.plotly_chart(fig_gauge2, use_container_width=True)

        st.metric("Revenue", subdiv_feb['Revenue'].sum(), delta=subdiv_feb['Revenue'].sum() - subdiv_jan['Revenue'].sum())
        st.metric("Profit", subdiv_feb['Profit'].sum(), delta=subdiv_feb['Profit'].sum() - subdiv_jan['Profit'].sum())

    with tabbu1[1]:
        st.subheader("Customer")
        produk_list = subdiv_feb['Produk'].unique()
        fig4 = px.pie(subdiv_feb, names='Produk', values='#of customer')
        st.plotly_chart(fig4, use_container_width=True)

        total_cust_feb = subdiv_feb['#of customer'].sum()
        total_cust_jan = subdiv_jan['#of customer'].sum()
        st.metric("Total Customer", total_cust_feb, delta=total_cust_feb - total_cust_jan)

        df_line2 = pd.DataFrame({
            'Produk': produk_list,
            'Feb': subdiv_feb.groupby('Produk')['Customer satisfaction'].mean().values,
            'Jan': subdiv_jan.groupby('Produk')['Customer satisfaction'].mean().values,
        })
        fig_line2 = px.line(df_line2.melt(id_vars='Produk', var_name='Month', value_name='Satisfaction'), x='Produk', y='Satisfaction', color='Month')
        st.plotly_chart(fig_line2, use_container_width=True)

    with tabbu1[2]:
        st.subheader("Quality")
        st.dataframe(subdiv_feb[['Target', 'Realization', 'Target vs Real']])
        st.metric("Velocity", round(subdiv_feb['Velocity'].mean(), 2))
        st.metric("Quality", round(subdiv_feb['Quality'].mean(), 2))

    with tabbu1[3]:
        st.subheader("Employee")
        subdiv_feb['MP_Gap'] = subdiv_feb['Needed MP'] - subdiv_feb['Current MP']
        st.dataframe(subdiv_feb[['Current MP', 'Needed MP', 'MP_Gap']])

        fig5 = px.pie(subdiv_feb, names='Produk', values='Competency')
        st.plotly_chart(fig5, use_container_width=True)

        st.markdown(f"**Average Competency:** {round(subdiv_feb['Competency'].mean(),2)}")
        st.metric("Turnover Ratio", round(subdiv_feb['Turnover ratio'].mean(), 2))

# ========== TAB 3 & 4 Placeholder ==========
with tabs[2]:
    st.title("Detail: Business Unit 2")
    st.info("Data belum tersedia.")

with tabs[3]:
    st.title("Detail: Business Unit 3")
    st.info("Data belum tersedia.")
