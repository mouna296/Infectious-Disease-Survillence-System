
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def main():
    df = pd.read_csv('NNDSS_Weekly_Data_20240503.csv')

    # Filter the DataFrame for week 11
    week_11_data = df[(df['Current MMWR Year'] == 2024) & (df['MMWR WEEK'] == 11)]

    # Group by disease and sum the cases for week 11
    disease_cases_week_11 = week_11_data.groupby('Label')['Current week'].sum()

    # Sort the diseases by total cases in descending order and get the top 10
    top_10_diseases_week_11 = disease_cases_week_11.nlargest(10)
    top_10_diseases_week_11 = top_10_diseases_week_11[::-1]

    # Create Streamlit app
    st.title('Top 10 Diseases for this week')

    # Create horizontal bar chart
    fig, ax = plt.subplots()
    top_10_diseases_week_11.plot(kind='barh', ax=ax)
    ax.set_xlabel('Cases')
    ax.set_ylabel('Disease')
    ax.set_title('Top 10 Diseases for this week')

    # Display the bar chart in Streamlit
    st.pyplot(fig)

    # yearly
    # Load your data into a DataFrame (replace 'your_data.csv' with your actual file path)

    # Filter the DataFrame for the year 2023
    df_2023 = df[df['Current MMWR Year'] == 2023]

    # Group by disease and sum the case count
    disease_cases_2023 = df_2023.groupby('Label')['Cumulative YTD Current MMWR Year'].sum()

    # Sort the diseases by total cases in descending order and get the top 10
    top_10_diseases_2023 = disease_cases_2023.nlargest(10)
    top_10_diseases_2023 = top_10_diseases_2023[::-1]

    # Create Streamlit app
    st.title('Top 10 Diseases for this year')

    # Create horizontal bar chart
    fig, ax = plt.subplots()
    top_10_diseases_2023.sort_values(ascending=False).plot(kind='barh', ax=ax)
    ax.set_xlabel('Cases')
    ax.set_ylabel('Disease')
    ax.set_title('Top 10 Diseases for this year')

    # Invert the y-axis to show the highest diseases on top
    plt.gca().invert_yaxis()

    # Display the bar chart in Streamlit
    st.pyplot(fig)


if __name__ == "__main__":
    main()
