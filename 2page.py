import streamlit as st
import pandas as pd
!pip install matplotlib
import matplotlib.pyplot as plt

# Function to load and preprocess the data
@st.cache_data
def load_data():
    filepath = "G:/pathsetter/all_files_in_one02.csv"
    data = pd.read_csv(filepath)
    data['Sale Date'] = pd.to_datetime(data['Sale Date'], errors='coerce')
    data[['Sales (Exc. Tax)', 'Tax', 'Sales(Inc. Tax)', 'Redeemed']] = data[['Sales (Exc. Tax)', 'Tax', 'Sales(Inc. Tax)', 'Redeemed']].replace(',', '', regex=True).astype(float)
    return data.dropna(subset=['Sale Date'])

# Function to calculate the count of repetitive guests at the same center
def count_repetitive_guests(group):
    guest_counts = group['Guest Name'].value_counts()
    repetitive_guest_count = guest_counts[guest_counts > 1].sum()
    return repetitive_guest_count if repetitive_guest_count else 0

data = load_data()
data['monthAndYear'] = data['Sale Date'].dt.to_period('M')

# Streamlit interface
st.title("Summary of Sales by Center")
month_year_options = data['monthAndYear'].astype(str).unique()
selected_month_year = st.selectbox('Select Month-Year:', month_year_options)

# Filter data based on selected month-year
filtered_data = data[data['monthAndYear'].astype(str) == selected_month_year]

center_summary = filtered_data.groupby('Center Name').apply(
    lambda group: pd.Series({
        'Total_Quantity': group['Qty'].sum(),
        'Total_Sales_Without_Tax': group['Sales (Exc. Tax)'].sum(),
        'Average_Sales_Without_Tax': group['Sales (Exc. Tax)'].mean(),
        'Repetitive_Guest_Count': count_repetitive_guests(group)
    })
).reset_index()

center_summary.index += 1  # Adjusting the index to start from 1

st.subheader(f"Summary of Sales by Center for {selected_month_year}")
st.write(center_summary)

# Custom y-axis formatter
def custom_formatter(x, _):
    if x >= 1e7:  # Crores
        return f'{x*1e-7:.1f} Cr'
    elif x >= 1e5:  # Lakhs
        return f'{x*1e-5:.1f} L'
    else:  # Thousands
        return f'{x*1e-3:.1f} K'

# After displaying the summary table
st.subheader(f"Sales from Monday to Sunday for {selected_month_year}")

# Extract the day name and group by it
daywise_data = filtered_data.groupby(filtered_data['Sale Date'].dt.day_name())['Sales (Exc. Tax)'].sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
ax = daywise_data.plot(kind='bar', color='lightblue', edgecolor='black')
ax.yaxis.set_major_formatter(plt.FuncFormatter(custom_formatter))
plt.ylabel('Sales (Exc. Tax)')
plt.title(f"Sales from Monday to Sunday for {selected_month_year}")
st.pyplot(plt.gcf())
plt.clf()

# Extract the year from the selected_month_year
selected_year = pd.Period(selected_month_year).year
yearly_data = data[data['Sale Date'].dt.year == selected_year].groupby(data['Sale Date'].dt.month_name())['Sales (Exc. Tax)'].sum().reindex(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
ax = yearly_data.plot(kind='bar', color='lightgreen', edgecolor='black')
ax.yaxis.set_major_formatter(plt.FuncFormatter(custom_formatter))
plt.ylabel('Sales (Exc. Tax)')
plt.title(f"Monthly Sales for the year {selected_year}")
st.pyplot(plt.gcf())
plt.clf()
