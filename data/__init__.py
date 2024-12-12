from .real_estate import clean_real_estate
from .unemployment import clean_unemployment

import pandas as pd

def get_real_estate_df():
    return clean_real_estate.clean('./data/real_estate/Real Estate.csv')

def get_unemployment_df(real_estate_df: pd.DataFrame):
    return clean_unemployment.clean(real_estate_df['Town'].unique())