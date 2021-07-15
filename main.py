# Import required
import requests
import pandas as pd

# Retrieving data from an online API
request = requests.get('https://www.alphavantage.co/query?function=OVERVIEW&symbol=AIG&apikey=2KMJ76XV3WQ5M9K7')

data = request.json()

print('The Book Value of AIG is ' + data['BookValue'] + ' and the Earnings per share figure is ' + data['EPS'] + '.')

# Importing a CSV file into a Pandas DataFrame
prop_price = pd.read_csv('PPR_ALL.csv', encoding='latin1', parse_dates=['Date of Sale (dd/mm/yyyy)'])

print(prop_price.head())
print(prop_price.info())

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

# Replace Irish with English in Description of Property
irish = ['Teach/?ras?n C?naithe Nua', 'Teach/Árasán Cónaithe Nua', 'Teach/Árasán Cónaithe Atháimhe']
english = ['New Dwelling house /Apartment', 'New Dwelling house /Apartment', 'Second-Hand Dwelling house /Apartment']
prop_price['Description of Property'] = prop_price['Description of Property'].replace(irish, english)
