#%% Analysis
# -*- coding: utf-8 -*-
from MIT_reader import DataManager
from time import time
import pandas as pd

db_path = pd.read_excel(r'Database\path.xlsx', index_col=0).loc['MIT_Parco_Circolante','Path']

#%%
st = time()
data = DataManager(path=db_path, main_file=r'Database\Regioni_parco_circolante.xlsx')        
d = data.parse(years=2019, regions=['Abruzzo'])
nd = time()
print(f'timing: {nd-st}')

ind = data.Data.columns

chart = data.Data.loc[(slice(None),slice(None),slice(None),slice(None),slice(None),"2019"),'count'].groupby(['power train','marca'], axis=0).sum().unstack().fillna(0)
chart_2 = data.Data.loc[(slice(None),"A",slice(None),"PROPRIO",slice(None),"2019"),('Well to Tank','Tank to Wheel','Carbon Footprint - Conventional Material')].dropna(subset=['Carbon Footprint - Conventional Material']).groupby(['region','power train']).mean().fillna(0)
chart_2L = data.Data.loc[(slice(None),"A",slice(None),"PROPRIO",slice(None),"2019"),('Well to Tank','Tank to Wheel','Carbon Footprint - Lightweight Material')].dropna(subset=['Carbon Footprint - Lightweight Material']).groupby(['region','power train']).mean().fillna(0)


chart_3 = chart_2 * [100000/1000,100000/1000,1/1000]
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


