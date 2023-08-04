#!/usr/bin/env python
# coding: utf-8
"""
INSPIRED STRUCTURE AND CODE IN cpv2010arg.py CHECK https://github.com/abenassi/pyredatam/blob/1480c481feb0698d54b59c3c17e52661a8c793df/pyredatam/cpv2010arg.py
"""

import pandas as pd
import numpy as np
import os
import warnings
import time
import datetime

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .utiles import *
from .limpieza_univar import frequency, cross_table

"""
SCRAPING FUNCTIONS THAT GET REDATAM OUTPUT AND CONVERT IT IN PANDAS DATAFRAME
"""

def customshowwarning(message, category=None, filename=None, lineno=None, file=None, line=None):
    print(" ", message)

def get(tipo=None,censo=None, var1=None,var2=None, selection=None,area_break=None, universe_filter=None, title=None, for_query=None, factor_exp=None,
        service_path=None, test=False, mensajes=True, print_query=False, pivot=False, output=None): # makes query to redatam and extract data
    '''
    tipo: Define the type of query (frequency or crosstab)
    censo: Define census database
    var1: Define first variable
    var2: Define second varible, just aplies when crosstab type of query is selected
    selection: Filters and select data from specific geographic location (it can be one or multiple UBIGEO codes)
    area_break: Define level of data output (departamento, provincia, distrito)
    ...
    pivot:
    output: to use the option shp, geopandas's library is required 
    factor_exp:
    '''
    # selects census databases. not properly implemented yet
    censo="2017"
    if (censo=="2017") & (area_break in ["departamento","provincia","distrito"]):
        url = "https://censos2017.inei.gob.pe/bininei/RpWebStats.exe/CmdSet?BASE=CPV2017DI&ITEM=PROGRED&lang=esp"
    else: 
        url = "https://censos2017.inei.gob.pe/bininei/RpWebStats.exe/CmdSet?BASE=CPV2017&ITEM=PROGRED&lang=esp"
    
    query0=build_query(tipo=tipo, censo=censo, var1=var1, var2=var2,
                       selection=selection, area_break=area_break,universe_filter=universe_filter, title=title,
                       for_query=for_query, factor_exp=factor_exp)
    
    if print_query==True:
        print(query0[0])
        query1=make_query(query0, service_path=service_path, service_url=url, tipo=tipo, pivot=pivot, test=test, mensajes=mensajes)
    else:
        query1=make_query(query0, service_path=service_path, service_url=url, tipo=tipo, pivot=pivot, test=test, mensajes=mensajes)

    if output=="excel":
        redapyx_excel(query1,var1,var2,factor_exp)
    else:
        return query1
    ## export the dataframe (table or layer)
    
    # try:
    #     redapyx_excel(query1,var1,var2,factor_exp) if output=='Excel' else return query1
    # except:
    #     warnings.showwarning = customshowwarning(message='Error generating Excel o Shape file')
        
def make_query(query, service_path=None, service_url=None, tipo=None, pivot=False, test=False, mensajes=True): # scraping function that makes query to redatam server
    begin_time = datetime.datetime.now()

    if mensajes==True: warnings.showwarning = customshowwarning(message='Scraping starts')  
    
    options = webdriver.ChromeOptions() #carga configuración del webdriver
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    if service_path!=None:
        driver = webdriver.Chrome(service=Service(service_path), options=options)
    else:
        driver=webdriver.Chrome(options=options) ## actualizado con selinum 4.10
    
    try:
        driver.get(service_url) # open redatam webpage
    except:
        if mensajes==True: warnings.showwarning = customshowwarning(message="Can't open REDATAM webpage")
    
    if mensajes==True: warnings.showwarning = customshowwarning(message='REDATAM webpage opened successfully')
    
    query_input = driver.find_element(By.TAG_NAME,"textarea")# find redatam command prompt 
    query_input.send_keys(query[0]) # write query in redatam command prompt
    submit = driver.find_element(By.NAME,"Submit") # find "Execute" button
    submit.click()# click "Execute" button
    
    try: 
        (WebDriverWait(driver, 3).
         until(lambda driver: len(driver.find_elements(By.XPATH,"//h2[contains(text(),'500 - Internal server error.')]")) == 1)
        )
        if mensajes==True: warnings.showwarning = customshowwarning(message="Can't load tables. Webpage Error 505. Check input data.")
        return ""
    except: 
        # wait 250 seconds or time need to show all requested data until 'Descargar en formato Excel' text renders;        
        (WebDriverWait(driver, 300).
         until(lambda driver: len(driver.find_elements(By.XPATH,"//*[contains(text(),'Descargar en formato Excel')]")) == 1)
        )
        
        if mensajes==True: warnings.showwarning = customshowwarning(message='Output table loaded successfully')
        html = driver.find_element(By.ID,"tab-output")# find html output tables
        html = html.get_attribute('outerHTML')# save html output tables
        driver.close() # close navigator
    try:
        tables = pd.read_html(html) # read all tables from html and convert it to dataframes
        tiempo = datetime.datetime.now() - begin_time
        message='Table was scraped successfully in: '+ str(tiempo)
        warnings.showwarning = customshowwarning(message=message)
        table_final = pd.concat(tables) # concatenate all dataframes in one dataframe
        try:
            #cleaning all dataframes
            #it calls frequency if query is a frequency type or crosstab if query is a crosstab type
            begin_time = datetime.datetime.now()         
            table_final = frequency(table_final,pivot=pivot) if tipo=='frequency' else cross_table(table_final,pivot=pivot) if tipo=='crosstab' else table_final 
            tiempo = datetime.datetime.now() - begin_time
            message='Table was cleaned successfully in: '+ str(tiempo)
            warnings.showwarning = customshowwarning(message=message)
        except: 
            warnings.showwarning = customshowwarning(message='Error cleaning tables')    
        if test == True:
            return table_final, tiempo
        else:
            return table_final
    except: 
        warnings.showwarning = customshowwarning(message='Cant scrap table. Check input data.')
        return ""

"""
FUNCTIONS THAT GENERATE QUERY TEXT FOR REDATAM COMMAND PROMPT 
MODIFIED VERSION OF pyredatam.py CHECK https://github.com/abenassi/pyredatam/blob/master/pyredatam/pyredatam.py
"""
def build_query(tipo=None,censo=None,var1=None,var2=None,selection=None,area_break=None,universe_filter=None, title=None, for_query=None, factor_exp=False):
    '''
    tipo: Define el tipo de consulta. frequency, crosstab
    var1: Primera variable
    var2: Segunda varible, aplica cuando se selecciona el tipo=crosstab
    selection: Es el nivel de salida específico de la consulta
    area_break: Es el nivel general de la consulta. Departamento, provincia, distrito
    universe_filter:
    title:
    
    '''
    # modify values from area_break argument so they can be compatible with REDATAM 2017
    area_break=set_string_for_query(area_break,param_area=True)
    
    # modify values from selection argument so they can be compatible with REDATAM 2017
    if selection!=None:
        selection=set_string_for_query(selection,param_area=False)
    
    var1=[split_clean_append_var(var1)]
    if tipo=="frequency": # frequency    
        return frequency_query(var1,selection,area_break,universe_filter,title,for_query,factor_exp), censo
    if tipo=="crosstab": # crosstab
        var2=[split_clean_append_var(var2)]
        return crosstab_query(var1,var2,selection,area_break,universe_filter,title,for_query,factor_exp), censo
    else:
        warnings.showwarning = customshowwarning(message='No seleccionó tipo de consulta')
        return "No seleccionó tipo de consulta"
    
    
# functions that write querys in redatam programing code

def frequency_query(var1,selection,area_break,
                   universe_filter, title,for_query,factor_exp):
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
    if factor_exp==True:
        lines.append("    WEIGHT "+"Poblacio.FACTORPOND")
    return "\n".join(lines)

def crosstab_query(var1,var2,selection,area_break,
                   universe_filter,title,for_query,factor_exp):
    # RUNDEF section
    lines = _build_rundef_section(selection,universe_filter)

    # TABLE section
    lines.append("TABLE TABLE1")
    lines.extend(_build_title(title))
    lines.append(_build_of_variables2(var1,var2))
    lines.append(_build_area_break(area_break))
    if for_query!=None:
        lines.append(_build_of_for(for_query_d=for_query))
    if factor_exp==True:
        lines.append("    WEIGHT "+"Poblacio.FACTORPOND")
    return "\n".join(lines)

def _build_rundef_section(selection=None, universe_filter=None):
    lines = ["RUNDEF Job"]
    lines.append(_build_selection_inline(selection))
    lines.append(_build_universe_filter(universe_filter))
    lines.append("")
    return lines

def _build_universe_filter(universe_filter):
    return "    UNIVERSE " + universe_filter if universe_filter else ""

def _build_title(title):
    return ['    TITLE "' + title + '"'] if title else []

def _build_area_break(area_break):
    return "    AREABREAK {}".format(", ".join(area_break)) if area_break else ""

def _build_selection_inline(selection):
    return "    SELECTION INLINE, {}".format(", ".join(selection)) if selection else ""

def _build_of_variables(var1):
    if type(var1) != list:
        var1 = [var1]
    return "    OF {}".format(", ".join(filter(lambda x: str(x) if x is not None else '',var1))) if var1 else ""

def _build_of_variables2(var1,var2):
    if type(var1) != list:
        var1 = [var1]
    if type(var2) != list:
        var2 = [var2]
    return "    AS CROSSTABS OF {} BY {}".format((", ".join(filter(lambda x: str(x) if x is not None else '',var1))),(", ".join(filter(lambda x: str(x) if x is not None else '',var2)))) if var1 or var2 else ""

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
    
"""
FUNCTIONS THAT GENERATE OUTPUT FORMATS
"""

def redapyx_excel(df=None,var1=None,var2=None, factor_exp=None):
    try: 
        if var2!=None:
            name = "TABLA_"+str(var1)+"_"+str(var2)
        else:
            name = "TABLA_"+str(var1)
            
        if factor_exp!=None:     
            name = name+"_PONDERADO"+".xlsx"
        else:
            name = name+".xlsx"
            
        df.to_excel(name)
        warnings.showwarning = customshowwarning(message='Excel file generated successfully')
    except:
        warnings.showwarning = customshowwarning(message='Error generating Excel file')

# def redapyx_shape()