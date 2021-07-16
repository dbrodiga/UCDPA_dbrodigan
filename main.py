# Import required
import requests
import pandas as pd
import numpy as np

# Retrieving data from an online API
request = requests.get('https://www.alphavantage.co/query?function=OVERVIEW&symbol=AIG&apikey=2KMJ76XV3WQ5M9K7')

data = request.json()

print('The Book Value of AIG is ' + data['BookValue'] + ' and the Earnings per share figure is ' + data['EPS'] + '.')

# Importing a CSV file into a Pandas DataFrame
prop_price = pd.read_csv('PPR_ALL.csv', encoding='latin1', parse_dates=['Date of Sale (dd/mm/yyyy)'], dayfirst=True)

print(prop_price.head())
print(prop_price.info())

prop_price = prop_price.rename(columns={'Date of Sale (dd/mm/yyyy)': 'Date of Sale', 'Price ()': 'Price'})

# Remove duplicates
prop_price.drop_duplicates(inplace=True)

print(prop_price.info())

# Check for missing values
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


# Remove the € symbol which is stored as  and commas from the Price column and convert column to float
def convert_currency(val):
    new_val = val.replace(',', '').replace(' ', '')
    return float(new_val)


prop_price['Price'] = prop_price['Price'].apply(convert_currency)

# Create a new column with the price including VAT of 13.5% where it is not included
price_VAT = []
for value in prop_price['VAT Exclusive']:
    if value == 'Yes':
        price_VAT.append(1.135)
    else:
        price_VAT.append(1)

prop_price['Price inc VAT'] = prop_price['Price']*price_VAT

print(prop_price.info())

# Set the Date of Sale column as the index
# Sort the index so that the date of sale is in chronological order
prop_price_index = prop_price.set_index('Date of Sale')
prop_price_sorted = prop_price_index.sort_index()

print(prop_price_sorted.head())

# Create a column for Year and also one for month
prop_price['Year'] = prop_price['Date of Sale'].dt.year
prop_price['Month'] = prop_price['Date of Sale'].dt.month_name

print(prop_price.info())

# Grouping to show the min, max, median and mean price by county and year
# Changing the selected_co list allows visibility over any chosen counties
selected_co = ['Monaghan', 'Dublin']
prop_price_co = prop_price[prop_price['County'].isin(selected_co)]
prop_price_co = prop_price_co.groupby(['County', 'Year'])['Price inc VAT'].agg([min, max, np.mean, np.median])
print(prop_price_co)

# Merge DataFrames