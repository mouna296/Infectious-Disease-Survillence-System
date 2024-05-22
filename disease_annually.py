from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st


def load_data():
    annual_data = pd.read_csv('merged_data_CaseCount_stateabbr.csv')
    weekly_data = pd.read_csv('NNDSS_Weekly_Data_20240503.csv')
    return annual_data, weekly_data


st.set_page_config(layout="wide")
df_annual, df_weekly = load_data()
df_annual['Case Count'] = pd.to_numeric(df_annual['Case Count'],
                                        errors='coerce')

disease_selected = st.sidebar.selectbox('Select a Disease', df_annual['Disease'].unique())
filtered_data = df_annual[df_annual['Disease'] == disease_selected]
filtered_data.fillna(0)


def create_choropleth(_filtered_data, column, title):
    return px.choropleth(
        _filtered_data,
        locations="state_abbr",
        locationmode='USA-states',
        color=column,
        hover_name="States",
        hover_data=["Case Count", "Population for Published Rate", column],
        range_color=(0, 0.8 * _filtered_data[column].max()),
        color_continuous_scale="purples",
        animation_frame="Year",
        scope="usa",
        title=title,
        height=500, width=500
    )


fig_choropleth_case_count = create_choropleth(filtered_data, "Case Count",
                                              f"Disease Cases Across the U.S. by State for {disease_selected}")
fig_choropleth_rate = create_choropleth(filtered_data, "Published Rate",
                                        f"Case Rates Across the U.S. by State for {disease_selected}")
line_case_data = df_annual[df_annual['Disease'] == disease_selected].groupby('Year')[
    'Case Count'].sum().reset_index()
line_rate_data = df_annual[df_annual['Disease'] == disease_selected].groupby('Year')[
    'Published Rate'].mean().reset_index()

fig_line = px.line(line_case_data, x='Year', y='Case Count',
                   title=f'Total Cases of {disease_selected} by Year', markers=True, height=500,
                   width=500)
fig_rate_line = px.line(line_rate_data, x='Year', y='Published Rate',
                        title=f'Case Rates of {disease_selected} by Year', markers=True,
                        height=500, width=500)

tab1, tab2 = st.tabs(["Disease Distribution and Trends", "Disease Trends"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_choropleth_case_count, use_container_width=True)
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.plotly_chart(fig_choropleth_rate, use_container_width=True)
        st.plotly_chart(fig_rate_line, use_container_width=True)

with tab2:
    st.title('Case Trends')
    selected_location = st.selectbox('Select Location', df_annual['States'].unique())

    col1, col2 = st.columns(2)
    with col1:
        st.write("## Weekly Case Change")
        current_date = datetime.now()
        current_week = current_date.isocalendar()[1]
        current_year = 2023

        last_week = current_week - 1 if current_week > 1 else 52
        last_weeks_year = current_year if last_week != 52 else current_year - 1
        current_week_cases = df_weekly[
            (df_weekly['MMWR WEEK'] == current_week) & (
                    df_weekly['Current MMWR Year'] == current_year)]
        current_week_cases = current_week_cases[
            ['LOCATION1', 'Label', 'Current week', 'MMWR WEEK', 'Current MMWR Year']].rename(
            columns={'Current week': 'Current Week Cases'})

        previous_week_cases = df_weekly[
            (df_weekly['MMWR WEEK'] == last_week) & (
                    df_weekly['Current MMWR Year'] == last_weeks_year)]
        previous_week_cases = previous_week_cases[
            ['LOCATION1', 'Label', 'Current week', 'MMWR WEEK', 'Current MMWR Year']].rename(
            columns={'Current week': 'Last Week Cases'})

        combined_df = pd.merge(previous_week_cases, current_week_cases, on=['LOCATION1', 'Label'],
                               how='outer')

        combined_df['Current Week Cases'] = combined_df['Current Week Cases'].fillna(0)
        combined_df['Last Week Cases'] = combined_df['Last Week Cases'].fillna(0)

        data = combined_df[
            (combined_df['LOCATION1'] == selected_location) & (
                    combined_df['Label'] == disease_selected)]

        trend_data = data[['Last Week Cases', 'Current Week Cases']]
        trend_data.fillna(0)

        fig, ax = plt.subplots()

        min_value = trend_data.min().min()
        max_value = trend_data.max().max()
        range_value = max_value - min_value
        buffer = range_value * 0.5

        ax.plot(trend_data.T)
        ax.set_ylim(bottom=min_value - buffer, top=max_value + buffer)  # Set y-axis with a buffer
        plt.xticks(ticks=[0, 1], labels=['Last Week', 'Current Week'])

        st.pyplot(fig)

        change = ((data['Current Week Cases'].values[0] - data['Last Week Cases'].values[0]) /
                  data['Last Week Cases'].values[0]) * 100 if data['Last Week Cases'].values[
                                                                  0] != 0 else 0
        direction = "increased" if change > 0 else "decreased" if change < 0 else "remained steady"
        change_color = "red" if change > 0 else "green" if change < 0 else "gray"
        st.markdown(f"**Change: {change:.2f}% ({direction})**", unsafe_allow_html=True)

    with col2:
        st.write("## Yearly Case Change")
        previous_year = current_year - 1

        # Filter data for the current and previous years
        current_year_data = df_annual[
            (df_annual['Year'] == current_year) & (df_annual['Disease'] == disease_selected)]
        previous_year_data = df_annual[
            (df_annual['Year'] == previous_year) & (df_annual['Disease'] == disease_selected)]

        # Merge the data for comparison
        yearly_comparison = pd.merge(
            previous_year_data[['States', 'Case Count']].rename(
                columns={'Case Count': 'Last Year Cases'}),
            current_year_data[['States', 'Case Count']].rename(
                columns={'Case Count': 'This Year Cases'}),
            on='States', how='outer'
        ).fillna(0)

        print("Yearly Compirison", yearly_comparison)

        comparison_data = yearly_comparison[
            yearly_comparison['States'] == selected_location]

        # Create a bar plot
        fig_yearly, ax_yearly = plt.subplots()
        ax_yearly.bar(['Last Year', 'This Year'],
                      comparison_data[['Last Year Cases', 'This Year Cases']].values[0],
                      color=['blue', 'orange'])
        ax_yearly.set_title('Yearly Case Comparison')
        ax_yearly.set_ylabel('Number of Cases')

        st.pyplot(fig_yearly)

        last_cases = comparison_data['Last Year Cases'].values[0]
        this_cases = comparison_data['This Year Cases'].values[0]
        year_change = ((this_cases - last_cases) / last_cases * 100) if last_cases != 0 else 0
        direction_year = "increased" if year_change > 0 else "decreased" if year_change < 0 else "remained steady"

        # Display the change in a marked format
        st.markdown(f"**Annual Change: {year_change:.2f}% ({direction_year})**",
                    unsafe_allow_html=True)
