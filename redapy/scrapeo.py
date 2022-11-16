#!/usr/bin/env python
# coding: utf-8

# In[11]:


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

import time
import redapy
import datetime
begin_time = datetime.datetime.now()

# area = ["Distrito"]
# var1 = ["Poblacio.PAREAasdas"]
# # var2 = ["Poblacio.C5P82"]
# selection = ["Provinci 1501"]
# filter_a = "Distrito"
# ser_url = r'C:\\Users\\Dieguinchi\\Desktop\\chromedriver.exe'

"""
FUNCIONES QUE SCRAPEA RESULTADOS DE CONSULTA REDATAM CENSO 2017 Y LO CONVIERTE EN DATAFRAME
MODIFICADO DE pyredatam.py en https://github.com/abenassi/pyredatam/blob/master/pyredatam/pyredatam.py
"""

def make_query_2017(query, url, ser_url): # hace consulta "query" a redatam a través de procesador estadístico online
    print('Scrapeo iniciado')
    options = webdriver.ChromeOptions()#carga configuración del webdriver
    options.headless = True
    ser = Service(ser_url)
    driver = webdriver.Chrome(options=options, service=ser)# el driver debe estar en archivos del pc. puede descargarse de https://chromedriver.chromium.org/downloads
    try: driver.get(url) # abre pagina web de redatam
    except: print('No se pudo abrir páginade REDATAM')
    print('Se cargó página REDATAM con éxito')
    query_input = driver.find_element(By.TAG_NAME,"textarea")# ubica linea de comandos
#     query_input.send_keys(query.decode("utf-8", "ignore"))
    query_input.send_keys(query) # escribe consulta en línea de comandos
    submit = driver.find_element(By.NAME,"Submit") #Busca botón "Ejecutar"
    submit.click()# clickea en "Ejecutar" y ejecuta consulta
    try: 
        WebDriverWait(driver, 3).until(lambda driver: len(driver.find_elements(By.XPATH,"//h2[contains(text(),'500 - Internal server error.')]")) == 1)
        print('No cargó la tabla. Error 505')
        return ""
    except: 
        print('Iniciando scrapeo...')
        WebDriverWait(driver, 999999).until(lambda driver: len(driver.find_elements(By.XPATH,"//*[contains(text(),'Descargar en formato Excel')]")) == 1)#espera 999 segundos o a que se muestren todas las tablas solicitadas, es decir, debe mostrar Descargar en formato Excel la misma cantidad de veces que la cantidad de variables de la solicitud 
        print('La tabla cargó completamente')
        html = driver.find_element(By.ID,"tab-output")# obtiene unicamente la tabla de resultados
        html = html.get_attribute('outerHTML')# obtiene el html de la tabla de resultados
        driver.close() # cierra navegador
    try: 
        tables = pd.read_html(html) # lee todos los dataframes de la tabla de resultados
        print('Tabla scrapeada con éxito en:')
        tiempo = datetime.datetime.now() - begin_time
        print(tiempo)
        table_final = pd.concat(tables)
        # if "SELECTION INLINE," in query:
        #     query_temp = query.split() 
        #     table_final['UBIGEO'] = query_temp[5]
        #     col = table_final.pop("UBIGEO")
        #     table_final.insert(0, col.name, col)
        #     return table_final
        # else:
        #     return table_final
        return table_final
    except: 
        print('No se logró scrapear la tabla')
        return ""

"""
FUNCIONES QUE GENERAN LINEA DE CÓDIGO EN LENGUAJE REDATAM
MODIFICADO DE pyredatam.py en https://github.com/abenassi/pyredatam/blob/master/pyredatam/pyredatam.py
"""
def query_final(tipo=None,var1=None, var2=None,selection=None,area_break=None,
           universe_filter=None, title=None):
    
    if tipo=="Frequency": # Frequency
        return frequency_query(var1,selection,area_break,universe_filter,title)
    if tipo=="Crosstab": # Crosstab
        return crosstab_query(var1,var2,selection,area_break,universe_filter,title)
    else:
        return "No seleccionó tipo de consulta"
    
# funcion para escribir consulta redatam en lenguaje redatam
def frequency_query(var1,selection,area_break,
                   universe_filter, title):
    # RUNDEF section
    lines = _build_rundef_section(selection,universe_filter)
    # TABLE section
    lines.append("TABLE TABLE1")
#     lines.extend(_build_title(title))
    lines.append("    AS FREQUENCY")
    lines.append(_build_area_break(area_break))
    lines.append(_build_of_variables(var1))

    return "\n".join(lines)

def crosstab_query(var1,var2,selection,area_break,
                   universe_filter,title):
    # RUNDEF section
    lines = _build_rundef_section(selection,universe_filter)

    # TABLE section
    lines.append("TABLE TABLE1")
    lines.extend(_build_title(title))
    lines.append(_build_of_variables2(var1,var2))
    lines.append(_build_area_break(area_break))

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

# query = query_final(tipo="Frequency",var1=var1,area_break=area)

# BASE_URL = "https://censos2017.inei.gob.pe/bininei/RpWebStats.exe/CmdSet?BASE=CPV2017DI&ITEM=PROGRED&lang=esp"
# # concatena dataframes de la tabla de resultados en un solo dataframe
# try: 
#     merged = pd.concat(make_dataframe(make_query_2017(query,BASE_URL)))
# except:
#     print('No se pudo generar Dataframe con resultados')

# Excelwriter = pd.ExcelWriter("tablas.xlsx",engine="xlsxwriter") #exporta en excel dataframe final
# merged.to_excel(Excelwriter)
# Excelwriter.save()
# print(datetime.datetime.now() - begin_time)


# In[ ]:




