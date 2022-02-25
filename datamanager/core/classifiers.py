"""
A python module for clustering vehicles based on different algorithms
"""

import pandas as pd
import numpy as np

from datamanager.tools.tools import (
    _CLASSIFICATION_METHODS,
    define_parser
)
from datamanager.tools import algos

class Classifier:

    def __init__(
        self,
        method,
        segments,
        segment_properties,
    ):

        self.method = method
        self.data = {}
        self.segments = segments

        self._classifier_check(segment_properties.keys())
        self.segment_properties = segment_properties
        self._classified = []


    def parser(
        self,
        mapper,
        io,
        node,
        index_col = None,
        header = 0,
        sheet_name = 0,
        sep = ',',
        filter = None,
        over_write = False,
        names = None,
    ):
        if node in self.nodes and not over_write:
            raise Exception(f"{node} already exists. To over write the node data use over_write = True.")

        self._classifier_check(mapper.values())

        kwargs = dict(
            index_col = index_col,
            header = header,
        )
        if isinstance(io,pd.DataFrame):
            data = io
        else:
            parser,extra_kwargs = define_parser(io)

            for kk in extra_kwargs:
                kwargs[kk] = eval(kk)
                data = parser(io,**kwargs)

        if filter is not None:
            data = filter(data)

        self.data[node] = data.rename(columns=mapper,errors='raise').loc[:,list(mapper.values())]

        
    def classify(self,node):

        
        if node in self._classified:
            raise ValueError(f"{node} is already classified.")

        function = getattr(algos,self.method)
        outputs = []
        

        for row in self.data[node].itertuples():
            kwargs = {kk:getattr(row,kk) for kk in self.sets}
            outputs.append(function(self,**kwargs)['segment'])
                
            
        


        self.data[node]["segment"] = outputs
        self._classified.append(node)

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self,method):
        if method not in _CLASSIFICATION_METHODS:
            raise ValueError(f"Acceptable method are : {[_CLASSIFICATION_METHODS]}")
        self._method = method

    @property
    def nodes(self):
        return [*self.data]

    @property
    def sets(self):
        return _CLASSIFICATION_METHODS[self.method]
    
    @property
    def segment_ids(self):
        return list(range(len(self.segments)))

    def _classifier_check(self,data):
        
        mapper_need  = _CLASSIFICATION_METHODS[self.method]
        mapper_given = data
        differences  = set(mapper_need).difference(set(mapper_given))
        
        if differences:
            raise ValueError(f"{differences} are missed for the mappers.")





    
    
    
