# Import Packages
import numpy as np
import pandas_datareader
import datetime
import pydst
import pandas as pd
import matplotlib.pyplot as plt

# a. Check Variables in NAN1
Dst = pydst.Dst(lang="da")
Dst.get_variables(table_id="NAN1")["values"][0][:20]

# b. Importing desired variables from NAN1

gdp = Dst.get_data(table_id = "NAN1", variables = {"TRANSAKT":["B1GQK"], "PRISENHED":["LAN_M"], "Tid":["*"]})
priv_cons = Dst.get_data(table_id = "NAN1", variables = {"TRANSAKT":["P31S1MD"], "PRISENHED":["LAN_M"], "Tid":["*"]})
publ_cons = Dst.get_data(table_id = "NAN1", variables = {"TRANSAKT":["P3S13D"], "PRISENHED":["LAN_M"], "Tid":["*"]})
inv = Dst.get_data(table_id = "NAN1", variables = {"TRANSAKT":["P51GD"], "PRISENHED":["LAN_M"], "Tid":["*"]})
exp = Dst.get_data(table_id = "NAN1", variables = {"TRANSAKT":["P6D"], "PRISENHED":["LAN_M"], "Tid":["*"]})
imp = Dst.get_data(table_id = "NAN1", variables = {"TRANSAKT":["P7K"], "PRISENHED":["LAN_M"], "Tid":["*"]})

# c. Generate lists of variables for later use
variable_list = ("B1GQK", "P31S1MD", "P3S13D", "P51GD", "P6D", "P7K") # we should make a loop for this
var_list = (gdp, priv_cons, publ_cons, inv, exp, imp)
var_list_string = ("gdp", "priv_cons", "publ_cons", "inv", "exp", "imp")      

# d. Drop unused variables
for i in var_list:
        """The loop below drops the unwanted columns from the var_list variables for the purpose of cleaning the dataset
        """
        i.drop(["TRANSAKT", "PRISENHED"], axis = 1, inplace = True)

var_list # Proves that our loop works

# e. Set data as timeseries
for i in var_list:
        """We can now index our data on time, this will ensure that it is treated as time-series.
        """
        i.index = i["TID"]

var_list # Proves that our loop works

# f. Rename variables
gdp = gdp.rename(columns = {"TID":"year", "INDHOLD":"gdp"}) #Renaming columns
"""Dataframe.rename(colums = {"original name":"new name"}) 
"""

priv_cons = priv_cons.rename(columns = {"TID":"year", "INDHOLD":"priv_cons"})
publ_cons = publ_cons.rename(columns = {"TID":"year", "INDHOLD":"publ_cons"})
inv = inv.rename(columns = {"TID":"year", "INDHOLD":"inv"})
exp = exp.rename(columns = {"TID":"year", "INDHOLD":"exp"})
imp = imp.rename(columns = {"TID":"year", "INDHOLD":"imp"})



# g. Creating Data Frame
data = pd.DataFrame(index=range(1966,2019), columns = ["year"]) # Create empty dataframe
data["year"] = range(1966, 2019)

data = pd.merge(data, gdp, how = "inner", on = ["year"]) #Partial Merge
""" how explains the type of merge, while on specifies the column we reference to
"""

data = pd.merge(data, priv_cons, how = "inner", on = ["year"])
data = pd.merge(data, publ_cons, how = "inner", on = ["year"])
data = pd.merge(data, inv, how = "inner", on = ["year"])
data = pd.merge(data, exp, how = "inner", on = ["year"])
data = pd.merge(data, imp, how = "inner", on = ["year"]) # Final dataset

# h. Indexing on time and delete year column
data.index = data["year"]
del data["year"]

# i. Subset data from 1980 to 2018
data = data.loc[1980 :]

# j. Correcting for comma separator and conver to floats
for i in var_list_string:
        """ This code is designed in order to change comma-separator
        """
        data[i] = (data[i].replace(",",".", regex=True))
        """ This converts the variables from "strings" to "floats"
        """
        data[i] = data[i].astype(float)
        
# k. Generate Gross Net Exports, 2010-chained value (bn. kr.)
data["nx"] = data["exp"] - data["imp"]
nx = data["nx"]

# l. Update var_list and var_list_string to include "nx"
var_list = (gdp, priv_cons, publ_cons, inv, exp, imp, nx)
var_list_string = ("gdp", "priv_cons", "publ_cons", "inv", "exp", "imp", "nx")

# m. Generate percentage change of variables
data_pct_change = data.pct_change()
data_pct_change = data_pct_change * 100 # in order to obtain percentage values

for i in var_list_string:
        data_pct_change = data_pct_change.rename(columns = {i:"pct. change in "+i})

data = pd.merge(data, data_pct_change, how = "inner", on = ["year"])

#Part 3 - data visualization
# calculations for piechart to compare compomnents in 1980 to 2018
sizes_1980 = [data.loc[1980, "priv_cons"], data.loc[1980, "publ_cons"], data.loc[1980, "inv"], data.loc[1980, "nx"]]
sizes_2018 = [data.loc[2018, "priv_cons"], data.loc[2018, "publ_cons"], data.loc[2018, "inv"], data.loc[2018, "nx"]]

labels = ["Private consumption", "Goverment spending", "Investment", "Net exports"]

fig1, ax = plt.subplots(1,2)
plt.style.use("tableau-colorblind10")

# 1980
ax[0].pie(sizes_1980, labels = labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax[0].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
ax[0].set_title("GDP components 1980")

#2018
ax[1].pie(sizes_2018, labels = labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax[1].axis('equal')
ax[1].set_title("GDP components 2018")

#adjustments
plt.subplots_adjust(wspace=1)

#add source
plt.annotate('Source: Danmarks Statistik - http://www.statistikbanken.dk/NAN1', (0,0), (0,0), fontsize = 7.5, xycoords = 'axes fraction', textcoords = 'offset points', va = 'top')

plt.show()

# we construct a function that can make our graphs
def my_graph(var1, varname1, var2 = "gdp", varname2 = "GDP", df = data):
    """
    df - a pandas dataframe containing the variables
    
    var1 - a string character that indicates the first variable of choice in our dataframe
    var2 - a string character that indicates the second variable of choice in our dataframe
    
    varname1 - a string character that indicates what we want the first variable to be called
    varname1 - a string character that indicates what we want the second variable to be called
    """
    
    fig, ax = plt.subplots(1, 2)
    plt.style.use("tableau-colorblind10")
    
    # Figure 1
    ax[0].plot(df.index,df[var2], linestyle = "--")
    ax[0].twinx().plot(df.index, df[var1])
    
    ax[0].set_xlabel("Years")
    ax[0].set_ylabel(varname2+" (Billion DKK)")
    ax[0].twinx().set_ylabel(varname1+" (Billions DKK)")
    ax[0].set_title(varname2+" and "+varname1)
    
    ax[0].legend(loc = 4, frameon = False)
    ax[0].twinx().legend(loc = 8, frameon = False)
    
    # Figure 2
    ax[1].plot(df.index,df["pct. change in "+var2], linestyle = "--")
    ax[1].twinx().plot(df.index, df["pct. change in "+var1])
    
    ax[1].set_xlabel("Years")
    ax[1].set_ylabel(varname2+" (growth rate)")
    ax[1].twinx().set_ylabel(varname1+" (growth rate)")
    ax[1].set_title(varname2+" and "+varname1)
    
    ax[1].legend(loc = 4, frameon = False)
    ax[1].twinx().legend(loc = 8, frameon = False)
    
    #Adjust size of plot
    plt.subplots_adjust(right = 2, wspace = 0.5, hspace = 0)
    
    #make annotation for source
    plt.annotate('Source: Danmarks Statistik - http://www.statistikbanken.dk/NAN1', (0,0), (0,-45), fontsize = 7.5, 
             xycoords = 'axes fraction', textcoords = 'offset points', va = 'top')
    
    plt.show()

my_graph("priv_cons", "Private consumption")
#summary statistics
#Pct change from 1980 to 2018
stats = round((((data.loc[2018]-data.loc[1980])/data.loc[1980])*100), 2)
stats = stats.dropna()
stats = pd.DataFrame(stats, columns = ["Pct. increase"])

# average pct increase
stats["Average pct. increase"] = [np.mean(data["pct. change in gdp"]), np.mean(data["pct. change in priv_cons"]), np.mean(data["pct. change in publ_cons"]), np.mean(data["pct. change in inv"]), np.mean(data["pct. change in exp"]), np.mean(data["pct. change in imp"]), np.mean(data["pct. change in nx"])]
stats["Average pct. increase"] = round(stats["Average pct. increase"],2)

stats.rename(index={"gdp":"Gross Domestic Product"}, inplace=True)
stats.rename(index={"priv_cons":"Private Consumption"}, inplace=True)
stats.rename(index={"publ_cons":"Goverment Expenditure"}, inplace=True)
stats.rename(index={"inv":"Investment"}, inplace=True)
stats.rename(index={"exp":"Export"}, inplace=True)
stats.rename(index={"imp":"Import"}, inplace=True)
stats.rename(index={"nx":"Net Export"}, inplace=True)

# Beginning value and end value
val_1980 = [data.loc[1980, "gdp"], data.loc[1980, "priv_cons"], data.loc[1980, "publ_cons"], data.loc[1980, "inv"], data.loc[1980, "exp"], data.loc[1980, "imp"], data.loc[1980, "nx"]]
val_2018 = [data.loc[2018, "gdp"], data.loc[2018, "priv_cons"], data.loc[2018, "publ_cons"], data.loc[2018, "inv"], data.loc[2018, "exp"], data.loc[2018, "imp"], data.loc[2018, "nx"]]

stats["1980 (bn DKK)"] = val_1980
stats["2018 (bn DKK)"] = val_2018

# gdp and private consumption
my_graph("priv_cons", "Private consumption")

# gdp and goverment spending
my_graph("publ_cons", "Goverment Expenditure")

# gdp and investment
my_graph("inv", "Investment")

# Net Exports
## Export and Import
fig, ax = plt.subplots()
plt.style.use("tableau-colorblind10")


ax.plot(data.index,data["exp"])
ax.plot(data.index,data["imp"], linestyle = "--")

ax.set_title("Export and Import")
ax.set_xlabel("Years")
ax.set_ylabel("(Billion DKK)")

ax.legend()
plt.show()

## gdp and net exports
my_graph("nx", "Net exports")

# concluding figure
# Drop non-used variables
stats2 = stats.drop(["Gross Domestic Product", "Export", "Import"])

# Figure
fig, ax = plt.subplots()
plt.style.use("tableau-colorblind10")

# Define Bars
ax.bar(stats2.index, stats2["1980 (bn DKK)"], label = "1980", width = 0.5)
ax.bar(stats2.index, stats2["2018 (bn DKK)"], label = "2018", width = 0.25, align = "edge")

# Axis Labels
ax.set_xticklabels(stats2.index, rotation = 90) #Rotating x-axis labels if long names
ax.set_ylabel("Billion DKK")

ax.set_title("GDP Components 1980 & 2018")
ax.legend()

plt.show()