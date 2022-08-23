# Importing necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Setting the scale and context for seaborn
plt.style.use('seaborn')
sns.set_context('paper')

"""
Importing & Pre Processing Data
"""

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

"""
Exploratory Data Analysis
"""

# Adding an extra column with month names
month_name = {1.0 : 'January',
            2.0 : 'February',
            3.0 : 'March',
            4.0 : 'April',
            5.0 : 'May',
            6.0 : 'June'}

def month_col (df, date):
    return df[date].apply(lambda x : month_name[x])

# Prints out the unique case types using the unique method
apportionment['Case Type'].unique()

# Prints out the summary statistics of the final apportionment amount per case type
apportionment.groupby('Case Type').agg({'Final Apportioned Amount' : 'describe'})


""" Case type count """
# Plot to show amount of cases managed
sns.catplot(data = apportionment,
                x = 'Case Type',
                kind = 'count',
                aspect = 2)
plt.ylabel('Count')
plt.title('Amount of cases managed')
plt.xticks(rotation = 90)
plt.show()

""" Revenue according to each case type wrt month """
# Grouping the apportionment table by month and case type
apportionment_by_month_case = apportionment.groupby([apportionment['Date of Invoice'].dt.month, 'Case Type']).agg({'Final Apportioned Amount' : 'sum'}).reset_index()

apportionment_by_month_case['Month'] = month_col(apportionment_by_month_case, 'Date of Invoice')

# Plot to show apportionment ammount per case type
sns.catplot(data = apportionment_by_month_case,
                x = 'Case Type',
                y = 'Final Apportioned Amount',
                kind = 'bar',
                ci = None,
                col = 'Month',
                aspect = 2,
                dodge = True,
                palette = 'Set2')
plt.xticks( rotation = 90)
plt.ylabel('Apportioned amount ($)')
plt.title('Apportioned amount per case type')
plt.show()

""" Monthly Revenue """
# Grouping the apportionment table by month only
apportionment_by_month = apportionment.groupby(apportionment['Date of Invoice'].dt.month).agg({'Final Apportioned Amount' : 'sum'}).reset_index()

apportionment_by_month['Month'] = month_col(apportionment_by_month, 'Date of Invoice')
print(apportionment_by_month)

# Plotting the total apportioned amount per month
sns.relplot(data = apportionment_by_month,
                x = 'Month',
                y = 'Final Apportioned Amount',
                ci = None,
                kind = 'line',
                marker = 'o',
                aspect = 2)
plt.title('Total monthly apportioned amount')
plt.ylabel('Apportioned amount ($)')
plt.show()

""" Monthly Revenue by Payment Status """
# Grouping the apportionment table by month and payment status
apportionment_by_month_status = apportionment.groupby([apportionment['Date of Invoice'].dt.month, 'Status']).agg({'Final Apportioned Amount' : 'sum'}).reset_index()

apportionment_by_month_status['Month'] = month_col(apportionment_by_month_status, 'Date of Invoice')

# Plotting total apportioned amount per month by status
sns.relplot(data = apportionment_by_month_status,
            x = 'Month',
            y = 'Final Apportioned Amount',
            ci = None,
            kind = 'line',
            hue = 'Status',
            aspect = 2,
            marker = 'o',
            palette = 'Paired')
plt.ylabel('Apportioned amount ($)')
plt.title('Total monthly apportioned amount')
plt.show()

# Cumulative sum
apportionment_by_month['Cumulative apportionment'] = apportionment_by_month['Final Apportioned Amount'].cumsum()
paid = apportionment_by_month_status.loc[apportionment_by_month_status['Status'] == 'Paid']
unpaid = apportionment_by_month_status.loc[apportionment_by_month_status['Status'] == 'Awaiting Payment']

paid['Cumulative paid apportionment'] = paid['Final Apportioned Amount'].cumsum()
unpaid['Cumulative unpaid apportionment'] = unpaid['Final Apportioned Amount'].cumsum()

# Plotting cumulative sum
plt.plot(apportionment_by_month['Month'], apportionment_by_month['Cumulative apportionment'], label = 'Cumulative apportioned amount')
plt.plot(paid['Month'], paid['Cumulative paid apportionment'], label = 'Cumulative paid apportioned amount')
plt.plot(unpaid['Month'], unpaid['Cumulative unpaid apportionment'], label = 'Cumulative unpaid apportioned amount')
plt.ylabel('Apportioned amount ($)')
plt.xlabel('Month')
plt.legend()
plt.show()

""" Monthly revenue from lawyers """
# Grouping the apportionment table by month and lawyer
apportionment_by_month_lawyer = apportionment.groupby([apportionment['Date of Invoice'].dt.month, 'User']).agg({'Final Apportioned Amount' : 'sum'}).reset_index()

apportionment_by_month_lawyer['Month'] = month_col(apportionment_by_month_lawyer, 'Date of Invoice')

# Plotting total apportioned amount per month by lawyer
sns.relplot(data = apportionment_by_month_lawyer,
            x = 'Month',
            y = 'Final Apportioned Amount',
            ci = None,
            kind = 'line',
            hue = 'User',
            aspect = 2,
            marker = 'o')
plt.ylabel('Apportioned amount ($)')
plt.title('Total monthly apportioned amount per lawyer')
plt.show()

""" Lawyer Specialization """
# Create a crosstable
lawyer_crosstab = pd.crosstab(apportionment['User'], apportionment['Case Type'])
lawyer_crosstab

# Plotting a heatmap to visualize which lawyers can do which cases better(?)
sns.heatmap(lawyer_crosstab,
            cmap = 'rocket_r',
            linewidth = 1,
            linecolor = 'w',
            annot = True)
plt.title('Types of cases managed by each lawyers')
plt.show()

""" Unpaid cases count """
# Plotting a countplot to see how many cases are paid/awaiting payment
fig, ax = plt.subplots()
ax = sns.countplot( x = 'Status', data = apportionment)
plt.ylabel('Count')
plt.xlabel('Payment status')
plt.title('Amount of cases managed according to payment status')
plt.show()

# Plotting a countplot to see how many cases are paid/awaiting payment
sns.countplot( x = 'Status', data = apportionment, hue = apportionment['Date of Invoice'].dt.month)
plt.legend(['January', 'February', 'March', 'April', 'May', 'June'])
plt.ylabel('Count')
plt.xlabel('Payment status')
plt.title('Amount of cases managed according to payment status')
plt.show()

""" Correlation between clocked hour and apportioned amount """ # double check the join
# Merging apportionment table and hours table to investigate relationship between clocked hours and apportioned amount
apportionment_hours = apportionment.merge(hours, left_on = ['Date of Invoice', 'User'], right_on = ['Date', 'User/Full Name'], how = 'outer', suffixes = ['_a','_h'])

# Dropping redudant columns
apportionment_hours = apportionment_hours.drop(['Date', 'User/Full Name'], axis = 1)

# Renaming the column Date of Invoice to Date
apportionment_hours['Date'] = pd.to_datetime(apportionment_hours['Date of Invoice'])

# Scatter plot between final apportioned amount and actual hours
sns.lmplot(data = apportionment_hours,
            y = 'Final Apportioned Amount',
            x = 'Actual Hours', 
            aspect = 2, 
            line_kws = {'color' : 'black'},
            scatter_kws = {'alpha' : 0.7})
plt.title('Scatter plot between apportioned amount against actual hours')
plt.xlabel('Apportioned amount ($)')
plt.show()

# Correlation between final apportioned amount and actual hours
print('Correlation between clocked hours and apportioned amount: ' + str(round(apportionment_hours['Final Apportioned Amount'].corr(apportionment_hours['Actual Hours']),2)))

""" Clocked hour by each lawyer """
# Plotting hours clocked by each lawyers
sns.relplot(data = hours,
            x = 'Date',
            y = 'Actual Hours',
            kind = 'line',
            aspect = 2,
            ci = None,
            hue = 'User/Full Name')
plt.axhline(y = 10,
            color = 'black',
            linestyle = '-')
plt.ylabel('Clocked hours')
plt.title('Amount of hours clocked by each lawyer')
plt.show()

""" Average clocked hour by each lawyer """
print(hours.groupby('User/Full Name').agg({'Actual Hours' : 'mean'}))

""" Lawyers meeting their target revenue? """
# Merging apportioned amount by month & lawyer with ctc table
kpi = apportionment_by_month_lawyer.merge(ctc,
                                        how = 'outer',
                                        on = 'User')

# Initializing condition list, choicelist and default for np.select function
condlist = [kpi['Final Apportioned Amount'] > kpi['Mthly 4X'],
            kpi['Final Apportioned Amount'] > kpi['Mthly 3X'],
            kpi['Final Apportioned Amount'] > kpi['Mthly 2X'],
            kpi['Final Apportioned Amount'] > kpi['Mthly 1X']]

choicelist = ['> 4X', '> 3X', '> 2X', '> 1X']

default = 'Not met'

kpi['kpi'] = np.select(condlist, choicelist, default)

# Subsetting the data frame according to each lawyers
def kpidf(x):
    return kpi.loc[kpi['User'] == x]

a_kpi = kpidf('Lawyer A')
b_kpi = kpidf('Lawyer B')
c_kpi = kpidf('Lawyer C')
d_kpi = kpidf('Lawyer D')
e_kpi = kpidf('Lawyer E')
f_kpi = kpidf('Lawyer F')
g_kpi = kpidf('Lawyer G')

def kpiplot(df, ctc, letter):
    sns.relplot(x = 'Month',
                y = 'Final Apportioned Amount',
                kind = 'line',
                marker = 'X',
                aspect = 2,
                data = df)
    plt.axhline(y = ctc, linestyle = '-', alpha = 0.5, color = 'g')
    plt.axhline(y = 2 * ctc, linestyle = '--', alpha = 0.5, color = 'g')
    plt.axhline(y = 3 * ctc, linestyle = '-.', alpha = 0.5, color = 'g')
    plt.axhline(y = 4 * ctc, linestyle = ':', alpha = 0.5, color = 'g')
    plt.title('Lawyer ' + str(letter) + '\'s apportioned amount and revenue targets')
    return plt.show()

kpiplot(a_kpi, 3600, 'A')
kpiplot(b_kpi, 6284.43, 'B')
kpiplot(c_kpi, 7320, 'C')
kpiplot(d_kpi, 6284.43, 'D')
kpiplot(e_kpi, 7320, 'E')
kpiplot(f_kpi, 10308.75, 'F')
kpiplot(g_kpi, 5699.43, 'G')

""" Revenue per case type """
# Plot to show apportionment ammount per case type
sns.boxenplot(data = apportionment,
                x = 'Case Type',
                y = 'Final Apportioned Amount',
                dodge = True)
plt.xticks( rotation = 90)
plt.show()

# Improve visual clarity by taking log()
sns.boxenplot(data = apportionment, 
            x = 'Case Type',
            y = 'Final Apportioned Amount')
plt.xticks( rotation = 90)
plt.yscale('log')
plt.show()