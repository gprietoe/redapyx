## ESP

## Redapy

Redapy es un modulo en desarrollo diseñado para facilitar el manejo de los resultados del Censo Nacional 2017: XII de Población, VII de Vivienda y III de Comunidades Indígenas, disponibles en la plataforma Redatam. El modulo conecta 4 etapas del manejo de datos censales de forma simple e intuitva, las cuales son: la descarga, limpieza, exploración y visualización de datos censales.

Redapy es parte de un proyecto mayor cuyo objeto es desarrollar un biblioteca de modulos que permitan reducir tiempo de procesamiento de datos publicos para la investigación y la gestión pública.


## ENG

Redapy is a developing module created for working with data from 2017 Peruvian National Census, which data is avaiable in a platform knows as Redatam on National Institute of Statistics and Informatics (INEI)'s webpage. The module aims to assist python's users on four steps which allow them to download, clean, explore and vizualice 2017 census' data in a simple and intuitive manner.

Redapy is the first of a bigger project that aims to create a collection of modules and package to efficiently manage public data for public administration and research purposes. 


## Installation 
En desarrollo:

#### Method 1: [`pip3`](https://pypi.org)

```bash
$ pip3 install redapy
```

#### Method 2: Install From Source

```bash
$ git clone https://github.com/gprietoe/redapy.git
```

## How it works

Imagen con el flujo del proceso de Redapy


## Quickstart

#### Limpieza de datos
Redapy permite limpiar los resultados de las consultas realizadas en Redatam de forma sencilla, reorganizando la tablas de frecuencias en matrices de datos ideales para el análisis y la vizualización de datos

```python
import pandas as pd
import redapy

# Abrimos el excel descargado de nuestra consulta en la plataforma de Redatam
df=pd.read_excel("Servicio de agua de la vivienda_2017.xlsx")

tabla_1=redapy.frecuencia(df, pivot=True)
tabl_1.head(3)
        
        CAMION CISTERNA  EMPRESA PRESTADORA  MUNICIPALIDAD  ORGANIZACION  VECINO
        (PAGO DIRECTO)	 DE SERVICIOS                       COMUNAL	
ubigeo					
0101	49	             6505                1348           3148          13
0102	59	             5765                1747           6057          14
0103	0	             0                   3767           1892          5
```
#### Tabla cruzada
```python
import pandas as pd
import redapy

# cargamos el resultado de nuestra consulta en la plataforma de Redatam
df=pd.read_excel("Discapacidad 4 por edad_2017.xlsx")

tabla_2=redapy.tabla_cruzada(df, continuous=True, kind="descriptivos")
tabla_2=head(3)

>>>
        Sí, tiene discapacidad para moverse o caminar para usar brazos y piernas
        Numero     Edad
        de casos   promedio
> ubigeo		
> 0101	1414       59.905941
> 0102	1521       57.236029
> 0103	858        60.085082

```

#### Visualización 



## Advace users

#### Scrapping
Con redapy es posible automatizar pedidos de datos utilizando el **Procesador estadístico en Linea** de la plataforma de Redatam.
Para ello es necesario utilizar la librería Selenium y tener instalado el drive de su navegador.

#### Query a Tabla cruzada
```python
import redapy

# Definimos las rutas
BASE_URL = "https://censos2017.inei.gob.pe/bininei/RpWebStats.exe/CmdSet?BASE=CPV2017DI&ITEM=PROGRED&lang=esp"
DRIVER_PATH = r"C:\Users\Guillermo\Desktop\chromedriver.exe"

# Definimos los criterios del pedido de datos
area = ["Distrito"]
var1 = ["Poblacio.C5P41"]
var2 = ["Poblacio.C5P82"]
selection = ["Provinci 1501"]
filter_a = "Distrito"

tabla_3=redapy.query_final(tipo="crosstab",variables1=var1,variables2=var2,area_break=area, selection=selection)
tabla_3 
```
Imagen con ejemplo del scrapping


```python 
redapy.tabla_cruzada(tabla_3, continuous=True, kind='descriptivos')
tabla_3=head(3)

        *Sí, afiliado al EsSalud*
        Numero de casos  Edad promedio
ubigeo		
150101	112328           40.220310
150102	14034            31.732721
150103	191936           32.700582

```


## Citado 

For citation purpose please use the following:

Prieto, Guillermo & Traverso, Diego (2022) "". --> Deberíamos encontrar un espacio para publicarlo aunque sea como reseña