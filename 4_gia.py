# Importing necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Setting the scale and context for seaborn
plt.style.use('ggplot')
sns.set_context('paper')

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

# Merging rows in the hours table
hours = hours.groupby(['Date', 'User/Full Name']).agg({'Actual Hours' : 'sum'}).reset_index()
hours.head()

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

# Same plot as above except we made a mathematical transformation - log('Final Apportioned Amount')
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

# Initialize a list of lawyers
Lawyers = ['Lawyer A', 'Lawyer B', 'Lawyer C', 'Lawyer D', 'Lawyer E', 'Lawyer F', 'Lawyer G']

# Looping through each lawyers and make a plot
for lawyer in Lawyers:
    l = apportionment[apportionment['User'] == lawyer]
    sns.catplot(data = l, x = 'Case Type', y = 'Final Apportioned Amount', hue = 'Status', kind = 'box').set(title = lawyer)
    plt.xticks( rotation = 90)
    plt.show()

## 2.2. Correlation between clocked time and apportioned amount

# Merging apportionment table and hours table to investigate relationship between clocked hours and apportioned amount
apportionment_hours = apportionment.merge(hours, 
left_on = ['Date of Invoice', 'User'], 
right_on = ['Date', 'User/Full Name'], 
how = 'outer', 
suffixes = ['_a','_h'])

# Dropping redundant columns
apportionment_hours = apportionment_hours.drop(['Date', 'User/Full Name'], axis = 1)

# Renaming the column Date of Invoice to Date
apportionment_hours['Date'] = pd.to_datetime(apportionment_hours['Date of Invoice'])

# Scatter plot between final apportioned amount and actual hours
sns.relplot(data = apportionment_hours, y = 'Final Apportioned Amount', x = 'Actual Hours', kind = 'scatter', hue = 'User')
plt.show()

# Correlation between final apportioned amount and actual hours
apportionment_hours['Final Apportioned Amount'].corr(apportionment_hours['Actual Hours'])

## 2.3. Lawyers reaching their target revenue?

# Grouping the data according to the month and lawyers
apportionment_months = apportionment_hours.groupby([apportionment_hours['Date'].dt.month, 'User']).agg({'Final Apportioned Amount' : 'sum'}).reset_index()

# Plotting the total apportioned amount per month with respect to each lawyers
g = sns.relplot(data = apportionment_months, 
            x = 'Date', 
            y = 'Final Apportioned Amount', 
            hue = 'User').set(title = 'Total revenue for each month', 
            xlabel = 'Month', 
            ylabel = 'Total apportioned amount')
plt.show()