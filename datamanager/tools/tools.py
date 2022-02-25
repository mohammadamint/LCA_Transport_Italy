
import pandas as pd

_CLASSIFICATION_METHODS = {
    "dis_pow_weight" : ["displacement","power","weight"],
    "pow_weight" : ["power","weight"]
}


def define_parser(file):

    extension = file.split(".")[-1]

    if extension in ("txt","csv"):
        return pd.read_csv,['sep',"names"]

    elif extension in ("xlsx"):
        return pd.read_excel,["sheet_name"]
