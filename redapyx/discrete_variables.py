import pandas as pd
import numpy as np

### BOTH


### MULTIVARIABLE

def clean_columns_answers(df, filter_var):
    df=df.copy()
    cols=df.iloc[0:1,0:].values.flatten().tolist()
    cols[-1:]=["ubigeo"]
    
    if filter_var==False:
        cols[:1]=["fila"]
        df.columns=cols
        df=df.iloc[1:].copy() ## posible BUG
        df=df.set_index("fila")
        
    else:
        cols[:1]=["filtro"]
        cols[1:2]=["fila"]
        df.columns=cols
        df=df.iloc[1:-1,1:-1].copy()
        df=df.set_index("fila")        
    
    return df

def multi_index(df):
    df=df.copy()
    df=(pd.DataFrame(df.
                    stack()).
        rename({0:"freq"},axis=1))
    return df

def clean_data(df):
    df=df.copy()    
    df.index=(df.
              index.
              set_names(["ubigeo","fila","columna"])
             )
    df=(df.
        reset_index("columna").
        rename(index=str.strip).
        query('columna != "ubigeo"', engine='python').
        rename({0:'freq'},axis=1))
    try:
        df=(df.assign(freq=lambda df_:df_.freq.str.replace(" ","")).
        replace("-","0",regex=True).
        assign(freq=lambda df_:df_.freq.astype(int))
       )
    except:
        df=(df.replace("-","0",regex=True).
        assign(freq=lambda df_:df_.freq.astype(int))
       )
        
    return df.set_index([df.index,"columna"])


def cleaning_list_ubigeos_des(list_ubi, frequency=False):
    '''
    Returns a new list without the tables(df) that do not has any information
    '''
    if frequency==True:
        list_index_to_remove = [i for i, df in enumerate(list_ubi) if pd.isna(df.set_index('resp').index[0])]
    else:
        list_index_to_remove = [i for i, df in enumerate(list_ubi) if pd.isna(df.index[0])]
    
    list_ubi2 = [df for i, df in enumerate(list_ubi) if i not in list_index_to_remove]  
    
    return list_ubi2