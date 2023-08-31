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
from .spatial_integration import redapyx_output

"""
SCRAPING FUNCTIONS THAT GET REDATAM OUTPUT AND CONVERT IT IN PANDAS DATAFRAME
"""

# def customshowwarning(message, category=None, filename=None, lineno=None, file=None, line=None):
#     print(" ", str(message))

def get(table_type=None,censo=None, var1=None,var2=None, selection=None,area_break=None, universe_filter=None, title=None, for_query=None, factor_exp=False, service_path=None, test=False, output_info=True, print_query=False, pivot=False, output=None,path_file=None):
    '''
    Parameters
    ----------
    table_type: Define the type of query (frequency or crosstab).
    censo: Define census database -  for future versions.
    var1: Define the first variable. 
    var2: Define the second variable; only applies when the crosstab type of query is selected.
    selection: Filters and selects data from specific geographic locations using INEI's ubigeo.
    area_break: Define the level of data output (departamento, provincia, distrito, centro poblado o manzana).
        In case of the level "manzana", the last two numbers of Ubigeo are replaced by the corresponding letter from the alphabet. For example, '01' becomes 'A', '02' becomes 'B', '03' becomes 'C' and so on up to 27, which becomes 'Z'. That happens because the spatial data for squares is coded as 18 numbers or 18 numbers plus a letter from the alphabet.
    universe_filter: Define specific filters for the data universe being queried.
    title: Define the title for the query.
    for_query: Dictionary containing query elements, such as variables, logic expressions, categories, and operators.
        - *variables*: A list of variables for the query
        - *category*: A list of numeric values corresponding to each variable. There values match those assigned in the 2017 Census form.
        - *logical_exp*: A list of logical expressions used to relate variables and categories (e.g., equal, greater than, less than, etc.)
        - *operator*: A list of operators that combine two or more variables, their categories, and logical expressions. This enables the creation of complex queries for Redatam.
        
    factor_exp: Boolean, if True, applies a specific factor created by INEI to the query; otherwise False.
    service_path: Define the path for the service to be called. After selenium 4.10 it's not longer needed because it uses SeleniumManager to deal with the right driver's version.
    test: Boolean, if True, runs the query in test mode; otherwise False.
    output_info: Boolean, if True, provides additional information in the output; otherwise False.
    print_query: Boolean, if True, prints the query; otherwise False.
    pivot: Boolean, if True, applies a pivot to the query; otherwise False.
    output: Define the output type; to use the option "geodata" the geopandas library is required.
    path_file: Define the path where the geodata is stored. If None, the spatial data is downloaded from INEI webpage.
    

    Returns:
    Returns a dataframe containing data from Redatam. If output is set as "geodata", a GeoDataframe containing the result and its geometry is returned
    '''
    # selects census databases. not properly implemented yet
    censo="2017"
            
    if (censo=="2017") & (area_break in ["departamento","provincia","distrito"]):
        url = "https://censos2017.inei.gob.pe/bininei/RpWebStats.exe/CmdSet?BASE=CPV2017DI&ITEM=PROGRED&lang=esp"
    else: 
        url = "https://censos2017.inei.gob.pe/bininei/RpWebStats.exe/CmdSet?BASE=CPV2017&ITEM=PROGRED&lang=esp"
    
    query0=build_query(table_type=table_type, censo=censo, var1=var1, var2=var2,
                       selection=selection, area_break=area_break, universe_filter=universe_filter, title=title,
                       for_query=for_query, factor_exp=factor_exp)
    
    if print_query==True:
        print(query0[0])
        query1=make_query(query0,
                          service_path=service_path, service_url=url,
                          table_type=table_type, pivot=pivot, test=test, output_info=output_info, area_break=area_break)
    else:
        query1=make_query(query0,
                          service_path=service_path, service_url=url,
                          table_type=table_type, pivot=pivot, test=test, output_info=output_info, area_break=area_break)

    if output=="geodata":
        if pivot==True:
            if area_break in ["departamento","provincia","distrito","manzana"]:
                gdf=redapyx_output(df=query1, path_file=path_file, area_break=area_break, selection=selection)
                return gdf
            else:
                raise Exception("Geodata for the level 'ccpp' is not yet implemented") ### this implementation needs to use OWS
        else:
            raise Exception("To merge data from Redatam with the spatial data, the 'pivot' parameter must be set to True")
    else:
        return query1
        
def make_query(query, service_path=None, service_url=None, table_type=None, pivot=False, test=False, output_info=True , area_break=None): # scraping function that makes query to redatam server
    begin_time = datetime.datetime.now()

    if output_info==True:  print('Scraping starts')#warnings.showwarning = customshowwarning(message='Scraping starts')  
    
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
    except WebDriverException:
        raise Exception("Can't open REDATAM webpage") 
        #if output_info==True: warnings.wars("Can't open REDATAM webpage")#warnings.showwarning = customshowwarning(message="Can't open REDATAM webpage")
    
    if output_info==True: print('REDATAM webpage opened successfully') # warnings.showwarning = customshowwarning(message='REDATAM webpage opened successfully')
    
    query_input = driver.find_element(By.TAG_NAME,"textarea")# find redatam command prompt 
    query_input.send_keys(query[0]) # write query in redatam command prompt
    submit = driver.find_element(By.NAME,"Submit") # find "Execute" button
    submit.click()# click "Execute" button
    
    try: 
        (WebDriverWait(driver, 3).
         until(lambda driver: len(driver.find_elements(By.XPATH,"//h2[contains(text(),'500 - Internal server error.')]")) == 1)
        )
        raise Exception("Can't load the tables. Webpage retrive an  Error 505. Check your input data.")
    except: 
        # wait 250 seconds or time need to show all requested data until 'Descargar en formato Excel' text renders;        
        (WebDriverWait(driver, 360).
         until(lambda driver: len(driver.find_elements(By.XPATH,"//*[contains(text(),'Descargar en formato Excel')]")) == 1)
        )
        
        if output_info==True: print('Output table loaded successfully')# warnings.showwarning = customshowwarning(message='Output table loaded successfully')
        html = driver.find_element(By.ID,"tab-output")# find html output tables
        html = html.get_attribute('outerHTML')# save html output tables
        driver.close() # close navigator
    try:
        tables = pd.read_html(html) # read all tables from html and convert it to dataframes
        tiempo = datetime.datetime.now() - begin_time
        message='Table was scraped successfully in: '+ str(tiempo)
        print(message)
        #warnings.showwarning = customshowwarning(message=message)
        table_final = pd.concat(tables) # concatenate all dataframes in one dataframe
        try:
            #cleaning all dataframes
            #it calls frequency if query is a frequency type or crosstab if query is a crosstab type
            begin_time = datetime.datetime.now()         
            table_final = frequency(table_final,pivot=pivot, area_break=area_break) if table_type=='frequency' else cross_table(table_final, pivot=pivot, area_break=area_break) if table_type=='crosstab' else table_final 
            
            tiempo = datetime.datetime.now() - begin_time
            message='Table was cleaned successfully in: '+ str(tiempo)
            print(message)
            #warnings.showwarning = customshowwarning(message=message)
        except: 
            raise Exception("Error cleaning tables")
        if test == True:
            return table_final, tiempo
        else:
            return table_final
    except WebDriverException: 
        raise Exception("Cant scrap the tables. Check your input data.")
        return ""

"""
FUNCTIONS THAT GENERATE QUERY TEXT FOR REDATAM COMMAND PROMPT 
MODIFIED VERSION OF pyredatam.py CHECK https://github.com/abenassi/pyredatam/blob/master/pyredatam/pyredatam.py
"""
def build_query(table_type=None,censo=None,var1=None,var2=None,selection=None,area_break=None,universe_filter=None, title=None, for_query=None, factor_exp=None):
    '''    
    '''
    # modify values from area_break argument so they can be compatible with REDATAM 2017
    area_break=set_string_for_query(area_break,param_area=True)
    
    # modify values from selection argument so they can be compatible with REDATAM 2017
    if selection!=None:
        selection=set_string_for_query(selection,param_area=False)
    
    var1=[split_clean_append_var(var1)]
    if table_type=="frequency": # frequency    
        return frequency_query(var1,selection,area_break,universe_filter,title,for_query,factor_exp), censo
    if table_type=="crosstab": # crosstab
        var2=[split_clean_append_var(var2)]
        return crosstab_query(var1,var2,selection,area_break,universe_filter,title,for_query,factor_exp), censo
    else:
        raise Exception("No seleccionó tipo de consulta")
        return None
    
    
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
    """
    Generates a formatted "FOR" query line for a given query dictionary.
    
    Parameters:
    -----------
    for_query_d : dict
        Dictionary containing query elements, such as variables, logic expressions, categories, and operators.

    Returns:
    --------
    line_final : str
        Formatted "FOR" query line.
        
    Notes:
    ------
    - `str_test`, `split_clean_append_var`, `logic_expression_trans`, `category_trans`, and `operator_trans` are assumed to be predefined helper functions.
    - The function assumes that the dictionary `for_query_d` contains specific keys that are used in the helper functions.

    Examples:
    ---------
    >>> _build_of_for({"variables": ["var1", "var2"], ...})
    "FOR var1 == value1 && var2 <= value2 ..."
    
    """
    variables_m=str_test(dict_t=for_query_d, var_t="variables")
    variables_f=[split_clean_append_var(_vars) for _vars in variables_m]

    if len(variables_f)>=2:
        a=[item_p+" "+logic_expression_trans(for_query_d=for_query_d,index_i=index_i)+" "+category_trans(for_query_d=for_query_d, index_i=index_i,variable_f=variables_f)+" "+operator_trans(for_query_d=for_query_d,index_i=index_i) for index_i, item_p in enumerate(variables_f)]
        line_final=("    FOR {}".format(", ".join(filter(lambda x: str(x) if x is not None else '', a))) if a else "").replace(",","")[0:-3]
    else:
        a=[item_p+" "+logic_expression_trans(for_query_d=for_query_d,index_i=index_i)+" "+category_trans(for_query_d=for_query_d, index_i=index_i,variable_f=variables_f) for index_i, item_p in enumerate(variables_f)]
        line_final=("    FOR {}".format(", ".join(filter(lambda x: str(x) if x is not None else '', a))) if a else "")

    return line_final
    
