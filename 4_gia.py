# Importing necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Setting the scale and context for seaborn
plt.style.use('ggplot')
sns.set_context('notebook')

### Importing and Data Cleaning

# Importing the data from xlsx files using pandas
apportionment = pd.read_excel('data.xlsx', sheet_name = 'Apportionment', parse_dates = True)
hours = pd.read_excel('data.xlsx', sheet_name = 'Hours', parse_dates = True)
ctc = pd.read_excel('data.xlsx', sheet_name = 'Cost to Company')

# Removing the unnamed columns in the apportionment table 
apportionment = apportionment.loc[:, ~apportionment.columns.str.contains('^Unnamed')]

# Converting the date into the same format as the date format in hours table
apportionment['Date of Invoice'] = pd.to_datetime(apportionment['Date of Invoice'], dayfirst = True)

apportionment.head()

# Checking if there is any missing data
print(apportionment.isna().any())
print(hours.isna().any())
print(ctc.isna().any())

# Dropping the missing data
apportionment.dropna()
hours.dropna()

### Exploratory Data Analysis

## 2.1. Case types

# Prints out the unique case types using the unique method
apportionment['Case Type'].unique()

# Prints out the summary statistics of the final apportionment amount per case type
apportionment.groupby('Case Type').agg({'Final Apportioned Amount' : 'describe'})

# Plot to show the apportionment amount per case types
fig, ax = plt.subplots()
fig.set_size_inches([16,9])
sns.boxplot( data = apportionment, x = 'Case Type', y = 'Final Apportioned Amount')
plt.xticks(rotation = 90)
plt.show()

# Same plot as above except we made log10('Final Apportioned Amount')
plt.clf()
sns.boxplot( data = apportionment, x = 'Case Type', y = 'Final Apportioned Amount')
plt.xticks(rotation = 90)
plt.yscale('log')
plt.show()

# Plot to show the apportionment amount per case types with respect to each lawyers
g = sns.catplot(data = apportionment, 
            x = 'Case Type', 
            y = 'Final Apportioned Amount', 
            col = 'User', 
            kind = 'box',
            col_wrap = 3)
g.set_titles('{col_name}')
g.set(xlabel = 'Case Types', ylabel = 'Final Apportioned Amount')
plt.xticks(rotation = 90)
plt.show()

# Above plot does not show appropriate xtick labelling.
def lawyer (x):
    """ Function to subset each lawyers from the apportionment data frame """
    return apportionment[apportionment['User'] == x]

def snsbox (data):
    """ Function to plot boxplots using seaborn """
    sns.catplot(data = data, x = 'Case Type', y = 'Final Apportioned Amount', hue = 'Status', kind = 'box')
    plt.show()