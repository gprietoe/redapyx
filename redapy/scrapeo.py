#!/usr/bin/env python
# coding: utf-8
"""
MODIFICADO DE cpv2010arg.py en https://github.com/abenassi/pyredatam/blob/1480c481feb0698d54b59c3c17e52661a8c793df/pyredatam/cpv2010arg.py
"""

import pandas as pd
import numpy as np
import os
import warnings

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .utiles import *

import time
import redapy
import datetime


"""
FUNCIONES QUE SCRAPEA RESULTADOS DE CONSULTA REDATAM CENSO 2017 Y LO CONVIERTE EN DATAFRAME
MODIFICADO DE pyredatam.py en https://github.com/abenassi/pyredatam/blob/master/pyredatam/pyredatam.py
"""

def make_query_2017(query, service_path=None, test=False, mensajes=True): # hace consulta "query" a redatam a través de procesador estadístico online
    begin_time = datetime.datetime.now()
    
    # Selecciona URL de acuerdo al censo seleccionado. Dado que CPV2017_D y CPV2017_M usan el mismo código de scrapeo, solo se añade un IF para que seleccione la URL correcta.
    
    if query[1] == 'CPV2017_M':
        url = 'https://censos2017.inei.gob.pe/bininei/RpWebStats.exe/CmdSet?BASE=CPV2017&ITEM=PROGRED&lang=esp'
    else: 
        url = 'https://censos2017.inei.gob.pe/bininei/RpWebStats.exe/CmdSet?BASE=CPV2017DI&ITEM=PROGRED&lang=esp'
        
    if mensajes==True: print('Scrapeo iniciado')    
    options = webdriver.ChromeOptions() #carga configuración del webdriver
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    
    ## Se puede establecer la ruta donde se encuentra el service (ChromeDriver) o se puede copiar el .exe en una de las rutas usadas por el notebook.
    ## Para el caso de google colab es mejor copiar el service en uno de paths del sistema del environment. Estos se pueden ver usando sys.path
    if service_path!=None:
        driver = webdriver.Chrome(service=Service(service_path),
                                  options=options)
    else:
        driver=webdriver.Chrome('chromedriver',options=options)
    
    try:
        driver.get(url) # abre pagina web de redatam
    except:
        if mensajes==True: print('No se pudo abrir páginade REDATAM')
    
    if mensajes==True: print('Se cargó página REDATAM con éxito')
    
    query_input = driver.find_element(By.TAG_NAME,"textarea")# ubica linea de comandos
    # query_input.send_keys(query.decode("utf-8", "ignore"))
    query_input.send_keys(query[0]) # escribe consulta en línea de comandos
    submit = driver.find_element(By.NAME,"Submit") #Busca botón "Ejecutar"
    submit.click()# clickea en "Ejecutar" y ejecuta consulta
    
    try: 
        (WebDriverWait(driver, 3).
         until(lambda driver: len(driver.find_elements(By.XPATH,"//h2[contains(text(),'500 - Internal server error.')]")) == 1)
        )
        if mensajes==True: print('No cargó la tabla. Error 505')
        return ""
    except: 
        #espera 250 segundos o a que se muestren todas las tablas solicitadas; es decir,
        #debe mostrar Descargar en formato Excel la misma cantidad de veces que la cantidad de variables de la solicitud 
        
        #print('Iniciando scrapeo...')
        (WebDriverWait(driver, 250).
         until(lambda driver: len(driver.find_elements(By.XPATH,"//*[contains(text(),'Descargar en formato Excel')]")) == 1)
        )
        
        if mensajes==True: print('La tabla cargó completamente')
        html = driver.find_element(By.ID,"tab-output")# obtiene unicamente la tabla de resultados
        html = html.get_attribute('outerHTML')# obtiene el html de la tabla de resultados
        driver.close() # cierra navegador
    try:
        tables = pd.read_html(html) # lee todos los dataframes de la tabla de resultados
        tiempo = datetime.datetime.now() - begin_time
        print('Tabla scrapeada con éxito en:',tiempo)
        table_final = pd.concat(tables)
            
        # if "SELECTION INLINE," in query:
        #     query_temp = query.split() 
        #     table_final['UBIGEO'] = query_temp[5]
        #     col = table_final.pop("UBIGEO")
        #     table_final.insert(0, col.name, col)
        #     return table_final
        # else:
        #     return table_final
        
        if test == True:
            return table_final, tiempo
        else:
            return table_final
    except: 
        print('No se logró scrapear la tabla')
        return ""

"""
FUNCIONES QUE GENERAN LINEA DE CÓDIGO EN LENGUAJE REDATAM
MODIFICADO DE pyredatam.py en https://github.com/abenassi/pyredatam/blob/master/pyredatam/pyredatam.py
"""
def query_final(tipo=None,censo=None,var1=None,var2=None,selection=None,area_break=None,universe_filter=None, title=None, for_query=None):
    '''
    tipo: Define el tipo de consulta. Frequency, Crosstab
    var1: Primera variable
    var2: Segunda varible, aplica cuando se selecciona el tipo=Crosstab
    selection: Es el nivel de salida específico de la consulta
    area_break: Es el nivel general de la consulta. Departamento, provincia, distrito
    universe_filter:
    title:
    
    '''
    # Modifica valores de la variable area_break para que sean compatibles con REDATAM 2017
    area_break=set_string_for_query(area_break,param_area=True)
    
    # Modifica valores de la variable selection para que sean compatibles con REDATAM 2017
    selection=set_string_for_query(selection,param_area=False)
    
    var1=[split_clean_append_var(var1)]
    if tipo=="Frequency": # Frequency    
        return frequency_query(var1,selection,area_break,universe_filter,title,for_query), censo #Se modifica para que retorne informacion sobre a qué censo se  hará la consulta y asi make_query2017 pueda leerlo
    if tipo=="Crosstab": # Crosstab
        var2=[split_clean_append_var(var2)]
        return crosstab_query(var1,var2,selection,area_break,universe_filter,title,for_query), censo 
    else:
        return "No seleccionó tipo de consulta"
    
    
# funcion para escribir consulta redatam en lenguaje redatam
def frequency_query(var1,selection,area_break,
                   universe_filter, title,for_query):
    # RUNDEF section
    lines = _build_rundef_section(selection,universe_filter)
    # TABLE section
    lines.append("TABLE TABLE1")
#     lines.extend(_build_title(title))
    lines.append("    AS FREQUENCY")
    lines.append(_build_area_break(area_break))
    lines.append(_build_of_variables(var1))
    if for_query!=None:
        lines.append(_build_of_for(for_query_d=for_query))
    
    return "\n".join(lines)

def crosstab_query(var1,var2,selection,area_break,
                   universe_filter,title,for_query):
    # RUNDEF section
    lines = _build_rundef_section(selection,universe_filter)

    # TABLE section
    lines.append("TABLE TABLE1")
    lines.extend(_build_title(title))
    lines.append(_build_of_variables2(var1,var2))
    lines.append(_build_area_break(area_break))
    if for_query!=None:
        lines.append(_build_of_for(for_query_d=for_query))

    return "\n".join(lines)

# funcion para escribir parametros de la primera linea de la consulta
def _build_rundef_section(selection=None, universe_filter=None):
    lines = ["RUNDEF Job"]
    lines.append(_build_selection_inline(selection))
    lines.append(_build_universe_filter(universe_filter))
    lines.append("")
    return lines

# funcion para escribir parametros de filtro universo
def _build_universe_filter(universe_filter):
    return "    UNIVERSE " + universe_filter if universe_filter else ""

# funcion para escribir parametros de nombre de la tabla
def _build_title(title):
    return ['    TITLE "' + title + '"'] if title else []

# funcion para escribir parametros de nivel de salida de la consulta (areabreak)
def _build_area_break(area_break):
    return "    AREABREAK {}".format(", ".join(area_break)) if area_break else ""

# funcion para escribir parametros de nivel de salida de la consulta (selection)
def _build_selection_inline(selection):
    return "    SELECTION INLINE, {}".format(", ".join(selection)) if selection else ""

# funcion para escribir parametros de variables de la consulta tipo Frecuency
def _build_of_variables(var1):
    if type(var1) != list:
        var1 = [var1]
    return "    OF {}".format(", ".join(filter(lambda x: str(x) if x is not None else '',var1))) if var1 else ""

# funcion para escribir parametros de variables de la consulta tipo Crosstab
def _build_of_variables2(var1,var2):
    if type(var1) != list:
        var1 = [var1]
    if type(var2) != list:
        var2 = [var2]
    return "    AS CROSSTABS OF {} BY {}".format((", ".join(filter(lambda x: str(x) if x is not None else '',var1))),(", ".join(filter(lambda x: str(x) if x is not None else '',var2)))) if var1 or var2 else ""

# funcion para establecer un query para una variable de la consulta tipo Frecuency
def _build_of_for(for_query_d):

    variables_m=str_test(dict_t=for_query_d, var_t="variables")
    variables_f=[split_clean_append_var(_vars) for _vars in variables_m]

    if len(variables_f)>=2:
        a=[item_p+" "+logic_expression_trans(for_query_d=for_query_d,index_i=index_i)+" "+category_trans(for_query_d=for_query_d, index_i=index_i,variable_f=variables_f)+" "+operator_trans(for_query_d=for_query_d,index_i=index_i) for index_i, item_p in enumerate(variables_f)]
        line_final=("    FOR {}".format(", ".join(filter(lambda x: str(x) if x is not None else '', a))) if a else "").replace(",","")[0:-3]
    else:
        a=[item_p+" "+logic_expression_trans(for_query_d=for_query_d,index_i=index_i)+" "+category_trans(for_query_d=for_query_d, index_i=index_i,variable_f=variables_f) for index_i, item_p in enumerate(variables_f)]
        line_final=("    FOR {}".format(", ".join(filter(lambda x: str(x) if x is not None else '', a))) if a else "")

    return line_final
    
