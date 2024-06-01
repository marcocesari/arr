import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.cm as cm
import streamlit as st

# Define MSCI World Index data
msci_data = {
    "Year": list(range(1990, 2024)),
    "MSCI_World_Close": [
        372.12,
        431.00,
        416.58,
        487.15,
        492.34,
        573.71,
        668.60,
        760.37,
        906.94,
        1125.41,
        1035.51,
        860.56,
        671.97,
        834.46,
        937.66,
        980.27,
        1128.04,
        1312.94,
        789.84,
        1058.07,
        1168.80,
        1073.44,
        1238.92,
        1491.48,
        1584.31,
        1560.51,
        1674.43,
        2036.67,
        1899.39,
        2323.14,
        2699.15,
        3354.00,
        2702.29,
        3295.00,
    ],
}

# Define NASDAQ historical yearly closing prices and US inflation rates
nasdaq_data = {
    "Year": list(range(1997, 2024)),
    "NASDAQ_Close": [
        1570.35,
        2192.69,
        4069.31,
        2470.52,
        1950.40,
        1340.43,
        2003.37,
        2178.34,
        2205.32,
        2415.29,
        2652.28,
        1577.03,
        2269.15,
        2652.87,
        2605.15,
        3019.51,
        4058.62,
        4736.05,
        5007.41,
        5383.12,
        6903.39,
        6635.28,
        8972.60,
        12888.28,
        15744.52,
        10535.48,
        14056.72,
    ],
}

# Define US inflation rates from 1990 to 2023
us_inflation_rates = [
    5.4,
    4.2,
    3.0,
    3.0,
    2.6,
    2.8,
    3.0,
    2.3,
    1.6,
    2.2,
    3.4,
    2.8,
    1.6,
    2.3,
    2.7,
    3.4,
    3.2,
    2.9,
    3.8,
    -0.4,
    1.6,
    3.2,
    2.1,
    1.5,
    1.6,
    0.1,
    1.3,
    2.1,
    2.4,
    1.8,
    1.2,
    4.7,
    8.0,
    4.0,
]

# Create DataFrames
df_msci = pd.DataFrame(msci_data)
df_msci["US_Inflation_Rate"] = us_inflation_rates

df_nasdaq = pd.DataFrame(nasdaq_data)
df_nasdaq["US_Inflation_Rate"] = us_inflation_rates[
    7:
]  # Align inflation rates with NASDAQ data starting from 1997

# Initial investment
initial_investment = 100000

# Streamlit app
st.title("Investment Analysis in MSCI World Index and NASDAQ Index")
st.sidebar.header("Settings")

# User input for number of installments
num_installments = st.sidebar.slider(
    "Number of Installments", min_value=1, max_value=10, value=3
)

# User input for inflation adjustment
inflation_adjusted = st.sidebar.checkbox("Inflation-Adjusted ARR%", value=True)

# User input for index selection
index_option = st.sidebar.selectbox("Index", ["MSCI World", "NASDAQ"])


# Function to calculate investment values and ARR over time for different starting years with installments
def calculate_investment_values_and_arr_series_instalments(
    start_year, df, num_installments, inflation_adjusted, index_column
):
    start_index = df[df["Year"] == start_year].index[0]
    investment_per_year = initial_investment / num_installments
    cumulative_inflation_factors = [1] * num_installments
    investment_values = []

    for i in range(start_index, len(df)):
        year = df.loc[i, "Year"]
        total_value = 0
        total_investment_made = 0

        # Spread the investment over the specified number of years
        for j in range(num_installments):
            if i - j >= start_index:
                initial_value = df.loc[start_index + j, index_column]
                cumulative_inflation_factors[j] *= (
                    1 + df.loc[i, "US_Inflation_Rate"] / 100
                )
                if inflation_adjusted:
                    value = (
                        investment_per_year * df.loc[i, index_column] / initial_value
                    ) / cumulative_inflation_factors[j]
                else:
                    value = (
                        investment_per_year * df.loc[i, index_column] / initial_value
                    )
                total_value += value
                total_investment_made += investment_per_year

        years_since_start = year - start_year + 1
        if total_investment_made == 0:
            arr_adjusted = 0
        else:
            arr_adjusted = (
                (total_value / total_investment_made) ** (1 / years_since_start) - 1
            ) * 100
        investment_values.append((year, arr_adjusted))

    return investment_values


# Select the DataFrame and column based on user input
if index_option == "MSCI World":
    df = df_msci
    index_column = "MSCI_World_Close"
    starting_years = list(range(1990, 2023))
else:
    df = df_nasdaq
    index_column = "NASDAQ_Close"
    starting_years = list(range(1997, 2023))

# Generate a colormap
colors = cm.viridis(np.linspace(0, 1, len(starting_years)))

# Plotting ARR for different starting years with gradient colors and specified yearly installments
plt.figure(figsize=(14, 8))

for i, start_year in enumerate(starting_years):
    values = calculate_investment_values_and_arr_series_instalments(
        start_year, df, num_installments, inflation_adjusted, index_column
    )
    years, arr_values = zip(*values)
    plt.plot(years, arr_values, label=f"{start_year}", color=colors[i])

# Adding labels and title
plt.xlabel("Year")
plt.ylabel("ARR (%)")
title = f'Adjusted ARR (%) in {index_option} Index ({"1990-2023" if index_option == "MSCI World" else "1997-2023"}) with {num_installments} Yearly Installments'
plt.title(title)
plt.legend(title="Starting Year", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.grid(True)
st.pyplot(plt)
