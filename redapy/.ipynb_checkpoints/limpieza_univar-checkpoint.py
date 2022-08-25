import pandas as pd
import numpy as np

### indetificar el index
def pivot_table(df):
    df=df.pivot(index="ubigeo",columns="vars", values="fre")
    return df

def clean_continuous_var(df):
    df["vars"]=df["vars"].apply(lambda x: "".join(filter(str.isnumeric, str(x)))).astype(int)
    df["fre"]=df["fre"].astype(int)
    ##numero
    return df

def grupos_intervalos(df,valor_inicio,intervalo):
    df=clean_continuous_var(df)
    
    len_var=df.vars.max() ##valor máximo
    list_in=list(range(valor_inicio,len_var+1,intervalo)) # lista con los intervalos 

    df["vars2"]=""
    df["lim_s"]=0
    for p in list_in:
        df["lim_s"]=np.where((df.vars>=p)&(df.vars<=p+intervalo),p+intervalo-1,df.lim_s)
        df["vars2"]=np.where((df.vars>=p)&(df.vars<=p+intervalo),str(p)+"-"+str(p+intervalo-1),df.vars2)

    #df["vars2"]=np.where((df.lim_s>len_var), str(max(list_in))+"-"+str(len_var-1),df.vars2)
    del df["vars"]
    df=df.rename({"vars2":"vars"},axis=1)
    df=df.groupby(["ubigeo","lim_s","vars"]).sum().reset_index().sort_values("lim_s")[["ubigeo","vars","fre"]].copy()
    return df


## Utilizamos la tabla resumen para crear la matriz de los valores posibles de la pregunta
def total_cat(df):
    
    i_start=df[df.vars=="RESUMEN"].index.values[0] #valor del index donde inicia la tabla resumen
    df_r=df.loc[i_start+3:]
    i_end=df_r[df_r.vars=="Total"].index.values[0] #valor del index donde acaba la tabla resumen

    df_rf=df.loc[i_start+3:i_end-1].copy() ## tabla resumen
    return df_rf

## Crea una lista con los ubigeos de la dataframe 
def list_ubigeo_index(df):
    ubigeo=df[(df.vars.notna())&(df.vars.str.startswith("AREA"))]["vars"].copy() ## extrae los ubigeos de cada tabla
    list_index_d=ubigeo.index.values
    return ubigeo, list_index_d

## Función para extraer la información de las frecuencias de cada tabla de ubigeo
def var_ubigeo(df,i_start_var):
    
    ubigeo, list_index=list_ubigeo_index(df)
    index_table=list_index[i_start_var]
    
    for p,q in ubigeo.loc[index_table:index_table+1].items():
        ubigeo_nom=q[7:]
    ###
    i_start_u=df.loc[index_table+3:]
    i_end_u=i_start_u[(i_start_u.vars.notna())&(i_start_u.vars=="Total")]["fre"].index[0]-1
    df_f=df.loc[i_start_u.index.values[0]:i_end_u].copy()
    df_f["ubigeo"]=str(ubigeo_nom)
    
    return df_f

def conversion_redatam_matriz(df, continuous=False, valor_inicio=0, intervalo=None):
    """
    conversion_redatam_matriz(df: 'DataFrame') -> Dataframe
    
    #Docstring:
    Permite de organizar los datos descargados de la plataforma de REDATAM - (INEI) en una formato de base datos de dos dimensiones.
    La base de datos de ingreso corresponde a un archivo en formato Excel, el cual se descarga luego de la busqueda de variables en REDATAM
    La base de datos resultante es un DataFrame con el ubigeo como índice

    """
    df=df[[df.columns[1], df.columns[2]]].copy()
    df.columns=["vars", "fre"]
    
    df_rf=total_cat(df)                        ##categorías del resumen
    ubigeo,list_index_f=list_ubigeo_index(df)
    ubigeos_des=[]
    
    if continuous==True:
        df_rf=(df_rf.
               assign(ubigeo="ubigeo").
               pipe(grupos_intervalos,valor_inicio,intervalo))
        
        df_rf_reindex=df_rf["vars"].tolist()
        df_rf=pivot_table(df_rf)
        df_rf=df_rf.drop("ubigeo")
        
        for p in list(range(0,len(list_index_f))): ## loop para extraer y girar los datos para cada tabla de ubigeo
            ubigeos_des.append(df.
                               pipe(var_ubigeo,p).
                               pipe(grupos_intervalos,valor_inicio,intervalo).## Se extra la información del ubigeo
                               pipe(pivot_table))  ## Se gira la tabla
        df_f=(pd.concat([df_rf, pd.concat(ubigeos_des)],axis=0).
              fillna(0).                           ## Se reemplazan los NaN por 0, no todos lo distritos tienen todas las categorías de la variable
              reindex(df_rf_reindex, axis=1))     
    else:
        df_rf=(df_rf.
               assign(ubigeo="ubigeo").
               pipe(pivot_table))
        df_rf=df_rf.drop("ubigeo")
        
        for p in list(range(0,len(list_index_f))): ## loop para extraer y girar los datos para cada tabla de ubigeo
            ubigeos_des.append(df.
                               pipe(var_ubigeo,p). ## Se extra la información del ubigeo
                               pipe(pivot_table))  ## Se gira la tabla 

        df_f=(pd.concat([df_rf, pd.concat(ubigeos_des)],axis=0).
              fillna(0))
    return df_f