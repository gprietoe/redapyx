#!/usr/bin/env python
# coding: utf-8

# In[3]:


import requests
import import_ipynb
import bs4
from bs4 import BeautifulSoup
from requests_html import HTMLSession, user_agent
from Redapy_query import query_final ## el código esta en el notebook llamado Redapy_query
import pandas as pd
import requests_random_user_agent
import time
import urllib.parse

area = ["Provinci"]
var1 = ["Poblacio.C5P41"]
var2 = ["Poblacio.C5P82"]
selection = ["Provinci 1501"]
filter_a = "Distrito"

rundef = query_final(tipo="crosstab",variables1=var1,variables2=var2,area_break=area,selection=selection)
enlace = "https://censos2017.inei.gob.pe/bininei/RpWebStats.exe/CmdSet?"
payload = {
    'MAIN':'WebServerMain.inl',
    'BASE':'CPV2017DI',
    'LANG':'esp',
    'CODIGO':'XXUSUARIOXX',
    'ITEM':'PROGRED',
    'MODE':'RUN',
   'CMDSET':'RUNDEF+Job%0D%0ATABLE+TABLE1%0D%0A++++AS+CROSSTABS+OF+Poblacio.C5P12+BY+Vivienda.C2P4%0D%0A++++AREABREAK+Provinci',
    'Submit':'Ejecutar'
}
payload2 = 'https://censos2017.inei.gob.pe/bininei/RpWebStats.exe/CmdSet?MAIN=WebServerMain.inl&BASE=CPV2017DI&LANG=esp&CODIGO=XXUSUARIOXX&ITEM=PROGRED&MODE=RUN&CMDSET=RUNDEF%20Job%0A%0A%0A%0ATABLE%20TABLE1%0A%20%20%20%20AS%20CROSSTABS%20OF%20Poblacio.C5P12%20BY%20Vivienda.C2P4%0A%20%20%20%20AREABREAK%20Provinci&Submit=Ejecutar'
def make_query(link): # hace consulta "query" a redatam a través de procesador estadístico online
    print(payload)
    session = HTMLSession()
#     response = session.request(method="post",url=link,data=payload2,headers={'User-Agent':session.headers['User-Agent']})
#     response = session.request(method="post",url=link,data=payload)
    response = session.request(method="post",url=link)
    response.html.render(timeout = 9999)
    html = response.html.html
    soup = BeautifulSoup(html, "html5lib")
    print(soup)
    iframe = soup.find('iframe',{'name':'grid'})['src']
    print(iframe)
    response = session.request(method="get",url=iframe)
    response.html.render(timeout = 999)
    html = response.html.html
    soup = BeautifulSoup(html, "html5lib")
    print(soup)
    return soup

def make_dataframe(html): # crea dataframe con resultados
    temp_table = pd.read_html(str(html)) # lee todos los dataframes de la tabla de resultados
    return temp_table # devuelve lista con dataframes

merged = pd.concat(make_dataframe(make_query(payload2)))

Excelwriter = pd.ExcelWriter("tablas_redatam2017_cruzada.xlsx",engine="xlsxwriter") #exporta en excel dataframe final
merged.to_excel(Excelwriter)
Excelwriter.save()

# In[ ]:




