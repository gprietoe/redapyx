# Redapy

## ENG

Redapy is a module developed for working with data from 2017 Peruvian National Census, which data is avaiable throught a platform knows as Redatam on National Institute of Statistics and Informatics (INEI)'s official webpage. The module aims to assist python's users on downloading and cleaning 2017 census' data in a simple and intuitive manner. Radapy retrieves data in a way that allow users to work with big amount of data stored at square and settlement level. This kind of data structure become perfect for spatial analysis and data visualization.

Redapy is the first of a bigger project that aims to create a collection of modules and package to efficiently manage public data for public administration and research purposes. 

## ESP

Redapy es un módulo creado para el manejo de los resultados del Censo Nacional 2017: XII de Población, VII de Vivienda y III de Comunidades Indígenas, actualmente disponible en la página oficial del Instituto Nacional de Estadística e Informática (INEI)a través de la plataforma Redatam. El modulo permite descargar y limpiar los datos censales de forma rápida e intuitiva. Redapy proporciona una estructura de datos que facilita el manejo de la información a nivel de manzana y centro poblado de acceso público desde el 2017, ideal para el análisis espacial y la visualización de los datos.

Redapy es parte de un proyecto mayor cuyo objeto es crear un biblioteca de módulos que permitan reducir tiempo de procesamiento de datos de acceso públicos y con ello aportar herramientas para la investigación y la gestión pública basada en evidencia.

## Installation 

```bash
! git clone https://github.com/gprietoe/redapy.git
```

## Quickstart

#### Limpieza de datos
Redapy permite limpiar los resultados de las consultas realizadas en Redatam de forma sencilla.

```python
import pandas as pd
import redapy

# Abrimos el excel descargado de nuestra consulta en la plataforma de Redatam
df=pd.read_excel("Servicio de agua de la vivienda_2017.xlsx")
redapy.frequency(df, pivot=True).head(3)
'''        
        CAMION CISTERNA  EMPRESA PRESTADORA  MUNICIPALIDAD  ORGANIZACION  VECINO
        (PAGO DIRECTO)	 DE SERVICIOS                       COMUNAL	
ubigeo					
0101	49	             6505                1348           3148          13
0102	59	             5765                1747           6057          14
0103	0	             0                   3767           1892          5
'''
```
#### Tabla cruzada
```python
import pandas as pd
import redapy

# cargamos el resultado de nuestra consulta en la plataforma de Redatam
df=pd.read_excel("Discapacidad 4 por edad_2017.xlsx")
redapy.cross_table(df, continuous=True, kind="descriptivos").head(3)

"""
        Sí, tiene discapacidad para moverse o caminar para usar brazos y piernas
        Numero     Edad
        de casos   promedio
ubigeo		
0101	1414       59.905941
0102	1521       57.236029
0103	858        60.085082
"""
```

## Advace users

#### Scrapping
Con redapy es posible automatizar pedidos de datos utilizando el **Procesador estadístico en Linea** de la plataforma de Redatam.
Para ello es necesario utilizar la librería Selenium y tener instalado el drive de tu navegador.

#### Query a Tabla cruzada
```python
import redapy

# Definimos las rutas
URL = "https://censos2017.inei.gob.pe/bininei/RpWebStats.exe/CmdSet?BASE=CPV2017&ITEM=PROGRED&lang=esp"
ser_url = r'C:\\Users\\Guillermo\\Desktop\\chromedriver.exe'

# Definimos los criterios del pedido de datos
area = ["Manzana"]
var1 = ["Poblacio.C5P17"]
selection = ["Provinci 1501"]
filter_a = "Distrito"

query=redapy.query_final(tipo="Frequency",var1=var1,area_break=area,selection=selection)
redapy.make_query_2017(query,URL,ser_url).head(3)
'''
    La semana pasada - ¿Qué hacia?
	resp	fre	ubigeo
8	Hombre	45	15010800010010000401
9	Mujer	31	15010800010010000401
15	Hombre	62	15010800010010000601
'''
```

## Citado 

For citation purpose please use the following:

Prieto, Guillermo & Traverso, Diego (2022) "". --> Deberíamos encontrar un espacio para publicarlo aunque sea como reseña