import pandas as pd
import numpy as np

from .continuous_variables import clean_continuous_var
from .continuous_variables import cal_intervalos
from .continuous_variables import cal_descriptivos

### Función para limpiar los caracteres especiales
def clean_str(df):
    df=df.copy()
    dic_replace={"Á":"A","É":"E","Í":"I","Ó":"O","Ú":"U","-":"","\/":""}
    df=(
        df.
        assign(resp=lambda df_:df_.resp.
               str.upper().
               str.strip().
               replace(dic_replace, regex=True)
              )
    )
    return df

### indetificar el index
def pivot_table(df):
    df=df.pivot(index="ubigeo",columns="resp", values="fre")
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
    ubigeo=(df.query('resp.notna() and resp.str.startswith("AREA")')
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

def analys_cont_var(df, kind,valor_inicio,intervalo):
    df= df.copy()
    df=clean_continuous_var(df)
    
    if kind =="intervalos":
        df=cal_intervalos(df,valor_inicio,intervalo)
        
    elif kind == "descriptivos":
        df=cal_descriptivos(df)
    return df

def conversion_redatam_matriz(df, continuous=False, kind=None, valor_inicio=0, intervalo=None):
    """
    conversion_redatam_matriz(df: 'DataFrame') -> Dataframe
    
    #Docstring:
    Permite de organizar los datos descargados de la plataforma de REDATAM - (INEI) en una formato de base datos de dos dimensiones.
    La base de datos de ingreso corresponde a un archivo en formato Excel, el cual se descarga luego de la busqueda de variables en REDATAM
    La base de datos resultante es un DataFrame con el ubigeo como índice

    """
    df=df[[df.columns[1], df.columns[2]]].copy()
    df.columns=["resp", "fre"]
    df=clean_str(df)
    
    df_rf=total_cat(df)                        ##categorías del resumen
    ubigeo,list_index_f=list_ubigeo_index(df)  ## Lista de ubigeos e indexes
    ubigeos_des=[]
    
    for p in list(range(0,len(list_index_f))): ## loop para extraer y los datos para cada ubigeo
        ubigeos_des.append(df.
                           pipe(extrac_freq_ubigeo,p)
                          )
    df_f=(pd.concat(ubigeos_des,axis=0))
    
    if continuous==True:
        df_f=(df_f.
              groupby("ubigeo").
              apply(analys_cont_var, kind, valor_inicio,intervalo)
             )

    else:
        df_f=(df_f.
              groupby("ubigeo").
              apply(pivot_table).
              fillna(0))
    return df_f