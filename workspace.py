#%% Analysis
# -*- coding: utf-8 -*-
from MIT_reader import DataManager
from time import time
import pandas as pd
from numpy import nan
import plotly.express as px


db_path = pd.read_excel(r'Database/path.xlsx', index_col=0).loc['MIT_Parco_Circolante','Path']

sn = slice(None)
st = time()
data = DataManager(path=db_path, main_file=r'Database/Regioni_parco_circolante.xlsx')        
data.parse(years=2019, regions=['Lombardia'])
nd = time()
print(f'timing: {nd-st}')

ind = data.Data.columns
#%%
db = data.Data.loc[(sn,"A",'AUTOVETTURA PER TRASPORTO DI PERSONE',sn,sn,'2019')]
mkt_share = db['segment'].value_counts()/db['segment'].value_counts().sum()

dict = {0.0:"Utility",1.0:"Small",2.0:"Medium",3.0:"Cross-over",4.0:"Berlina/SUV",5.0:"Van"}
db.replace({"segment": dict}, inplace=True)
db.segment.fillna("I don't know", inplace=True)
db.index = [db.index.get_level_values(i).fillna('Unknown') for i in range(db.index.nlevels)]

# segmentation check by power train
mkt_seg = db.reset_index().set_index(['segment','power train']).groupby(level=[0,1]).sum().loc[:,'count'].unstack().fillna(0)
mkt_seg_per = mkt_seg / mkt_seg.sum(0).values *100
#

fig = px.scatter_3d(db.loc['Emilia Romagna'].reset_index(), x='kW', y='massa complessiva', z='cilindrata', 
                    color='segment', size_max=18, opacity=0.7)
fig.update_layout(template='plotly_white', font_family='Palatino Linotype',
                  title='Veicoli Emiliano Romagnoli vrruuuum')
fig.write_html('Plots\segmentation3d.html')
fig.show()

#%%
plt1 = db.reset_index().loc[:,['kW','massa complessiva','segment','power train','cilindrata']]
fig = px.scatter(plt1, x='kW', y='massa complessiva', 
                 color='segment', facet_col='power train')
fig.write_html('Plots\segmentation.html')
fig.show()


#%% Plotting footprints

# Manufacturing
fig = px.box(db.reset_index(), x="segment", y="Carbon Footprint - Lightweight Material", color="alimentazione")
fig.update_traces(quartilemethod="linear") # or "inclusive", or "linear" by default
fig.update_layout(template='plotly_white', font_family='Palatino Linotype',
                  title='GHG emissions necessary to produce the vehicle per segment and power train [M grCO2e = ton CO2eq]')
fig.write_html('Plots\GHG_manufacturing_ali.html')
# fig.show()

# Driving

db['Driving emissions'] = db.loc[:,'Well to Tank'].fillna(0) + db.loc[:,'Tank to Wheel'].fillna(0) 
fig = px.box(db.reset_index(), x="segment", y="Driving emissions", color="alimentazione", points='outliers')
fig.update_traces(quartilemethod="inclusive") # or "inclusive", or "linear" by default
fig.update_layout(template='plotly_white', font_family='Palatino Linotype',
                  title='GHG emissions necessary to drive 1 km with a vehicle of a specific segment and power train [grCO2e/km]')
fig.write_html('Plots\GHG_driving_ali.html')
# fig.show()



#%% Evaluating Median Greehouse Gases Pay-back Distance (GHG PBT)
GHGPBT_median = db.reset_index().set_index(['region','segment','power train']).groupby(level=[0,1,2]).median()

fig = px.scatter(GHGPBT_median.reset_index(), x='Carbon Footprint - Lightweight Material',
                 y='Driving emissions', color='power train', facet_row='region', 
                 facet_col='segment')
fig.update_layout(template='plotly_white', font_family='Palatino Linotype',
                  title='Driving vs footprint by region, segment and power train')
fig.write_html('Plots\Checks.html')




#%% OLD CODE
chart = data.Data.loc[(slice(None),slice(None),slice(None),slice(None),slice(None),"2019"),'count'].groupby(['power train','marca'], axis=0).sum().unstack().fillna(0)
chart_2 = data.Data.loc[(slice(None),"A",slice(None),"PROPRIO",slice(None),"2019"),('Well to Tank','Tank to Wheel','Carbon Footprint - Conventional Material')].dropna(subset=['Carbon Footprint - Conventional Material']).groupby(['region','power train']).mean().fillna(0)
chart_2L = data.Data.loc[(slice(None),"A",slice(None),"PROPRIO",slice(None),"2019"),('Well to Tank','Tank to Wheel','Carbon Footprint - Lightweight Material')].dropna(subset=['Carbon Footprint - Lightweight Material']).groupby(['region','power train']).mean().fillna(0)


chart_3 = chart_2 * [100000/1000,100000/1000,1/1000]
#%%
data.Data['segment'].value_counts() 

#%%
regions = list(set(chart_3.index.get_level_values(0)))
col = ['Saved emissions per km - EV vs ICEV [g/km]','km to emission parity [km] - Conventional','km to emission parity [km] - Lightweight']
chart_4 = pd.DataFrame(index=regions, columns=col)

for r in regions:
    chart_4.loc[r,'Saved emissions per km - EV vs ICEV [g/km]'] = chart_2.loc[(r,'ICEV'),'Well to Tank'] +chart_2.loc[(r,'ICEV'),'Tank to Wheel'] - (chart_2.loc[(r,'EV'),'Well to Tank'] +chart_2.loc[(r,'EV'),'Tank to Wheel'])
    chart_4.loc[r,'km to emission parity [km] - Conventional'] = (chart_2.loc[(r,'EV'),'Carbon Footprint - Conventional Material'] - chart_2.loc[(r,'ICEV'),'Carbon Footprint - Conventional Material']) / chart_4.loc[r,'Saved emissions per km - EV vs ICEV [g/km]']
    chart_4.loc[r,'km to emission parity [km] - Lightweight'] = (chart_2L.loc[(r,'EV'),'Carbon Footprint - Lightweight Material'] - chart_2L.loc[(r,'ICEV'),'Carbon Footprint - Lightweight Material']) / chart_4.loc[r,'Saved emissions per km - EV vs ICEV [g/km]']

#%% MEDIAN


ind = data.Data.columns

chart = data.Data.loc[(slice(None),slice(None),slice(None),slice(None),slice(None),"2019"),'count'].groupby(['power train','marca'], axis=0).sum().unstack().fillna(0)
chart_2 = data.Data.loc[(slice(None),"A",slice(None),"PROPRIO",slice(None),"2019"),('Well to Tank','Tank to Wheel','Carbon Footprint - Conventional Material')].dropna(subset=['Carbon Footprint - Conventional Material']).groupby(['region','power train']).median().fillna(0)
chart_2L = data.Data.loc[(slice(None),"A",slice(None),"PROPRIO",slice(None),"2019"),('Well to Tank','Tank to Wheel','Carbon Footprint - Lightweight Material')].dropna(subset=['Carbon Footprint - Lightweight Material']).groupby(['region','power train']).median().fillna(0)


chart_3 = chart_2 * [100000/1000,100000/1000,1/1000]
#%%
regions = list(set(chart_3.index.get_level_values(0)))
col = ['Saved emissions per km - EV vs ICEV [g/km]','km to emission parity [km] - Conventional','km to emission parity [km] - Lightweight']
chart_4 = pd.DataFrame(index=regions, columns=col)

for r in regions:
    chart_4.loc[r,'Saved emissions per km - EV vs ICEV [g/km]'] = chart_2.loc[(r,'ICEV'),'Well to Tank'] +chart_2.loc[(r,'ICEV'),'Tank to Wheel'] - (chart_2.loc[(r,'EV'),'Well to Tank'] +chart_2.loc[(r,'EV'),'Tank to Wheel'])
    chart_4.loc[r,'km to emission parity [km] - Conventional'] = (chart_2.loc[(r,'EV'),'Carbon Footprint - Conventional Material'] - chart_2.loc[(r,'ICEV'),'Carbon Footprint - Conventional Material']) / chart_4.loc[r,'Saved emissions per km - EV vs ICEV [g/km]']
    chart_4.loc[r,'km to emission parity [km] - Lightweight'] = (chart_2L.loc[(r,'EV'),'Carbon Footprint - Lightweight Material'] - chart_2L.loc[(r,'ICEV'),'Carbon Footprint - Lightweight Material']) / chart_4.loc[r,'Saved emissions per km - EV vs ICEV [g/km]']


