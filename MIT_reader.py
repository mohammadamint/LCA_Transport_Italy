# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 15:08:11 2021

@author: Amin-Nicolo
"""

import pandas as pd
import numpy as np
import zipfile
from copy import deepcopy as dc
from time import time
from datamanager.core.classifiers import Classifier

def Cleaning_PC(PC):
    '''
    Function to clean the regional parco circolante files
    Operating with PC files only
    '''
    #DATA FILTERING
    #Deleteing motorcycles
    PC = PC.loc[PC["tipo_veicolo"]=='A']
    #Deleting unwanted usage destination
    # wanted = ['AUTOVEICOLO USO ESCLUSIVO DI POLIZIA','AUTOVETTURA PER TRASPORTO DI PERSONE','TRAS.SPECIFICO PERSONE PART.CONDIZIONI','AUTOVEIC. TRASP. PROMISCUO PERSONE/COSE']
    wanted = ['AUTOVETTURA PER TRASPORTO DI PERSONE',]
    # cond = (PC["destinazione"] == wanted[0]) | (PC["destinazione"] == wanted[1]) | (PC["destinazione"] == wanted[2]) | (PC["destinazione"] == wanted[3])
    cond = (PC["destinazione"] == wanted[0])
    PC = PC.loc[cond]
    #Deleting unwanted columns
    unwanted_col=['tipo_veicolo', 'destinazione', 'uso', 'residenza', 'marca', 'alimentazione', 'data_immatricolazione', 'classe_euro', 'emissioni_co2']
    PC = PC.drop(unwanted_col,axis=1)
    #DATA CLEANING
    #Eliminating vehicles with wheight>4000 and weight>0
    PC = PC.loc[(PC["massa_complessiva"]>500) & (PC["massa_complessiva"]<4000)]
    #Eliminating vehicles with cilindrata > 5000 and nan as value
    PC = PC.loc[(PC["cilindrata"]>0) & (PC["cilindrata"]<5000)]
    #Eliminating vehicles with power nan as value
    PC = PC.loc[(PC['kw']>0)]

    #PC = PC.reset_index(drop=True)
    return PC


class DataManager:
    
    def __init__(self,path,main_file):
        
        self.path = path
        self.main_file = main_file
        
        
        sheets = {'Reading'                 : {'name':'reg_table'     ,'header':[0], 'index_col':[0]},
                  'from_ali_to_type'        : {'name':'vehicle_type'  ,'header':[0], 'index_col':[0]},
                  'Conventional WTT'        : {'name':'wtt_con'       ,'header':[0], 'index_col':[0]},
                  'EV WTT  kWh_km'          : {'name':'wtt_ev'        ,'header':[0], 'index_col':[0,1]},
                  'EV WTT Fattore_emissione': {'name':'e_fact_em'     ,'header':[0], 'index_col':[0]},
                  'ICEV_embedded_co2'       : {'name':'icev_f_co2'    ,'header':[0], 'index_col':[0]},
                  'HEV_embedded_co2'        : {'name':'hev_f_co2'     ,'header':[0], 'index_col':[0]},
                  'EV_embedded_co2'         : {'name':'ev_f_co2'      ,'header':[0], 'index_col':[0]},
                  'FCV_embedded_co2'        : {'name':'fcv_f_co2'     ,'header':[0], 'index_col':[0]},
                #   'PHEV_embedded_co2'       : {'name':'phev_f_co2'   ,'header':[0], 'index_col':[0]},
                  
                  }
        
        for sheet,items in sheets.items():
            to_read = pd.read_excel(main_file,sheet,index_col=items['index_col'],header=items['header'])
            setattr(self, items['name'], to_read)
            
            
            
        self.columns = ['index',
                       'tipo',
                       'destinazione',
                       'Uso',
                       'provincia',
                       'marca',
                       'cilindrata',
                       'alimentazione',
                       'kW',
                       'data',
                       'classe auto',
                       'Tank to Wheel',
                       'massa complessiva',
                       ]
    
    def parse(self,
              years   = None,
              regions = None,
              index   = ['region','tipo','destinazione','Uso','data','year','provincia','marca','alimentazione','power train'],
              materials= ['Conventional Material','Lightweight Material']
              ):
        
        if regions is None:
            regions = list(self.reg_table.columns)
            
        for count,region in enumerate(regions):
            with zipfile.ZipFile(self.path + self.reg_table.loc['zip',region]) as zip:
                with zip.open(self.reg_table.loc['csv',region]) as myZip:
                    df = pd.read_csv(myZip)

                    start = time()
                    dataset = Classifier(
                        method='dis_pow_weight',
                        segments = ['Utility','Small','Medium','Cross-over','Berlina/SUV','Van'],
                        segment_properties=dict(
                            displacement = np.array([1000,1200,1500,2000,3000,2000]),
                            power = np.array([51,74,110,131,250,110]),
                            weight = np.array([1400,1900,2000,2200,2600,3200]),
                            )
                        )

                    dataset.parser(
                        io = df,
                        mapper = {
                            "cilindrata":"displacement",
                            "kw": "power",
                            "massa_complessiva": "weight"
                            },
                        node = region,
                        names = ['tipo_veicolo', 'destinazione', 'uso', 'residenza', 'marca', 'cilindrata', 'alimentazione', 'kw', 'data_immatricolazione', 'classe_euro', 'emissioni_co2', 'massa_complessiva'],
                        filter = Cleaning_PC
                    )
                    dataset.classify(node = region)
                    end = time()

                    print("Leggendo il database della regione {}, avente {} colonne.".format(region,len(df.columns)))
                    
                    if len(df.columns) != 13:
                        df.insert(0, "index", "") 
                        
                        
                    df.columns = self.columns
                    
                    df['count']  = 1
                    df['region'] = region
                    df['data']   = pd.to_datetime(df.data)
                    df['year']   = [str(x.year) for x in df['data']]
                    df['segment'] = dataset.data[region].segment.values
                    
                    # Take the caegories in the column alimentazione (the missing information will be Unknown) and fill it 
                    # with the values from vehicle_type
                    df['power train'] = self.vehicle_type.loc[df['alimentazione'].fillna('Unknown')].values
                    
                    
                    df['WTT conventional'] = self.wtt_con.loc[df['alimentazione'].fillna('Unknown')].values
                    
                    df.set_index(['marca'], inplace=True)
                    
                    self.__filter(df[df['power train'] == 'EV'].index)
                    
                    df = df.reset_index()
                    df.set_index(['marca','power train'], inplace=True) 
                    

                    for item in self.found:
                        df.loc[(item,'EV'),'WTT electric'] = self.wtt_ev.loc[item].values[0][0]
                        df.loc[(item,'EV'),'WTT conventional'] = self.wtt_ev.loc[item].values[0][0] * self.e_fact_em.loc[region,'fattore']
                        
                   
                    
                    types = ['ev','icev','hev','fcv']
                    
                    df = df.reset_index()
                    df.set_index(['marca'], inplace=True)

                    existing = {}
                    for _type in types:
                        for material in materials: 
                            existing[_type] = set(df.loc[df['power train']==_type.upper()].index)
                    
                    df = df.reset_index()
                    df.set_index(['marca','power train'], inplace=True) 
                    
                    self.check = df
                    for _type in types:
                        for material in materials:
                            db = getattr(self,f'{_type}_f_co2')
                            
                            
                            for i in existing[_type]:
                                try:
                                    df.loc[(i,_type.upper()),
                                       f'Specific Carbon Footprint - {material}'] = db.loc[i,material]
                                except KeyError as e:
                                    missing = e.args
                                    print(f'{missing}-{_type} is missing in {region}')
                                
                    
                    df = df.reset_index()
                    df.set_index(index, inplace=True)
                        
                    if count:
                        self.Data = pd.concat([self.Data,df])
                    else:
                        self.Data = df
                        
        self.__calc_abs_footprint(materials)

        self.Data['Well to Tank'] = self.Data['WTT electric'].fillna(0) + self.Data['WTT conventional'].fillna(0) 
        
    def __calc_abs_footprint(self,materials):
        
        for material in materials:
            
            self.Data[f'Carbon Footprint - {material}'] = self.Data['massa complessiva'] * self.Data[f'Specific Carbon Footprint - {material}']
            
    def __filter(self,index):
        
        real_names = list(self.wtt_ev.index.get_level_values(0))
        new_names  = list(index)

        self.found     = []
        self.not_found = []
        
        for item in set(new_names):
            if item in real_names:
                self.found.append(item)
            else:
                self.not_found.append(item)
                
    def save(self,path,_format):
        formats = ['csv','feather','parquet','html']
        if _format not in formats:
            raise ValueError(f'acceptable formats are {formats}')
        
        eval('self.Data.to_{}(path)'.format(_format))
                    
