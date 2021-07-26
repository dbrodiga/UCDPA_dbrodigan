# Imports required
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Retrieving data from an online API - importing data milestone
request = requests.get('https://www.alphavantage.co/query?function=OVERVIEW&symbol=AIG&apikey=2KMJ76XV3WQ5M9K7')

data = request.json()

print('The Book Value of AIG is ' + data['BookValue'] + ' and the Earnings per share figure is ' + data['EPS'] + '.')

# Importing a CSV file into a Pandas DataFrame - importing data milestone
prop_price = pd.read_csv('PPR_ALL.csv', encoding='latin1', parse_dates=['Date of Sale (dd/mm/yyyy)'], dayfirst=True)

print(prop_price.head())
print(prop_price.info())

prop_price = prop_price.rename(columns={'Date of Sale (dd/mm/yyyy)': 'Date of Sale', 'Price ()': 'Price'})

# Remove duplicates - analyzing data milestone
prop_price.drop_duplicates(inplace=True)

print(prop_price.info())

# Check for missing values - analyzing data milestone
print(prop_price.isna().any())

# Remove the columns Postal Code and Property Size Description as there are so many missing values
# No accurate insights can be sought on those variables
# The below code could have filled in the missing values with a zero but this would add no benefit to the analysis
# prop_price.fillna(0, inplace=True)
prop_price.drop(['Postal Code', 'Property Size Description'], axis='columns', inplace=True)

print(prop_price.info())

# Replace Irish with English in Description of Property column
irish = ['Teach/?ras?n C?naithe Nua', 'Teach/Árasán Cónaithe Nua', 'Teach/Árasán Cónaithe Atháimhe']
english = ['New Dwelling house /Apartment', 'New Dwelling house /Apartment', 'Second-Hand Dwelling house /Apartment']
prop_price['Description of Property'] = prop_price['Description of Property'].replace(irish, english)


# Remove the € symbol which is stored as ' ' and commas from the Price column and convert column to float
# Use of functions - python milestone
def convert_currency(val):
    new_val = val.replace(',', '').replace(' ', '')
    return float(new_val)


prop_price['Price'] = prop_price['Price'].apply(convert_currency)

# Create a new column with the price including VAT of 13.5% where it is not included
# Use of Loop - analyzing data milestone
price_VAT = []
for value in prop_price['VAT Exclusive']:
    if value == 'Yes':
        price_VAT.append(1.135)
    else:
        price_VAT.append(1)

prop_price['Price inc VAT'] = prop_price['Price']*price_VAT

print(prop_price.info())

# Set the Date of Sale column as the index
# Sort the index so that the date of sale is in chronological order - analyzing data milestone
prop_price_index = prop_price.set_index('Date of Sale')
prop_price_sorted = prop_price_index.sort_index()

print(prop_price_sorted.head())

# Create a column for Year
prop_price['Year'] = prop_price['Date of Sale'].dt.year

print(prop_price.info())

# Grouping to show the min, max, median and mean price by county and year - analyzing data milestone
# Changing the selected_co list allows visibility over any chosen counties
# Use of Numpy and Lists
selected_co = ['Monaghan', 'Dublin']
prop_price_co = prop_price[prop_price['County'].isin(selected_co)]
prop_price_co = prop_price_co.groupby(['County', 'Year'])['Price inc VAT'].agg([min, max, np.mean, np.median])
print(prop_price_co)

# Subset the entire data frame for properties that were sold exactly twice in the time period
two_sales = prop_price[prop_price.groupby('Address').Address.transform('count') == 2]

# Merge DataFrames specifically for properties that were sold in both 2010 and 2020  - analyzing data milestone
two_sales_2010 = two_sales[two_sales['Year'] == 2010]
two_sales_2020 = two_sales[two_sales['Year'] == 2020]
sales_2010_2020 = two_sales_2010.merge(two_sales_2020, on='Address', suffixes=('_10', '_20'))
sales_2010_2020.to_csv('sales.csv')

# Use Matplotlib to create charts - Visualize milestone
dublin_prices = prop_price_co.loc['Dublin']
monaghan_prices = prop_price_co.loc['Monaghan']


# Define a function called plot_timeseries
def plot_timeseries(axes, x, y, color, xlabel, ylabel):
    axes.plot(x, y, color=color)
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel, color=color)
    axes.tick_params('y', colors=color)


fig, ax = plt.subplots()
plot_timeseries(ax, dublin_prices.index, dublin_prices['median'], "red", "Time", "Dublin Prices")
ax2 = ax.twinx()
plot_timeseries(ax2, monaghan_prices.index, monaghan_prices['median'], "Blue", "Time", "Monaghan Prices")
ax.set_title('Dublin and Monaghan median property prices')
plt.show()

# Create a pie chart to show the county where the largest portion of sales take place
county_sales = prop_price.groupby('County').agg('count')
county_sales = county_sales.sort_values('Date of Sale', ascending=False)
county_labels = county_sales.index
county_sales_volume = county_sales['Date of Sale']

fig_2, ax = plt.subplots()
ax.pie(county_sales_volume, labels=county_labels, autopct='%.0f%%')
plt.title('Volume of sales by County')
plt.show()


# Create a function to calculate the 75th percentile and group the lesser counts in an other category
def group_lower(df, column):
    county_counts = df.groupby(column).agg('count')
    pct_value = county_counts[lambda x: x.columns[0]].quantile(.75)
    values_below_pct_value = county_counts[lambda x: x.columns[0]].loc[lambda s: s < pct_value].index.values

    def fix_values(row):
        if row[column] in values_below_pct_value:
            row[column] = 'Other'
        return row
    county_group = df.apply(fix_values, axis=1).groupby(column).agg('count')
    return county_group


fig_3, ax = plt.subplots()
county_grouped = group_lower(prop_price, 'County')
county_labels_oth = county_grouped.index
county_sales_volume_oth = county_grouped['Date of Sale']
explode = (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1)
ax.pie(county_sales_volume_oth, labels=county_labels_oth, autopct='%.0f%%', explode=explode)
plt.title('Volume of sales by County')
plt.show()
