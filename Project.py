import pandas as pd
import matplotlib.pyplot as plt

property_price = pd.read_csv('PPR_ALL.csv', encoding = 'latin1')

print(property_price.head())
