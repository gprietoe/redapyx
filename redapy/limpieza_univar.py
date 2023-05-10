import pandas as pd
import numpy as np

from .continuous_variables import clean_continuous_var
from .continuous_variables import cal_intervalos
from .continuous_variables import cal_descriptivos
from .continuous_variables import multi_column_des

from .discrete_variables import *


def pivot_table(df, column, values):
    df=df.copy()
    df=df.pivot(columns=column, values=values)
    return df

def list_ubigeo_index(df):
    '''
    Returns two list, one with the INEI's unique code (ubigeo) and the second one with each ubigeo's index position
    '''
    ubigeo=(df.query('resp.notna() and resp.str.startswith("AREA #")', engine='python')
            ["resp"].
            copy()
           ) ## extrae los ubigeos de cada tabla
    list_index_d=ubigeo.index.values
    return ubigeo, list_index_d


def extrac_freq_ubigeo(df,i_start_var):
    '''
    Returns a dataframe with the data frecuencies from each ubigeo (distrito, provincia or departamento)
    '''
    ubigeo, list_index=list_ubigeo_index(df)
    index_table=list_index[i_start_var]
    
    ubigeo_nom = ubigeo.loc[index_table][7:]
    
    ##
    i_start_u=df.loc[index_table+3:].copy()
    i_start_u["resp"]=i_start_u["resp"].str.strip()
    i_end_u=i_start_u.query('resp.notna() and resp=="Total"', engine='python')[i_start_u.columns[0]].index[0]-1
    df_f=df.loc[i_start_u.index.values[0]:i_end_u].copy()
    df_f["ubigeo"]=str(ubigeo_nom)
    
    return df_f


def analys_cont_var(df, kind, start,interval, pivot, column, values):
    '''
    Returns a dataframe with the result of the quantitative value
    '''
    df= df.copy()
    
    if kind =="intervalos":
        if pivot==True:
            df_f=(cal_intervalos(df,start,interval, column).
                  pipe(pivot_table,column ,values)
                 )
        else:
            df_f=(cal_intervalos(df,start,interval, column).
                  iloc[:,1:].
                  copy()
                 )
        
    elif kind == "descriptivos":
        if len(values)>1: ## if columns are more than 1, if it's true, there are more than 1 variable
            list_des=[cal_descriptivos(df, values=p, fila=column).pipe(multi_column_des, values=p) for p in values]
            df_f=pd.concat(list_des,axis=1)
        else:
            df_f=cal_descriptivos(df)
    
    return df_f

def frequency(df, pivot=False, continuous=False, kind=None, start=0, interval=None):
    """
    #Docstring:
    Permite de organizar los datos descargados de la plataforma de REDATAM - (INEI) en una formato de base datos de dos dimensiones.
    La base de datos de ingreso (df) corresponde a la información descargada, la cual se obtiene luego de la búsqueda en REDATAM

  Parameters
    ----------
    df: str, path object or dataframe.
        If you downloaded the data from the INEI web page using REDATAM platform, you should open it using pandas first. On the other hand, if you were using redapy.query, you should pass the dataframe directly.
    pivot: bool, default False
        It allows you retrive the final data with the ubigeo as Index 
    continuous: bool, default False
        If True, the variable knows as "fila" is continuous
    kind: bool, default None
        
        *if Intervalos, compute the frecuency table for the continuous variable
        *if Descriptivos, compute the descriptive statistics for the continuous variable
    
    start: int, default 0
        Number that works as the fisrt position for calculating the interval 
    interval: int, default None.
        Number for the interval of each group
        
    """
    df=df.copy()
    df=df[[df.columns[1], df.columns[2]]]
    df.columns=["resp", "fre"]
    
    ubigeo, list_index_f = list_ubigeo_index(df)  ## Lista de ubigeos e indexes
    
    ubigeos_des = [df.pipe(extrac_freq_ubigeo, p) for p in list(range(len(list_index_f)))]
    df_f=pd.concat(cleaning_list_ubigeos_des(ubigeos_des, frequency=True),axis=0)
    
              
    if continuous==True:
        list_var, df_f=clean_continuous_var(df_f, column='resp')
        df_f=(df_f.
              groupby("ubigeo").
              apply(analys_cont_var, kind, start, interval, pivot, column='resp', values=list_var).
              fillna(0).
              reset_index(level=1, drop=True)
             )

    else:
        try:
            df_f["fre"]=df_f.fre.replace(" ","", regex=True).astype(int)
            
            if pivot==True:
                df_f=(df_f.pivot(index="ubigeo",columns="resp", values="fre").
                      fillna(0).
                      astype(int)
                     )
            else:
                return df_f
        except:
            print("Existe en el resultado tablas vacias en alguno de los UBIGEOS")
            
            if pivot==True:
                df_f=(df_f.pivot(index="ubigeo",columns="resp", values="fre").
                      fillna(0).
                      astype(int)
                     )
            else:
                return df_f
            return df_f
    
    return df_f

def cross_table(df, filter_var=False, pivot=False, continuous=False, kind=None, start=0, interval=None):
    """
    #Docstring:
    Permite de organizar los datos descargados de la plataforma de REDATAM - (INEI) en una formato de base datos de dos dimensiones.
    La base de datos de ingreso corresponde a la data descargada, la cual se optiene luego de la busqueda de variables en REDATAM
    La base de datos resultante es un DataFrame con el Ubigeo como indice principal

  Parameters
    ----------
    df: str, path object or dataframe.
        If you downloaded the data from the INEI web page using REDATAM platform, you should open it using pandas first. On the other hand, if you were using redapy.query, you should pass the dataframe directly.
    pivot: bool, default False
        It allows you retrive the final data with the ubigeo as Index 
    continuous: bool, default False
        If True, the variable knows as "fila" is continuous
    kind: bool, default None
        
        *if Intervalos, compute the frecuency table for the continuous variable
        *if Descriptivos, compute the descriptive statistics for the continuous variable
    
    start: int, default 0
        Number that works as the fisrt position for calculating the interval 
    interval: int, default None.
        Number for the interval of each group
        
    """
    df=df.iloc[:,1:].copy()
    ## se limpia la columna con las respuestas de las categorías "fila"
    df=(df.
        rename({df.columns[0]:"resp"},axis=1)
       )

    ubigeo, list_index_f=list_ubigeo_index(df)
    
    if filter_var==False:
        ubigeos_des = [df.pipe(extrac_freq_ubigeo, p).
                       pipe(clean_columns_answers,filter_var) for p in list(range(len(list_index_f)))]
        
        try:
            df_f=pd.concat(ubigeos_des,axis=0)
        except:            
            df_f=pd.concat(cleaning_list_ubigeos_des(ubigeos_des),axis=0)        
    
    else:
        ubigeos_des = [(df.pipe(extrac_freq_ubigeo, p).
                       assign(resp=lambda df_:df_.resp.fillna(method='ffill')).
                       groupby(['ubigeo','resp']).
                       apply(clean_columns_answers,filter_var)) for p in list(range(len(list_index_f)))]
        try:
            df_f=pd.concat(ubigeos_des,axis=0)
        except:
            df_f=pd.concat(cleaning_list_ubigeos_des(ubigeos_des),axis=0)

    if continuous==True:
        list_var, df_f=clean_continuous_var(df_f, column='fila')
        df_f=(df_f.
              groupby("ubigeo").
              apply(analys_cont_var, kind, start, interval, pivot, column='fila', values=list_var).
              fillna(0).
              reset_index(level=1, drop=True)
             )
        
    else:
        if filter_var==False:
            df_f=(df_f.
                      groupby("ubigeo").
                      apply(multi_index)
                     )
            df_f.index=(df_f.
                        index.
                        set_names(["ubigeo","fila","columna"])
                       )
            df_f=(df_f.reset_index().
                  query('columna!="ubigeo"', engine='python').
                  set_index(["ubigeo","fila","columna"])
                 )
            df_f["freq"]=(df_f.replace("-","0",regex=True).
                          replace(r'(?<=\d)\s+(?=\d)', '', regex=True).
                          astype(int))

            if pivot==True:
                df_f=(df_f.
                      reset_index().
                      pivot(index=["ubigeo"],columns=["fila","columna"], values="freq").
                      fillna(0)
                     )
            else:
                df_f
        else:
            df_f=(multi_index(df_f).
                 assign(freq=lambda df_:df_.freq.replace("-","0",regex=True).
                        replace(r'(?<=\d)\s+(?=\d)', '', regex=True)).
                  astype(int)
                 )
            df_f.index=(df_f.
                        index.
                        set_names(["ubigeo","filtro","fila","columna"])
                       )
             
            if pivot==True:
                df_f=(df_f.
                      reset_index().
                      pivot(index=["ubigeo"],columns=["filtro","fila","columna"], values="freq").
                      fillna(0)
                     )
            else:
                df_f
    return df_f