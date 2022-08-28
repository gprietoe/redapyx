import pandas as pd
import numpy as np

## Función para convertir las variables continuas en integrales
def clean_continuous_var(df):
    df=df.copy()
    try:
        df=(df.
            assign(resp=lambda df_: df_.resp.
                   apply(lambda x:"".join(filter(str.isnumeric, str(x)))).
                   astype(int)).
            assign(fre=lambda df_: df_.fre.astype(int))
           )
    except:
        raise AssertionError("La variable bajo análisis no es continua")
    return df


def cal_intervalos(df,valor_inicio,intervalo):
    '''
    Return a DataFrame where each column is a class interval
    '''    
    df=df.copy()
    len_var=df.resp.max() ##valor máximo
    list_in=(list(range(valor_inicio,len_var+1,intervalo))) # lista con los intervalos 

    df["resp2"]=""
    df["lim_s"]=0
    for p in list_in:
        df["lim_s"]=np.where((df.resp>=p)&(df.resp<=p+intervalo),p+intervalo-1,df.lim_s)
        df["resp2"]=np.where((df.resp>=p)&(df.resp<=p+intervalo),str(p)+"-"+str(p+intervalo-1),df.resp2)

    #df["resp2"]=np.where((df.lim_s>len_var), str(max(list_in))+"-"+str(len_var-1),df.resp2)
    del df["resp"]
    df=(df.
        rename({"resp2":"resp"},axis=1).
        groupby(["ubigeo","lim_s","resp"]).
        sum().
        reset_index().
        sort_values("lim_s")
        [["ubigeo","resp","fre"]].
        copy().
        pivot(index="ubigeo",columns="resp", values="fre")
       )
    return df

def cal_descriptivos(df):
    '''
    Return a DataFrame with descriptive statistics
    '''
    df=df.copy()
    df=(df.
          assign(freq2=df.fre*df.resp).
          assign(mean_2=lambda df_: df_.freq2.sum()/df_.fre.sum()).
          assign(var1=lambda df_:((df_.resp-df_.mean_2)**2)*df_.fre)
         )

    data={"numero de casos":[],"suma":[],"maximo":[],"minimo":[],"promedio":[],"varianza":[],"des estandar":[]}
    
    data["numero de casos"].append(df.fre.sum())
    data["suma"].append(df.freq2.sum())
    data["maximo"].append(df["resp"].max())
    data["minimo"].append(df["resp"].min())
    data["promedio"].append(df.freq2.sum()/df.fre.sum())
    data["varianza"].append(df.var1.sum()/df.fre.sum())
    data["des estandar"].append(np.sqrt(df.var1.sum()/df.fre.sum()))
    
    df_f=(pd.DataFrame(data).
          assign(ubigeo=df.ubigeo.iloc[0],
                 coeficiente=lambda df_:(df_["des estandar"]/df_["promedio"])*100).
          rename({"coeficiente":"coeficiente de variacion"},axis=1).
          set_index("ubigeo")
         )
    
    return df_f
    
    