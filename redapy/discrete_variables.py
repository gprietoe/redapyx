import pandas as pd
import numpy as np

### BOTH
### Función para limpiar los caracteres especiales
def clean_str(df, column=None):
    df=df.copy()
    dic_replace={"Á":"A","É":"E","Í":"I","Ó":"O","Ú":"U","-":"","\/":""}
    df[column]=(df[column].
                  str.upper().
                  str.strip().
                  replace(dic_replace, regex=True)
                 )
    return df

### UNIVARIABLE
def index_filter_uni(df, fila_filtro):
    
    if fila_filtro!=None:
        dic_replace={"Á":"A","É":"E","Í":"I","Ó":"O","Ú":"U","-":"","/":""}
        fila_filtro=[e_string.upper().strip().translate(str.maketrans(dic_replace)) for e_string in fila_filtro]
        
        df=(df.
            set_index("resp").
            loc[fila_filtro].
            reset_index().
            pivot(index="ubigeo",columns="resp", values="fre"))
    else:
        df=df.pivot(index="ubigeo",columns="resp", values="fre")
    return df

### MULTIVARIABLE

def clean_columns_answers(df):
    df=df.copy()
    cols=df.iloc[0:1,0:].values.flatten().tolist()
    cols[-1:]=["ubigeo"]
    df.columns=cols
    df=df.iloc[1:].copy()
    return df

def multi_index(df):
    df=df.copy()
    df=pd.DataFrame(df.
                    rename({0:"freq"},axis=1).
                    set_index("fila").
                    stack())
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
        pipe(clean_str, column="columna").
        query('columna != "UBIGEO"').
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

def index_filter(df,fila_filtro=None, columna_filtro=None):
    df=df.copy()
    
    dic_replace={"Á":"A","É":"E","Í":"I","Ó":"O","Ú":"U","-":"","/":""}
    
    if (fila_filtro==None) & (columna_filtro==None):
        df_f=(df.
              reset_index().
              pivot(index=["ubigeo"] ,columns=["fila","columna"], values="freq")
             )
    
    elif (fila_filtro!=None) & (columna_filtro==None):
        fila_filtro=[e_string.upper().strip().translate(str.maketrans(dic_replace)) for e_string in fila_filtro]
        df_f=(df.
              loc[pd.IndexSlice[:,fila_filtro,:],:].
              reset_index().
              pivot(index=["ubigeo"] ,columns=["fila","columna"], values="freq")
             )
    
    elif (fila_filtro==None) & (columna_filtro!=None):
        columna_filtro=[e_string.upper().strip().translate(str.maketrans(dic_replace)) for e_string in columna_filtro]
        df_f=(df.
              loc[pd.IndexSlice[:,:,columna_filtro],:].
              reset_index().
              pivot(index=["ubigeo"] ,columns=["fila","columna"], values="freq")
             )
    
    elif (fila_filtro!=None) & (columna_filtro!=None):
        fila_filtro=[e_string.upper().strip().translate(str.maketrans(dic_replace)) for e_string in fila_filtro]
        columna_filtro=[e_string.upper().strip().translate(str.maketrans(dic_replace)) for e_string in columna_filtro]
        df_f=(df.
              loc[pd.IndexSlice[:,fila_filtro,columna_filtro],:].
              reset_index().
              pivot(index=["ubigeo"] ,columns=["fila","columna"], values="freq")
             )
        
    return df_f