#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import import_ipynb
import bs4
import time
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from Redapy_query_requests import query_final ## el código esta en el notebook llamado Redapy_query
import pandas as pd

area = ["Provinci"]
var1 = ["Poblacio.C5P41"]
var2 = ["Poblacio.C5P82"]
# selection = ["Provinci 1501"]
filter_a = "Distrito"

query = query_final(tipo="crosstab",variables1=var1,variables2=var2,area_break=area)
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}

def make_query(query): # hace consulta "query" a redatam a través de procesador estadístico online
    print(query)
    session = requests.Session()
    response = session.get(query,headers=headers)
    response.status_code
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html5lib")
        print(soup+"A")
        iframe = soup.find('iframe',{'name':'grid'})['src']
        print(iframe+"B")
        html_iframe = requests.get(iframe,headers=headers)
        if html_iframe.status_code == 200:
            html = BeautifulSoup(html_iframe.text,"html5lib")
            print(html)
        elif response.status_code == 404:
            html = ""
#         iframe_url = iframe.replace('&amp;TYPE=TMP','') 
#         iframe = soup.find_all('iframe')[0]
        return html
    elif response.status_code == 404:
        print('Error 404')
        html  = ""
        return html

def make_dataframe(html): # crea dataframe con resultados
    print(str(html))
    temp_table = pd.read_html(str(html)) # lee todos los dataframes de la tabla de resultados
    return temp_table # devuelve lista con dataframes

merged = pd.concat(make_dataframe(make_query(query)))


# In[ ]:





# In[ ]:




