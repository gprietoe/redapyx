# redapyx

## ENG

redapyx is a module developed for working with data from 2017 Peruvian National Census, which data is avaiable throught a platform knows as Redatam on National Institute of Statistics and Informatics (INEI)'s official webpage. The module aims to assist python's users on downloading and cleaning 2017 census' data in a simple and intuitive manner. Radapy retrieves data in a way that allow users to work with big amount of data stored at square and settlement level. This kind of data structure become perfect for spatial analysis and data visualization.

redapyx is the first of a bigger project that aims to create a collection of modules and package to efficiently manage public data for public administration and research purposes. 

## ESP

Redapyx es un módulo creado acceder a los resultados del Censo Nacional 2017: XII de Población, VII de Vivienda y III de Comunidades Indígenas, actualmente disponibles en la página oficial del Instituto Nacional de Estadística e Informática (INEI) a través de la plataforma Redatam. El modulo permite descargar y limpiar los datos censales de forma rápida e intuitiva. Redapyx proporciona una estructura de datos que facilita el manejo de la información a nivel de manzana y centro poblado de acceso público desde el 2017, ideal para el análisis espacial y la visualización de los datos.

Redapyx es parte de un proyecto mayor cuyo objeto es crear un repositorio de módulos que permitan reducir el tiempo de procesamiento de datos de acceso público y con ello contribuir a la investigación y a la gestión pública basada en evidencia.

## Install 

```bash
! git clone https://github.com/gprietoe/redapyx.git
```

## Quickstart

Para acceder a la información del CPV 2017, redapyx se conecta con el **Procesador estadístico en Linea** de la plataforma de Redatam, al cual se puede acceder a través de https://censos2017.inei.gob.pe/redatam/

```python
import pandas as pd
import redapyx

>>> redapyxx.get(table_type='frequency',var1="vivienda.C2P8",
                 area_break="distrito", selection="1501", pivot=True)
```
    >>> redapyxx.get(table_type='frequency',var1="vivienda.C2P8",
                 area_break="distrito", selection="1501", pivot=True)

        	No pagan por  Sí pagan por 
         	el servicio   el servicio
    ubigeo  de agua       de agua
    150101	634	          73731
    150102	386	          16341
    150103	2597	      149089
    150104	45	          10908

>>> redapyxx.get(table_type='frequency',var1="vivienda.C2P8",
                 area_break="distrito", selection="1501", pivot=True)



#### Tabla cruzada
```python
import pandas as pd
import redapyx

# cargamos el resultado de nuestra consulta en la plataforma de Redatam
df=pd.read_excel("Discapacidad 4 por edad_2017.xlsx")
redapyx.cross_table(df, continuous=True, kind="descriptivos").head(3)

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


## Citado 

For citation purpose please use the following:

Prieto, Guillermo & Traverso, Diego (2022) "". --> Deberíamos encontrar un espacio para publicarlo aunque sea como reseña