

# Se redefine el string de la varible como lista de un solo valor (ya que asi funciona para la union de caracteres del query) asignandole el primer valor de acuerdo al diccionario que es un STRING
# el segundo valor seria númerico (1,2,3,4,5) por si en algun momento queremos utilizarlo de esa manera.
def set_string_for_query(string_name):
    string_name_dic = {'DEPARTAMENTO':['Departam',1],
                       'PROVINCIA':['Provinci',2],
                       'DISTRITO':['Distrito',3],
                       'MANZANA':['Manzana',4],
                       'CENTRO POBLADO':['Centro Poblado',5]}

    clean_string=[string_name.upper().strip()] ## Reducimos el error humano
    string_res=[string_name_dic[clean_string[0]][0]]
    
    return string_res