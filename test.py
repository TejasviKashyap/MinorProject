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


def loadImages():
    weStayAtHome = Image.open('yuioi.jpg')
    myth1 = Image.open('myth1.jpeg')
    myth2 = Image.open('myth2.jpeg')
    myth3 = Image.open('myth3.jpeg')
    myth4 = Image.open('myth4.jpeg')
    myth5 = Image.open('myth5.jpeg')
    myth6 = Image.open('myth6.jpeg')
    breath = Image.open('breath.jpg')
    chills = Image.open('chills.jpg')
    cough = Image.open('cough.jpg')
    fever = Image.open('fever.jpg')
    lossOfSmell = Image.open('loss of smell.jpg')
    muscle = Image.open('muscle.jpg')
    soreThroat = Image.open('sore throat.jpg')
    covidInstructions = Image.open('Screenshot (407).png')
    
    images = {
        "weStayAtHome": weStayAtHome,
        "myth1": myth1,
        "myth2": myth2,
        "myth3": myth3,
        "myth4": myth4,
        "myth5": myth5,
        "myth6": myth6,
        "breath": breath,
        "chills": chills,
        "cough": cough,
        "soreThroat": soreThroat,
        "muscle": muscle,
        "fever": fever,
        "lossOfSmell": lossOfSmell,
        "covidInstructions": covidInstructions
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
    indiaCases = pd.DataFrame(indiaCovidData.loc[:,["State","Active cases","Deaths"]])
    indiaCases = pd.merge(indiaCovidData['State'],indiaCases,
                          how = "inner", on="State")
    
    indiaCases['Sum'] = [0 for i in range(len(indiaCases['State']))]
    for i in range(len(indiaCases['State'])):
        indiaCases['Sum'][i] = indiaCases['Deaths'][i] + indiaCases['Active cases'][i]
        
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


def chloropeth_map(choice_selected):
    json1 = f"states_india.geojson"
    m = folium.Map(location=[28.59,77.22], tiles='CartoDB positron',name="Light Map",
               zoom_start=4.0,
               attr='My Data Attribution')
    
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
        'Second Dose Administered': 'SecondDose',
        #"18-30 years (Age)": 'Age18to30',
        "18-45 years (Age)": 'Age18to45',
        "45-60 years (Age)": 'Age45to60',
        "60+ years (Age)": 'Age60plus'        
        }, inplace=True)
    #st.write(statewiseVaccineData.columns)
    #selectedStateVaccinated = statewiseVaccineData.groupby('State')['Male','Female','FirstDose','SecondDose'].sum().reset_index()
    selectedStateVaccinated = statewiseVaccineData.query('State == @selected_state').reset_index()
    #st.write(selectedStateVaccinated.columns)
    selectedStateVaccinated.dropna(
        subset = ["Female",                  
                  "Male",
                  #"Age18to30",
                  "Age18to45",
                  "Age45to60",
                  "Age60plus"
    ], inplace = True)
    
    selectedStateVaccinated["PerDayFemale"] = [0 for i in range(len(selectedStateVaccinated["Female"]))]
    selectedStateVaccinated["PerDayMale"] = [0 for i in range(len(selectedStateVaccinated["Male"]))]
    selectedStateVaccinated["PerDayFirstDose"] = [0 for i in range(len(selectedStateVaccinated["FirstDose"]))]
    selectedStateVaccinated["PerDaySecondDose"] = [0 for i in range(len(selectedStateVaccinated["SecondDose"]))]
    #selectedStateVaccinated["PerDay18to30"] = [0 for i in range(len(selectedStateVaccinated["Age18to30"]))]
    selectedStateVaccinated["PerDay18to45"] = [0 for i in range(len(selectedStateVaccinated["Age18to45"]))]
    selectedStateVaccinated["PerDay45to60"] = [0 for i in range(len(selectedStateVaccinated["Age45to60"]))]
    selectedStateVaccinated["PerDay60plus"] = [0 for i in range(len(selectedStateVaccinated["Age60plus"]))]
    #st.write(selectedStateVaccinated)
    selectedStateVaccinated=selectedStateVaccinated.reset_index()
    for i in range(1,len(selectedStateVaccinated["Female"])):
        selectedStateVaccinated["PerDayFemale"][i] = selectedStateVaccinated["Female"][i] - selectedStateVaccinated["Female"][i-1]
        selectedStateVaccinated["PerDayMale"][i] = selectedStateVaccinated["Male"][i] - selectedStateVaccinated["Male"][i-1]
        selectedStateVaccinated["PerDayFirstDose"][i] = selectedStateVaccinated["FirstDose"][i] - selectedStateVaccinated["FirstDose"][i-1]
        selectedStateVaccinated["PerDaySecondDose"][i] = selectedStateVaccinated["SecondDose"][i] - selectedStateVaccinated["SecondDose"][i-1]
        #selectedStateVaccinated["PerDay18to30"][i] = selectedStateVaccinated["Age18to30"][i] - selectedStateVaccinated["Age18to30"][i-1]
        selectedStateVaccinated["PerDay18to45"][i] = selectedStateVaccinated["Age18to45"][i] - selectedStateVaccinated["Age18to45"][i-1]
        selectedStateVaccinated["PerDay45to60"][i] = selectedStateVaccinated["Age45to60"][i] - selectedStateVaccinated["Age45to60"][i-1]
        selectedStateVaccinated["PerDay60plus"][i] = selectedStateVaccinated["Age60plus"][i] - selectedStateVaccinated["Age60plus"][i-1]
    selectedStateVaccinated = selectedStateVaccinated[selectedStateVaccinated.PerDayFemale >= 0]
    selectedStateVaccinated = selectedStateVaccinated[selectedStateVaccinated.PerDayMale >= 0]
    selectedStateVaccinated = selectedStateVaccinated[selectedStateVaccinated.PerDayFirstDose >= 0]
    selectedStateVaccinated = selectedStateVaccinated[selectedStateVaccinated.PerDaySecondDose >= 0]
    #selectedStateVaccinated = selectedStateVaccinated[selectedStateVaccinated.PerDay18to30 >= 0]
    selectedStateVaccinated = selectedStateVaccinated[selectedStateVaccinated.PerDay18to45 >= 0]
    selectedStateVaccinated = selectedStateVaccinated[selectedStateVaccinated.PerDay45to60 >= 0]
    selectedStateVaccinated = selectedStateVaccinated[selectedStateVaccinated.PerDay60plus >= 0]
    
    selectedStateVaccinated.set_index("Date", inplace=True)
    #st.write(selectedStateVaccinated)
    return selectedStateVaccinated


st.markdown("""
    <style>
    .standard-text {
        font-size:16px;
    }
    .streamlit-expanderHeader{
        font-size:20px;
    }
    .stMarkdown {
        padding: 10px 10px 10px 10px;
        text-align: center !important;
    } 
    h2 {
        text-align:center !important;
    }
    .css-vfskoc {
        font-size: 1.2rem;
    }
    </style>        
            
            
""",unsafe_allow_html=True)




#<span style="background-color:blue;">
title = '<body bgcolor="red"><h1>Sahayog Bharat - An Online Covid Dashboard</h1></body>'
st.markdown(title, unsafe_allow_html=True)


'''Sahyog Bharat is a portal where citizens can find and visualize covid related information and gives  them a brief understanding of the covid trends in various domains .
As the name suggests, it helps the citizens gain an overview of current active cases , recovered cases,  and total deaths across the states in india.
'''

indiaCovidData = load_data()
statewiseCovidData = loadStatewiseCasesData(indiaCovidData)
statewiseVaccineData = loadStatewiseVaccineData(indiaCovidData)
images = loadImages()

st.image(images['weStayAtHome'], use_column_width='always')





ind_map=indiaCovidData
#st.write(ind_map)

st.header("Map of India")
indiaMap=plt_india_map()
map1,map2,map3 = st.beta_columns([5,1,5])
#with map1:
folium_static(indiaMap,width=1370)
    

chloropethMap = st.beta_expander("Expand to view a Chloropeth Map of India")


choice = ['Total cases','Active cases', 'Recoveries', 'Deaths']
choice_selected = chloropethMap.selectbox("Select Choice ", choice)
indiaChloroMap=chloropeth_map(choice_selected)
with chloropethMap:
    folium_static(indiaChloroMap,width=1370)

 
st.header("Covid-19 Symptoms")
col = st.beta_columns(7)
col[0].image(images['soreThroat'], caption='Sore Throat', use_column_width='always', output_format='png')
col[1].image(images['cough'], caption='Cough', use_column_width='always', output_format='png')
col[2].image(images['lossOfSmell'], caption='Loss of Taste & Smell', use_column_width='always', output_format='png')
col[3].image(images['chills'], caption='Shivering', use_column_width='always', output_format='png')
col[4].image(images['breath'], caption='Breathlessness', use_column_width='always', output_format='png')
col[5].image(images['fever'], caption='Fever', use_column_width='always', output_format='png')
col[6].image(images['muscle'], caption='Muscle Pain', use_column_width='always', output_format='png')


st.image(images['covidInstructions'], use_column_width='always',output_format='png')

#typeOfData = st.sidebar.selectbox("Select the type of Data", ["Covid 19 Cases","Covid 19 Vaccination"])

cumulativeStatewiseCases = loadCumulativeStatewiseCases()
cumulativeStatewiseVaccination = loadCumulativeStatewiseVaccination()


col1,col2 = st.beta_columns(2)
#if typeOfData == "Covid 19 Cases":
col1.write(alt.Chart(cumulativeStatewiseCases.reset_index(),title="Statewise Active Cases and Deaths").mark_bar().encode(
    x=alt.X('State', sort=None),
    y='Total',
    color = 'Status',
    tooltip = ['State','Status','Total']
).properties(
    #width = 500,
    height = 500        
).configure_header(
    titleAlign="center",
    titleFontSize=24,
    titleFontWeight='bold'
).configure_title(
    fontSize=24        
).interactive())
    


    
#else:
col2.write(alt.Chart(cumulativeStatewiseVaccination.reset_index(),title="Statewise Male and Female Vaccinated").mark_bar().encode(
    x=alt.X('State', sort=None),
    y='Vaccinated',
    color = 'Gender',
    tooltip = ['State', 'Gender','Vaccinated']
).properties(
    #width = 500,
    height = 500        
).configure_header(
    titleAlign="center",
    titleFontSize=24,
    titleFontWeight='bold'
).configure_title(
    fontSize=24        
).interactive())
    
selected_state=col1.selectbox("Select State", ind_map['State'],index=12)
select_graph=col2.multiselect("Select the Graph you want:",['Line','Area','Bar'])
   
selectedStateCases = loadSelectedStateCases(statewiseCovidData, selected_state)

#col1,col2 = st.beta_columns(2)
#selected_state=col1.selectbox("Select State", ind_map['State'],index=12)
#select_graph=col2.multiselect("Select the Graph you want:",['Line','Area','Bar'])
selectedStateVaccinated = loadSelectedStateVaccinated(statewiseVaccineData, selected_state)
perDayCases=st.beta_expander('Per Day Active cases, Recoveries and Deaths')
firstSecondDose=st.beta_expander('Per Day First and Second Doses')
maleFemale=st.beta_expander('Per Day Males and Females Vaccinated')
age=st.beta_expander("Age Group")
if 'Line' in select_graph:
    perDayCases.line_chart(selectedStateCases[['PerDayCured','PerDayDeath','PerDayConfirmed']])           
    firstSecondDose.line_chart(selectedStateVaccinated[["PerDayFirstDose","PerDaySecondDose"]])        
    maleFemale.line_chart(selectedStateVaccinated[["PerDayMale","PerDayFemale"]])
    age.line_chart(selectedStateVaccinated[["PerDay18to45","PerDay45to60","PerDay60plus"]])
if 'Area' in select_graph:
    #firstSecondDose=st.beta_expander('Per Day First and Second Doses')
    perDayCases.area_chart(selectedStateCases[['PerDayCured','PerDayDeath','PerDayConfirmed']])  
    firstSecondDose.area_chart(selectedStateVaccinated[["PerDayFirstDose","PerDaySecondDose"]])
    #maleFemale=st.beta_expander('Per Day Males and Females Vaccinated')
    maleFemale.area_chart(selectedStateVaccinated[["PerDayMale","PerDayFemale"]])
    age.area_chart(selectedStateVaccinated[["PerDay18to45","PerDay45to60","PerDay60plus"]])
if 'Bar' in select_graph:
    perDayCases.bar_chart(selectedStateCases[['PerDayCured','PerDayDeath','PerDayConfirmed']])  
    #firstSecondDose=st.beta_expander('Per Day First and Second Doses')
    firstSecondDose.bar_chart(selectedStateVaccinated[["PerDayFirstDose","PerDaySecondDose"]])
    #maleFemale=st.beta_expander('Per Day Males and Females Vaccinated')
    maleFemale.bar_chart(selectedStateVaccinated[["PerDayMale","PerDayFemale"]])
    age.bar_chart(selectedStateVaccinated[["PerDay18to45","PerDay45to60","PerDay60plus"]])

#st.write("Here")

#st.write(select_graph)

st.header("Myths & Facts")
col1,col3,col4,col5,col6 = st.beta_columns(5)

col1.image(images['myth1'], use_column_width='always', output_format='png')
#col2.image(images['myth2'], use_column_width='always', output_format='png')
col3.image(images['myth3'], use_column_width='always', output_format='png')
col4.image(images['myth4'], use_column_width='always', output_format='png')
col5.image(images['myth5'], use_column_width='always', output_format='png')
col6.image(images['myth6'], use_column_width='always', output_format='png')   


    





