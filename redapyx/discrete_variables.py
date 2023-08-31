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


def cleaning_manzana(df_mz):
    df=df_mz.copy()
    dic_lim={'00':'','01':'A','02':'B','03':'C','04':'D','05':'E','06':'F','07':'G','08':'H','09':'I',
             '10':'J','11':'K','12':'L','13':'M','14':'N','15':'Ñ','16':'O','17':'P','18':'Q','19':'R',
             '20':'S','21':'T','22':'U','23':'V','24':'W','25':'X','26':'Y','27':'Z'}

    ## limpiamos los último dos dígitos del ubigeo
    df["mz_c"]=df.ubigeo.str[18:20]
    df['mz_c']=df['mz_c'].replace(dic_lim, regex=True)
    df["ubigeo"]=df.ubigeo.str[0:18]+df.mz_c
    del df['mz_c']
    
    
    return df