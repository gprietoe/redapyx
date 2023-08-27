import numpy as np
import pandas as pd

# Se redefine el string de la varible como lista de un solo valor (ya que asi funciona para la union de caracteres del query) asignandole el primer valor de acuerdo al diccionario que es un STRING
# el segundo valor seria númerico (1,2,3,4,5) por si en algun momento queremos utilizarlo de esa manera.
def set_string_for_query(string_name, param_area=False):
    """
    Sets a query string based on the given string name and area parameter.

    Parameters:
        string_name (str): The name of the geographical unit (e.g., DEPARTAMENTO, PROVINCIA, etc.).
        param_area (bool): If True, returns the string name for the specified area. Default is False.

    Returns:
        list: A list containing the query string(s).
    """
    
    string_name_dic = {'DEPARTAMENTO':['Departam',1,2],
                       'PROVINCIA':['Provinci',2,4],
                       'DISTRITO':['Distrito',3,6],
                       'MANZANA':['Manzana',4,None],
                       'CENTRO POBLADO':['Cenpob',5,None]}
    
    if param_area==True:
        string_res=[string_name_dic[[string_name.upper().strip()][0]][0]]
    else:
        string_res=[k_values[0]+" "+string_name for key, k_values in string_name_dic.items() if k_values[2]==len(string_name)]
    
    return string_res


### CLEANING THE CENSUS VARIABLES ACCORDING TO REDATAM 
def set_var_string_for_query(string_var):
    """
    Cleans and formats variable strings according to Redatam conventions.
    
    Parameters:
        string_var (str): The variable name (e.g., VIVIENDA, HOGAR, POBLACION).
    
    Returns:
        str: The formatted variable name.
    """

    string_var_dic = {'VIVIENDA':['Vivienda',1],
                       'HOGAR':['Hogar',2],
                       'POBLACION':['Poblacio',3]}
    
    clean_string=[string_var.upper().strip()] ## Reducimos el error humano
    string_res=string_var_dic[clean_string[0]][0]
    
    return string_res

def split_clean_append_var(var0):
    """
    Splits, cleans, and appends variable names.
    
    Parameters:
        var0 (str): The initial variable name.
    
    Returns:
        str: The cleaned and appended variable name.
    """
    
    var1=set_var_string_for_query(var0.split(".")[0])
    var2=var0.split(".")[1]
    var=var1+"."+var2
    return var


#### FUNCTIONS FOR CLEANING _build_of_for
def str_test(dict_t, var_t):
    """
    Checks the type of the value for a specified key in a dictionary.
    
    Parameters:
        dict_t (dict): The dictionary to check.
        var_t (str): The key to look up.
    
    Returns:
        list: The value as a list.
    """   
    if type(dict_t.get(var_t))==str:
        test_r=[dict_t.get(var_t)]
    else:
        test_r=dict_t.get(var_t)
    return test_r
        
def logic_expression_trans(for_query_d,index_i):
    """
    Translates a logical expression to its corresponding symbol.
    
    Parameters:
        for_query_d (dict): The query dictionary.
        index_i (int): The index position of the logical expression in the list.
    
    Returns:
        str: The corresponding logical symbol.
    """    
    logic_d={"equal":"=",
             "greater than":">",
             "less than":"<",
             "not equal than":"<>",
             "greater or equal than":">=",
             "less or equal than":"<="}
    
    logical_exp_m=str_test(dict_t=for_query_d, var_t="logical_exp")

    #test number of items of the loop 
    if len(for_query_d.get("variables"))>=2 & len(logical_exp_m)<2:
        logic_ex=logic_d.get(logical_exp_m[0])
    else:
        logic_ex=logic_d.get(for_query_d.get('logical_exp')[index_i])
        
    return logic_ex

def operator_trans(for_query_d, index_i):
    """
    Translates the query operator to its uppercase form.
    
    Parameters:
        for_query_d (dict): The query dictionary.
        index_i (int): The index position of the operator in the list.
    
    Returns:
        str: The translated operator in uppercase.
    """

    operator_m=[p.upper() for p in str_test(dict_t=for_query_d, var_t="operator")]
    
    #test number of items of the loop 
    if len(operator_m)>=2:
        ope_ex=print("Error, el operador solo puede ser una  de las opciones  NOT, AND u OR")
    else:
        ope_ex=operator_m[0]
    
    return ope_ex

def category_trans(for_query_d, index_i, variable_f):
    """
    Translates category values for variables.
    
    Parameters:
        for_query_d (dict): The query dictionary.
        index_i (int): The index position of the category in the list.
        variable_f (str): The variable associated with the category.
    
    Returns:
        str: The translated category value.
    """    
    category_m=str_test(dict_t=for_query_d, var_t="category")
     
    #test number of items of the loop 
    if len(variable_f)==len(category_m):
        cat_ex=category_m[index_i]
    else:
        cat_ex=print("error, el número de variables y la categorías no son iguales")
    
    return cat_ex


def clean_directorio_ccpp(path, nacional=False):
    '''
    Cleans and returns a Dataframe with data according with the "Directorio Nacional de Centros Poblados 2017". The information is available on https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1541/index.htm
    Parameters:
        path (str): File path to the Excel dataset.
        nacional (bool): If True, the function reads from multiple departmental Excel files. Default is False.

    Returns:
        DataFrame: The cleaned DataFrame containing settlement data.
    '''
    col_names1 = ['codigo', 'ccpp_nombre', 'region_natural', 'altitud', 'pob_censada', 'hob_censados', 'muj_censados', 'viv_particulares', 'viv_ocupadas', 'viv_des']
    if nacional==True:
        path_html='/'.join(path.split('/')[0:9])
        dep1=list(range(1,10))
        dep2=list(range(10,26))
        dep2.remove(15)
        dep3=['15a', '15b']
        list1=[pd.read_excel(path_html+"/dpto0"+str(dep)+".xlsx", skiprows=2, dtype={'CÓDIGO': str}, names=col_names1) for dep in dep1]
        list2=[pd.read_excel(path_html+"/dpto"+str(dep)+".xlsx", skiprows=2, dtype={'CÓDIGO': str}, names=col_names1) for dep in dep2]
        list3=[pd.read_excel(path_html+"/dpto"+dep+".xlsx", skiprows=2, dtype={'CÓDIGO': str}, names=col_names1) for dep in dep3]
        
        df=pd.concat((list1+list2+list3), axis=0)
    else:
        df = pd.read_excel(path, skiprows=2, dtype={'CÓDIGO': str}, names=col_names1)
     
    df['altitud'] = np.where(df['codigo'].str.len() == 6, '0', df['altitud'])
    df = df.dropna(subset=['codigo', 'altitud']).copy()

    numeric_columns = ['altitud', 'pob_censada', 'hob_censados', 'muj_censados', 'viv_particulares', 'viv_ocupadas', 'viv_des']
    df[numeric_columns] = df[numeric_columns].replace([' ', '-'], ['', '0'], regex=True).astype(int)

    df['ubigeo'] = np.where(df['codigo'].str.len() == 6, df['codigo'], np.nan)
    df['ubigeo'] = df['ubigeo'].fillna(method='ffill')
    df = df.query('codigo.str.len() == 4 & ubigeo.notna()', engine='python').copy()
    df['ubigeo']=df.ubigeo+df.codigo
    df=df.set_index('ubigeo')
    
    return df

"""
FUNCTIONS THAT GENERATE OUTPUT FORMATS
"""
# def def_file_name(var1=None, var2=None, format_t=None):
#     if var2 is not None:
#             name = f"TABLA_{var1}_{var2}"
#     else:
#             name = f"TABLA_{var1}"
#     if factor_exp is not None:
#             name += f"_PONDERADO.{format_t}"
#     else:
#             name += f".{format_t}"
#     return name
    
# def redapyx_export():
#     if output=="dataframe":
#         name_file=def_file_name(var1=var1, var2=var2, format_t="xlsx")
#         df.to_excel(name)
#     else:
#         name_file=def_file_name(var1=var1, var2=var2, format_t="gpkg")
#         gdf.to_file(name)
#     return 


        
            

            
        
