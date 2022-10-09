import pandas as pd
import numpy as np

from .continuous_variables import clean_continuous_var
from .continuous_variables import cal_intervalos
from .continuous_variables import cal_descriptivos

from .discrete_variables import *


def pivot_table(df, column, values):
    df=df.copy()
    df=df.pivot(columns=column, values=values)
    return df

## Utilizamos la tabla resumen para crear la matriz de los valores posibles de la pregunta
def total_cat(df):
    
    i_start=(df.
             query('resp=="RESUMEN"').
             index.
             values[0]) #valor del index donde inicia la tabla resumen
    df_r=df.loc[i_start+3:]
    i_end=(df_r.
           query('resp=="TOTAL"').
           index.
           values[0]) #valor del index donde acaba la tabla resumen

    df_rf=df.loc[i_start+3:i_end-1].copy() ## tabla resumen
    return df_rf

## Crea una lista con los ubigeos de la dataframe 
def list_ubigeo_index(df):
    ubigeo=(df.query('resp.notna() and resp.str.startswith("AREA #")')
            ["resp"].
            copy()
           ) ## extrae los ubigeos de cada tabla
    list_index_d=ubigeo.index.values
    return ubigeo, list_index_d

## Función para extraer la información de las frecuencias de cada tabla de ubigeo
def extrac_freq_ubigeo(df,i_start_var):
    
    ubigeo, list_index=list_ubigeo_index(df)
    index_table=list_index[i_start_var]
    
    # ubigeo_nom=ubigeo.loc[index_table:index_table+1].str.split("")[1][7:]
    for p,q in ubigeo.loc[index_table:index_table+1].items():
        ubigeo_nom=q[7:]
    ##
    i_start_u=df.loc[index_table+3:]
    i_end_u=i_start_u.query('resp.notna() and resp=="TOTAL"')[i_start_u.columns[0]].index[0]-1
    df_f=df.loc[i_start_u.index.values[0]:i_end_u].copy()
    df_f["ubigeo"]=str(ubigeo_nom)
    
    return df_f

### create a multicolumn for the descriptive statistics
def multi_column_des(df, values=None):
    fila_1=values
    tup=[(fila_1,'numero de casos'), (fila_1,'suma'), (fila_1,'maximo'), (fila_1,'minimo'), (fila_1,'promedio'), (fila_1,'varianza'),
           (fila_1,'des estandar'), (fila_1,'coeficiente de variacion')]

    df.columns=pd.MultiIndex.from_tuples(tup)
    return df

def analys_cont_var(df, kind, valor_inicio,intervalo, column, values):
    df= df.copy()
    
    if kind =="intervalos":
        df_f=(cal_intervalos(df,valor_inicio,intervalo, column).
              pipe(pivot_table,column,values)
             )
        
    elif kind == "descriptivos":
        if len(values)>1: ## if columns are more than 1, if it's true, there are more than 1 variable
            list_des=[]
            for p in values:
                (
                    list_des.
                    append(cal_descriptivos(df, values=p, fila=column).
                           pipe(multi_column_des, values=p)
                          )
                )
            df_f=pd.concat(list_des,axis=1)
        else:
            df_f=cal_descriptivos(df)
    
    return df_f

def conversion_redatam_matriz(df, continuous=False, kind=None, valor_inicio=0, intervalo=None, fila_filtro=None):
    """
    conversion_redatam_matriz(df: 'DataFrame') -> Dataframe
    
    #Docstring:
    Permite de organizar los datos descargados de la plataforma de REDATAM - (INEI) en una formato de base datos de dos dimensiones.
    La base de datos de ingreso corresponde a un archivo en formato Excel, el cual se descarga luego de la busqueda de variables en REDATAM
    La base de datos resultante es un DataFrame con el ubigeo como índice

    """
    df=df.copy()
    df=df[[df.columns[1], df.columns[2]]].copy()
    df.columns=["resp", "fre"]
    df=clean_str(df, column='resp')
    
    df_rf=total_cat(df)                        ##categorías del resumen
    ubigeo,list_index_f=list_ubigeo_index(df)  ## Lista de ubigeos e indexes
    ubigeos_des=[]
    
    for p in list(range(0,len(list_index_f))): ## loop para extraer y los datos para cada ubigeo
        ubigeos_des.append(df.
                           pipe(extrac_freq_ubigeo,p)
                          )
    df_f=(pd.concat(ubigeos_des,axis=0))
    
    if continuous==True:
        list_var, df_f=clean_continuous_var(df_f, column='resp')
        df_f=(df_f.
              groupby("ubigeo").
              apply(analys_cont_var, kind, valor_inicio, intervalo, column='resp', values=list_var).
              fillna(0).
              reset_index(level=1, drop=True)
             )
    else:
        df_f=(index_filter_uni(df_f,fila_filtro).
              fillna(0)
             )
    return df_f

def tabla_cruzada(df, continuous=False, kind=None, valor_inicio=0, intervalo=None, fila_filtro=None, columna_filtro=None):
    """
    conversion_redatam_matriz(df: 'DataFrame') -> Dataframe
    
    #Docstring:
    Permite de organizar los datos descargados de la plataforma de REDATAM - (INEI) en una formato de base datos de dos dimensiones.
    La base de datos de ingreso corresponde a un archivo en formato Excel, el cual se descarga luego de la busqueda de variables en REDATAM
    La base de datos resultante es un DataFrame con el ubigeo como índice

    """
    df=df.iloc[:,1:].copy()
    ## se limpia la columna con las respuestas de las categorías "fila"
    df=(df.
        rename({df.columns[0]:"resp"},axis=1).
        pipe(clean_str, column='resp')
       )

    ubigeo, list_index_f=list_ubigeo_index(df)
    ubigeos_des=[]
    
    for p in list(range(0,len(list_index_f))): ## loop para extraer y los datos para cada ubigeo
        ubigeos_des.append(df.
                           pipe(extrac_freq_ubigeo,p).
                           pipe(clean_columns_answers)
                          )
    df_f=(pd.concat(ubigeos_des,axis=0))
    df_f=df_f.rename({df_f.columns[0]:"fila"},axis=1)
    
    if continuous==True:
        list_var, df_f=clean_continuous_var(df_f, column='fila')
        df_f=(df_f.
              groupby("ubigeo").
              apply(analys_cont_var, kind, valor_inicio, intervalo, column='fila', values=list_var).
              fillna(0).
              reset_index(level=1, drop=True)
             )
        
    else:
        df_f=(df_f.
              groupby("ubigeo").
              apply(multi_index).
              pipe(clean_data)
             )
#               pipe(index_filter, fila_filtro, columna_filtro)
#              )
    
    return df_f