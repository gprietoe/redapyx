import pandas as pd

### indetificar el index
def pivot_table(df):
    df=df.pivot(index="ubigeo",columns="vars", values="fre")
    return df

def total_cat(df):
    i_start=df[df.vars=="RESUMEN"].index.values[0]
    df_r=df.loc[i_start+3:]
    i_end=df_r[df_r.vars=="Total"].index.values[0]

    df_rf=df.loc[i_start+3:i_end-1].copy()
    df_rf["ubigeo"]="ubigeo"
    df_rf=df_rf.pivot(index="ubigeo",columns="vars", values="fre")
    df_rf=df_rf.drop("ubigeo")
    return df_rf

def list_ubigeo_index(df):
    ubigeo=df[(df.vars.notna())&(df.vars.str.startswith("AREA"))]["vars"].copy()
    list_index_d=ubigeo.index.values
    return ubigeo, list_index_d
    
def var_ubigeo(df,i_start_var):
    
    ubigeo, list_index=list_ubigeo_index(df)
    
    index_table=list_index[i_start_var]
    
    for p,q in ubigeo.loc[index_table:index_table+1].items():
        ubigeo_nom=q[7:]
    ###
    i_start_u=df.loc[index_table+3:]
    i_end_u=i_start_u[(i_start_u.vars.notna())&(i_start_u.vars=="Total")]["fre"].index[0]
    df_f=df.loc[i_start_u.index.values[0]:i_end_u].copy()
    df_f["ubigeo"]=str(ubigeo_nom)
    
    return df_f

def conversion_redatam_matriz(df):
    """
    conversion_redatam_matriz(df: 'DataFrame') -> Dataframe
    
    #Docstring:
    Permite de organizar los datos descargados de la plataforma de REDATAM - (INEI) en una formato de base datos de dos dimensiones.
    La base de datos de ingreso corresponde a un archivo en formato Excel, el cual se descarga luego de la busqueda de variables en REDATAM
    La base de datos resultante es un DataFrame con el ubigeo como índice

    """
    df=df[["vars", "fre"]].copy()
    ubigeo,list_index_f=list_ubigeo_index(df)
    prov=[]
    for p in list(range(0,len(list_index_f))):
        prov.append(df.
                    pipe(var_ubigeo,p).
                   pipe(pivot_table))
    df_f=pd.concat(prov)
        
    df_rf=total_cat(df)
    df_rf=df_rf.append(df_f)
    df_rf=df_rf.fillna(0)
    
    return df_rf