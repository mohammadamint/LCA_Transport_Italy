#%%
from MIT_reader import DataManager
from time import time
import pandas as pd
from numpy import nan
import plotly.express as px


sn = slice(None)
st = time()


def loop(region):
    print('I start with {}'.format(region))
    db_path = pd.read_excel(r'Database/path.xlsx', index_col=0).loc['MIT_Parco_Circolante','Path']
    data = DataManager(path=db_path, main_file=r'Database/Regioni_parco_circolante.xlsx')        
    data.parse(years=2019, regions=[region])
    
    db = data.Data.loc[(sn,"A",'AUTOVETTURA PER TRASPORTO DI PERSONE',sn,sn,'2019')]
    db.index = [
        db.index.get_level_values(i).fillna('Unknown') for i in range(db.index.nlevels)
    ]

    plt1 = db.reset_index().loc[:,['kW','massa complessiva','segment','power train','cilindrata']]
    fig = px.scatter(plt1, x='kW', y='massa complessiva', 
                     color='segment', facet_col='power train')
    fig.update_layout(template='plotly_white', font_family='Palatino Linotype',
                      title='Veicoli della regione {}'.format(region))
    fig.write_html('Plots\segmentation_{}.html'.format(region))

    print('Tutto liscio con {}'.format(region))

#%%
all_reg = list(pd.read_excel('Database\Regioni_parco_circolante.xlsx', index_col=[0]).columns)
reg = all_reg

reg = ['Piemonte']

list(map(loop,reg))
# %%
