# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 22:11:15 2021

@author: Tejasvi Kashyap
"""
import numpy as np
import pandas as pd
import folium
import streamlit as st
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import altair as alt
from PIL import Image

st.set_page_config(layout="wide")
def data_pre(cord):
    return cord[0:5]

@st.cache
def loadImages():
    weStayAtHome = Image.open('yuioi.jpg')
    myth1 = Image.open('myth1.jpeg')
    myth2 = Image.open('myth2.jpeg')
    myth3 = Image.open('myth3.jpeg')
    myth4 = Image.open('myth4.jpeg')
    myth5 = Image.open('myth5.jpeg')
    myth6 = Image.open('myth6.jpeg')
    
    images = {
        "weStayAtHome": weStayAtHome,
        "myth1": myth1,
        "myth2": myth2,
        "myth3": myth3,
        "myth4": myth4,
        "myth5": myth5,
        "myth6": myth6
        }
    return images

@st.cache
def load_data():
    info = pd.read_html("http://www.quickgs.com/latitudinal-and-longitudinal-extents-of-india-indian-states-and-cities/") 
    #convering the table data into DataFrame
    coordinates = pd.DataFrame(info[0])
    coordinates['Latitude']  = coordinates['Latitude'].apply(data_pre).astype('float')
    coordinates['Longitude'] = coordinates['Longitude'].apply(data_pre).astype('float')
    #print(coordinates)
    # Retreving the LIVE COVID19 Stats from Wikipedia
    coronastats = pd.read_html('https://prsindia.org/covid-19/cases')
    #Convert to DataFrame
    covid19 = pd.DataFrame(coronastats[0])
    #st.write(covid19)
    covid19=(covid19.loc[:,["State/UT","Confirmed Cases","Active Cases","Cured/Discharged","Death"]])
    covid19.columns = ['State','Total cases','Active cases','Recoveries','Deaths']
    #st.write(coordinates)
    #st.write(covid19)
    final_data = pd.merge(coordinates, covid19, how ='inner', on ='State')   
    return final_data


@st.cache
def loadStatewiseCasesData(states):
    ind_info = pd.read_csv("covid_19_india.csv")
    state_info=pd.DataFrame(ind_info)
    
    state_info.rename(columns={'State/UnionTerritory': 'State'}, inplace=True)
    state_info=pd.merge(state_info,states['State'],how="inner", on="State")
    state_info['Date']=state_info['Date'].astype('datetime64[ns]')
    return state_info

@st.cache
def loadStatewiseVaccineData(states):
    ind_inf = pd.read_csv("covid_vaccine_statewise.csv")
    statewiseVaccination = pd.DataFrame(ind_inf)
    statewiseVaccination.rename(columns={
        'State/UnionTerritory': 'State',
        'Male(Individuals Vaccinated)': 'Male',
        'Female(Individuals Vaccinated)': 'Female',
        'Updated On': 'Date'
    }, inplace=True)
    statewiseVaccination = pd.merge(statewiseVaccination, states['State'], how = 'inner', on = 'State')
    statewiseVaccination['Date'] = statewiseVaccination['Date'].astype('datetime64[ns]')
    return statewiseVaccination
    

@st.cache
def loadCumulativeStatewiseVaccination():
    statewiseVaccination = pd.DataFrame(statewiseVaccineData.loc[:,['State','Male','Female']])
    statewiseVaccination = pd.merge(indiaCovidData['State'], statewiseVaccination, how='inner', on='State')
    statewiseVaccination=pd.DataFrame(statewiseVaccination.groupby('State')['Male','Female'].max().reset_index())
    statewiseVaccination['Sum'] = [0 for i in range(len(statewiseVaccination['State']))]
    for i in range(len(statewiseVaccination['State'])):
        statewiseVaccination['Sum'][i] = statewiseVaccination['Male'][i] + statewiseVaccination['Female'][i]
    statewiseVaccination = statewiseVaccination.set_index('State').sort_values('Sum').reset_index()
    statewiseVaccination = statewiseVaccination.drop(['Sum'], axis = 1)
    statewiseVaccination = statewiseVaccination.melt('State', var_name='Gender', value_name='Vaccinated')
    return statewiseVaccination

@st.cache
def loadCumulativeStatewiseCases():
    indiaCases = pd.DataFrame(indiaCovidData.loc[:,["State","Active cases","Deaths","Recoveries"]])
    indiaCases = pd.merge(indiaCovidData['State'],indiaCases,
                          how = "inner", on="State")
    
    indiaCases['Sum'] = [0 for i in range(len(indiaCases['State']))]
    for i in range(len(indiaCases['State'])):
        indiaCases['Sum'][i] = indiaCases['Deaths'][i] + indiaCases['Active cases'][i] + indiaCases['Recoveries'][i]
        
    indiaCases = indiaCases.set_index('State').sort_values(by = 'Sum').reset_index()
    indiaCases = indiaCases.drop(['Sum'], axis = 1)
    indiaCases = indiaCases.melt('State', var_name='Status', value_name='Total')
    return indiaCases


def plt_india_map():
    india = folium.Map(location = [20.5937,78.9629],zoom_start=4.0)
    #adding to map
    for state,lat,long,total_cases,Death,Recov,Active in zip(list(ind_map['State']),list(ind_map['Latitude']),list(ind_map['Longitude']),list(ind_map['Total cases']),list(ind_map['Deaths']),list(ind_map['Recoveries']),list(ind_map['Active cases'])):
        #for creating circle marker
        folium.CircleMarker(location = [lat,long],
                           radius = 5,
                           color='red',
                           fill = True,
                           fill_color="red").add_to(india)
        #for creating marker
        folium.Marker(location = [lat,long],
                      # adding information that need to be displayed on popup
                      popup=folium.Popup(('<strong><b>State  : '+state+'</strong> <br>' +
                        '<strong><b>Total Cases : '+str(total_cases)+'</strong><br>' +
                        '<strong><font color= red>Deaths : </font>'+str(Death)+'</strong><br>' +
                        '<strong><font color=green>Recoveries : </font>'+str(Recov)+'</strong><br>' +
                        '<strong><b>Active Cases : '+str(Active)+'</strong><br>' ),max_width=200)).add_to(india)
    #to show the map
    return india


def chloropeth_map(selected_state):
    json1 = f"states_india.geojson"
    m = folium.Map(location=ind_map.query("State == @selected_state")[['Latitude','Longitude']], tiles='CartoDB positron',name="Light Map",
               zoom_start=4.0,
               attr='My Data Attribution')
    
    choice = ['Total cases','Active cases', 'Recoveries', 'Deaths']
    choice_selected = st.sidebar.selectbox("Select Choice ", choice)
    folium.Choropleth(
        geo_data=json1,
        name="choropleth",
        data=ind_map,
        columns=["State", choice_selected],
        key_on="feature.properties.st_nm",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=.1,
        legend_name=choice_selected+"(%)",
    ).add_to(m)
    folium.features.GeoJson('states_india.geojson', name="LSOA Code",
                               popup=folium.features.GeoJsonPopup(fields=['st_nm'])).add_to(m)
    return m
    



def loadSelectedStateCases(state_info,selected_state):
    stwise=state_info.groupby('State')['Confirmed','Cured','Deaths'].sum().reset_index()
    #selected_state=st.sidebar.selectbox("Select State", stwise['State'])    
    stwise=state_info.query('State == @selected_state').reset_index().set_index('Date')
    stwise['PerDayCured']=[0 for i in range(len(stwise['Cured']))]
    stwise['PerDayDeath']=[0 for i in range(len(stwise['Deaths']))]
    stwise['PerDayConfirmed']=[0 for i in range(len(stwise['Confirmed']))]

    for i in range(1,len(stwise['Cured'])):
        stwise['PerDayCured'][i]=stwise['Cured'][i]-stwise['Cured'][i-1]
        stwise['PerDayDeath'][i]=stwise['Deaths'][i]-stwise['Deaths'][i-1]
        stwise['PerDayConfirmed'][i]=stwise['Confirmed'][i]-stwise['Confirmed'][i-1]
    stwise=stwise[stwise.PerDayConfirmed>=0]
    stwise=stwise[stwise.PerDayDeath>=0]
    stwise=stwise[stwise.PerDayCured>=0]
    return stwise

def loadSelectedStateVaccinated(statewiseVaccineData, selected_state):
    #st.write(statewiseVaccineData.columns)
    statewiseVaccineData.rename(columns={
        'First Dose Administered': 'FirstDose',
        'Second Dose Administered': 'SecondDose'        
        }, inplace=True)
    #st.write(statewiseVaccineData.columns)
    #selectedStateVaccinated = statewiseVaccineData.groupby('State')['Male','Female','FirstDose','SecondDose'].sum().reset_index()
    selectedStateVaccinated = statewiseVaccineData.query('State == @selected_state').reset_index()
    #st.write(selectedStateVaccinated.columns)
    selectedStateVaccinated.dropna(
        subset = ["Female",
                  
                  "Male"
                  
    ], inplace = True)
    
    selectedStateVaccinated["PerDayFemale"] = [0 for i in range(len(selectedStateVaccinated["Female"]))]
    selectedStateVaccinated["PerDayMale"] = [0 for i in range(len(selectedStateVaccinated["Male"]))]
    selectedStateVaccinated["PerDayFirstDose"] = [0 for i in range(len(selectedStateVaccinated["FirstDose"]))]
    selectedStateVaccinated["PerDaySecondDose"] = [0 for i in range(len(selectedStateVaccinated["SecondDose"]))]
    for i in range(1,len(selectedStateVaccinated["Female"])):
        selectedStateVaccinated["PerDayFemale"][i] = selectedStateVaccinated["Female"][i] - selectedStateVaccinated["Female"][i-1]
        selectedStateVaccinated["PerDayMale"][i] = selectedStateVaccinated["Male"][i] - selectedStateVaccinated["Male"][i-1]
        selectedStateVaccinated["PerDayFirstDose"][i] = selectedStateVaccinated["FirstDose"][i] - selectedStateVaccinated["FirstDose"][i-1]
        selectedStateVaccinated["PerDaySecondDose"][i] = selectedStateVaccinated["SecondDose"][i] - selectedStateVaccinated["SecondDose"][i-1]

    selectedStateVaccinated = selectedStateVaccinated[selectedStateVaccinated.PerDayFemale >= 0]
    selectedStateVaccinated = selectedStateVaccinated[selectedStateVaccinated.PerDayMale >= 0]
    selectedStateVaccinated = selectedStateVaccinated[selectedStateVaccinated.PerDayFirstDose >= 0]
    selectedStateVaccinated = selectedStateVaccinated[selectedStateVaccinated.PerDaySecondDose >= 0]
    
    selectedStateVaccinated.set_index("Date", inplace=True)
    #st.write(selectedStateVaccinated)
    return selectedStateVaccinated

'''Sahyog Bharat is a portal where citizens can find and visualize covid related information and gives  them a brief understanding of the covid trends in various domains .
As the name suggests, it helps the citizens gain an overview of current active cases , recovered cases,  and total deaths across the states in india.
'''

indiaCovidData = load_data()
statewiseCovidData = loadStatewiseCasesData(indiaCovidData)
statewiseVaccineData = loadStatewiseVaccineData(indiaCovidData)
images = loadImages()

st.image(images['weStayAtHome'], use_column_width='always')

col1,col3,col4,col5,col6 = st.beta_columns(5)

col1.image(images['myth1'], use_column_width='always', output_format='png')
#col2.image(images['myth2'], use_column_width='always', output_format='png')
col3.image(images['myth3'], use_column_width='always', output_format='png')
col4.image(images['myth4'], use_column_width='always', output_format='png')
col5.image(images['myth5'], use_column_width='always', output_format='png')
col6.image(images['myth6'], use_column_width='always', output_format='png')


ind_map=indiaCovidData
#st.write(ind_map)

st.header("Map of India")
indiaMap=plt_india_map()
map1,map2,map3 = st.beta_columns([5,1,5])
with map1:
    folium_static(indiaMap,width=600)

selected_state=st.sidebar.selectbox("Select State", ind_map['State'],index=12)
indiaChloroMap=chloropeth_map(selected_state)
with map3:
    folium_static(indiaChloroMap,width=600)
    
    
typeOfData = st.sidebar.selectbox("Select the type of Data", ["Covid 19 Cases","Covid 19 Vaccination"])

cumulativeStatewiseCases = loadCumulativeStatewiseCases()
cumulativeStatewiseVaccination = loadCumulativeStatewiseVaccination()

select_graph=st.multiselect("Select the Graph you want:",['Line','Area','Bar'])

if typeOfData == "Covid 19 Cases":
    st.write(alt.Chart(cumulativeStatewiseCases.reset_index()).mark_bar().encode(
        x=alt.X('State', sort=None),
        y='Total',
        color = 'Status',
        tooltip = ['State','Status','Total']
    ).properties(
        width = 1300,
        height = 500        
    ).interactive())
    selectedStateCases = loadSelectedStateCases(statewiseCovidData, selected_state)
    if 'Line' in select_graph:
        st.line_chart(selectedStateCases[['PerDayCured','PerDayDeath','PerDayConfirmed']])
    if 'Area' in select_graph:
        st.area_chart(selectedStateCases[['PerDayCured','PerDayDeath','PerDayConfirmed']])
    if 'Bar' in select_graph:
        st.bar_chart(selectedStateCases[['PerDayCured','PerDayDeath','PerDayConfirmed']])
        
else:
    st.write(alt.Chart(cumulativeStatewiseVaccination.reset_index()).mark_bar().encode(
        x=alt.X('State', sort=None),
        y='Vaccinated',
        color = 'Gender',
        tooltip = ['State', 'Gender','Vaccinated']
    ).properties(
        width = 1300,
        height = 500        
    ).interactive())
    selectedStateVaccinated = loadSelectedStateVaccinated(statewiseVaccineData, selected_state)
    if 'Line' in select_graph:
        st.line_chart(selectedStateVaccinated[["PerDayFirstDose","PerDaySecondDose"]])
        st.line_chart(selectedStateVaccinated[["Male","Female"]])
    if 'Area' in select_graph:
        st.area_chart(selectedStateVaccinated[["PerDayFirstDose","PerDaySecondDose"]])
        st.area_chart(selectedStateVaccinated[["Male","Female"]])
    if 'Bar' in select_graph:
        st.bar_chart(selectedStateVaccinated[["PerDayFirstDose","PerDaySecondDose"]])
        st.bar_chart(selectedStateVaccinated[["Male","Female"]])

#st.write("Here")

#st.write(select_graph)

    


    





