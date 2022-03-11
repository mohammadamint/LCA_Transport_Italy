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
data.parse(years=2019)
nd = time()
print(f'timing: {nd-st}')

ind = data.Data.columns
#%%
database = data.Data.loc[(sn,"A",'AUTOVETTURA PER TRASPORTO DI PERSONE',sn,sn,'2019')]
mkt_share = database['segment'].value_counts()/database['segment'].value_counts().sum()

dict = {0.0:"Utility",1.0:"Small",2.0:"Medium",3.0:"Large",4.0:"SUV",5.0:"Other"}
database.replace({"segment": dict}, inplace=True)
database.segment.fillna("I don't know", inplace=True)
database.index = [database.index.get_level_values(i).fillna('Unknown') for i in range(database.index.nlevels)]


#%% Data cleaning

power_trains = ['EV','ICEV']
segments = ['Utility','Small','Medium','Large','SUV']

db = database.loc[(database.loc[:,'kW']<=600) & 
                  (database.loc[:,'massa complessiva']<=5000) &
                  (database.loc[:,'segment'].isin(segments))]

db = db.loc[(sn,sn,sn,sn,sn,sn,power_trains)]
# segmentation check by power train
mkt_seg = db.reset_index().set_index(['segment','power train']).groupby(level=[0,1]).sum().loc[:,'count'].unstack().fillna(0)
mkt_seg_per = mkt_seg / mkt_seg.sum(0).values *100


#%%
plt1 = db.reset_index().loc[:,['kW','massa complessiva','segment','power train','cilindrata']]
fig = px.scatter(plt1, x='kW', y='massa complessiva', 
                 color='segment', facet_col='power train')
fig.write_html('Plots\segmentation.html')
fig.show()

#%% Plotting footprints

# Manufacturing
fig = px.box(db.reset_index(), x="segment", y="Carbon Footprint - Lightweight Material", color="power train")
fig.update_traces(quartilemethod="linear") # or "inclusive", or "linear" by default
fig.update_layout(template='plotly_white', font_family='Palatino Linotype',
                  title='GHG emissions necessary to produce the vehicle per segment and power train [M grCO2e = ton CO2eq]')
fig.write_html('Plots\GHG_manufacturing.html')
fig.show()

#%% Driving

db['Driving emissions'] = db.loc[:,'Well to Tank'].fillna(0) + db.loc[:,'Tank to Wheel'].fillna(0) 
fig = px.box(db.reset_index(), x="segment", y="Driving emissions", color="power train", points='outliers')
fig.update_traces(quartilemethod="inclusive") # or "inclusive", or "linear" by default
fig.update_layout(template='plotly_white', font_family='Palatino Linotype',
                  title='GHG emissions necessary to drive 1 km with a vehicle of a specific segment and power train [grCO2e/km]')
fig.write_html('Plots\GHG_driving.html')
fig.show()

#%% Building charts
qnt = [.25,.75]

db_ps = db.reset_index().set_index(['segment','power train'])
info = ['Manufacturing emissions [kgCO2]','Driving emissions [kgCO2/km]']
levels = ['Low','Medium','High']

db_lc = pd.DataFrame(0, index=pd.MultiIndex.from_product([power_trains,segments,levels], names=['Power train','Segment','Estimate']), columns=info)
for i in power_trains:
    for j in segments:
        db_lc.loc[(i,j,'Low'),'Manufacturing emissions [kgCO2]'] = db_ps.loc[(j,i)].describe(qnt).loc['{}%'.format(round(100*qnt[0])),'Carbon Footprint - Lightweight Material']/1000
        db_lc.loc[(i,j,'Medium'),'Manufacturing emissions [kgCO2]'] = db_ps.loc[(j,i)].describe(qnt).loc['50%','Carbon Footprint - Lightweight Material']/1000
        db_lc.loc[(i,j,'High'),'Manufacturing emissions [kgCO2]'] = db_ps.loc[(j,i)].describe(qnt).loc['{}%'.format(round(100*qnt[1])),'Carbon Footprint - Lightweight Material']/1000
        db_lc.loc[(i,j,'Low'),'Driving emissions [kgCO2/km]'] = db_ps.loc[(j,i)].describe(qnt).loc['{}%'.format(round(100*qnt[0])),'Driving emissions']/1000
        db_lc.loc[(i,j,'Medium'),'Driving emissions [kgCO2/km]'] = db_ps.loc[(j,i)].describe(qnt).loc['50%','Driving emissions']/1000
        db_lc.loc[(i,j,'High'),'Driving emissions [kgCO2/km]'] = db_ps.loc[(j,i)].describe(qnt).loc['{}%'.format(round(100*qnt[1])),'Driving emissions']/1000


#%% prova 0
distance = list(range(1000,75000,1000))

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

fil_map = {'Low':None, 'High':'tonexty'}
col_map = {'EV':'#59C9A5', 'ICEV':'#5B6C5D'}
colM_map = {'EV':'#56E39F', 'ICEV':'#2E382F'}
leg_map = {'Utility':True,'Small':False,'Medium':False,'Large':False,'SUV':False}

fig = make_subplots(rows=1, cols=len(segments), subplot_titles=segments, shared_yaxes='all')
for seg in segments:
    for pt in power_trains:
        for est in ['Low','High']:
            fig.add_trace(go.Scatter(x=distance, y=np.array(distance)*db_lc.loc[(pt,seg,est),'Driving emissions [kgCO2/km]'] + db_lc.loc[(pt,seg,est),'Manufacturing emissions [kgCO2]'], 
                        fill=fil_map[est], name='{} - {}'.format(pt,est),
                        line=dict(color=col_map[pt]), showlegend=leg_map[seg], legendgroup=pt,
                        ), row=1, col=segments.index(seg)+1)
        fig.add_trace(go.Scatter(x=distance, y=np.array(distance)*db_lc.loc[(pt,seg,'Medium'),'Driving emissions [kgCO2/km]'] + db_lc.loc[(pt,seg,'Medium'),'Manufacturing emissions [kgCO2]'],
                                line=dict(color=colM_map[pt], dash='dash'), showlegend=leg_map[seg], 
                                name='{} - {}'.format(pt,'Median'), legendgroup=pt,
                                ), row=1, col=segments.index(seg)+1) # fill down to xaxis
fig.update_layout(template='plotly_white', font_family='Palatino Linotype', hovermode='x',
                  title='How many km do I have to drive to off-set EVs additional manufacturing emission?',
                  annotations=[go.layout.Annotation(
                        showarrow=False,
                        text='Low and high estimate considers the top and bottom 15% of the distribution of 1.6 M vehicles. Assumed emission factor for electricity is 300 grCO2/kWh',
                        xanchor='left',
                        x=0, y=-0.05,
                        yanchor='top',
                        font_size = 10,
                        font_family='Palatino Linotype')],
                  yaxis=dict(title='Manufacturing (in x=0) and driving LCA GHG emissions [kgCO2eq]'))
fig.write_html('Plots/GHGPBD.html')

fig.show()

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


