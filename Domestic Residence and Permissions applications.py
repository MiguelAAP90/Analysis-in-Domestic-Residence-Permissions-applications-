# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 20:56:27 2024

@author: MAAP
"""

import pandas as pd
import pycountry
import pycountry_convert as pc
from difflib import get_close_matches
import matplotlib.pyplot as plt



path_file = "C:/Users/55a55b1e-cf64-4ca3-b34c-9be3c0ae8b70.xlsx" ###data from https://data.gov.ie/dataset/domestic-residence-permissions-applications-and-decisions-year-and-nationality

df = pd.read_excel(path_file)

df["Total_visas"] = df.loc[:,2017:2024].sum(axis=1)
df["Average"]=df.loc[:,2017:2024].sum(axis=1)/8


##check for correct name 
country_list = [country.name for country in pycountry.countries]

def correct_name(name):
    match = get_close_matches(name, country_list, n=1, cutoff=0.5)  # n=1 for best match, cutoff for accuracy
    return match[0] if match else name 

df["Nationality"] = df["Nationality"].apply(correct_name)


##check for continent
def country_continent(country):
    ##Handle countries not in .country_name_to_country_alpha2
    continents = {"Europe":['Holy See (Vatican City State)','Kosovo'],"Oceania" :['Pitcairn'],
                  "North America":['Sint Maarten (Dutch part)','United States Minor Outlying Islands'],
                  "Asia" : ["Timor-Leste"],"Africa" : ['Western Sahara'],"Antarctica":["Antarctica"]}
      
    try:
        country_code = pc.country_name_to_country_alpha2(country)
        continent_code = pc.country_alpha2_to_continent_code(country_code)
        continent_name = pc.convert_continent_code_to_continent_name(continent_code)
        return continent_name
        

    except KeyError:
        for i in continents:
            if country in continents[i]:
                return i
    else:
        return "Other" 
            
df["Continent"] = df["Nationality"].apply(country_continent)

df.to_excel("C:/Users/MAAP/Documents/second_DF.xlsx")

#################################################################################################
##modify dataframe for plotting
df_melted = df.melt(id_vars='Status',value_vars=list(range(2017, 2024)), var_name='Year', value_name='Count')
df_melted['Year'] = pd.to_numeric(df_melted['Year'])


# Plotting

### plt1
plt.figure(figsize=(10, 6))
for status in df_melted['Status'].unique():
    subset = df_melted[df_melted['Status'] == status]
    plt.bar(subset['Year'], subset['Count'], label=status)
plt.title("Visa Applications (2017-2024)")
plt.xlabel("Year")
plt.ylabel("Number of Applications")
plt.legend(title="Status")
plt.grid(True)
plt.show()

### plt2
approval_rate = []
refuse_rate = []
years= [2017,2018,2019,2020,2021,2022,2023,2024]



#### rate per Satatus
for i in years:
    x= float((df[i][df["Status"]== "Granted"].sum()/df["Total_visas"][df["Status"]== "Received"].sum())*100)
    y= float((df[i][df["Status"]== "Refused"].sum()/df["Total_visas"][df["Status"]== "Received"].sum())*100)
    approval_rate.append(x)
    refuse_rate.append(y)
    
### plot Approval and Refuse
plt.figure(figsize=(10,6))
plt.plot(years,approval_rate,label="Approval")
plt.plot(years,refuse_rate,label="Refuse")
plt.title("Visa Approval vs. Refusal Rates (2017-2024)")
plt.xlabel("Year")
plt.ylabel("Rate (%)")
plt.legend(title="Trype")


###group by continents to plot 
df_grouped = df.groupby(["Continent","Status"])["Total_visas"].sum().reset_index()
df_grouped['Continent_Index'] = pd.factorize(df_grouped['Continent'])[0]
##plot 3
# Scatter plot with different colors for each Status
plt.figure(figsize=(10, 6))
for status in df_grouped['Status'].unique():
    subset = df_grouped[df_grouped['Status'] == status]
    plt.scatter(subset['Continent_Index'], subset['Total_visas'], label=status)

#### labels
plt.xticks(df_grouped['Continent_Index'].unique(), df_grouped['Continent'].unique(), rotation=45)
plt.xlabel("Continent")
plt.ylabel("Total Visas")
plt.title("Scatter Plot of Visa Applications by Continent and Status")
plt.legend(title="Status")
plt.grid(True)


plt.show()
plt.clf()


