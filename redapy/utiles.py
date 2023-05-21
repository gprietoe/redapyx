

# Se redefine el string de la varible como lista de un solo valor (ya que asi funciona para la union de caracteres del query) asignandole el primer valor de acuerdo al diccionario que es un STRING
# el segundo valor seria númerico (1,2,3,4,5) por si en algun momento queremos utilizarlo de esa manera.
def set_string_for_query(string_name, param_area=False):
    
    string_name_dic = {'DEPARTAMENTO':['Departam',1,2],
                       'PROVINCIA':['Provinci',2,4],
                       'DISTRITO':['Distrito',3,6],
                       'MANZANA':['Manzana',4,None],
                       'CENTRO POBLADO':['Centro Poblado',5,None]}
    
    if param_area==True:
        string_res=[string_name_dic[[string_name.upper().strip()][0]][0]]
    else:
        string_res=[k_values[0]+" "+string_name for key, k_values in string_name_dic.items() if k_values[2]==len(string_name)]
    
    return string_res


### CLEANING THE CENSUS VARIABLES ACCORDING TO REDATAM 
def set_var_string_for_query(string_var):
    string_var_dic = {'VIVIENDA':['Vivienda',1],
                       'HOGAR':['Hogar',2],
                       'POBLACION':['Poblacio',3]}
    
    clean_string=[string_var.upper().strip()] ## Reducimos el error humano
    string_res=string_var_dic[clean_string[0]][0]
    
    return string_res

def split_clean_append_var(var0):
    
    var1=set_var_string_for_query(var0.split(".")[0])
    var2=var0.split(".")[1]
    var=var1+"."+var2
    return var


#### FUNCTIONS FOR CLEANING _build_of_for
def str_test(dict_t, var_t):
    if type(dict_t.get(var_t))==str:
        test_r=[dict_t.get(var_t)]
    else:
        test_r=dict_t.get(var_t)
    return test_r
        
def logic_expression_trans(for_query_d,index_i):
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
    operator_m=[p.upper() for p in str_test(dict_t=for_query_d, var_t="operator")]
    
    #test number of items of the loop 
    if len(operator_m)>=2:
        ope_ex=print("Error, el operador solo puede ser una  de las opciones  NOT, AND u OR")
    else:
        ope_ex=operator_m[0]
    
    return ope_ex

def category_trans(for_query_d, index_i, variable_f):
    category_m=str_test(dict_t=for_query_d, var_t="category")
     
    #test number of items of the loop 
    if len(variable_f)==len(category_m):
        cat_ex=category_m[index_i]
    else:
        cat_ex=print("error, el número de variables y la categorías no son iguales")
    
    return cat_ex