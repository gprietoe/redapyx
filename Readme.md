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
Con redapyx es posible automatizar pedidos de datos utilizando el **Procesador estadístico en Linea** de la plataforma de Redatam.

```python
import pandas as pd
import redapyx

redapyx.get(table_type='frequency',var1="vivienda.C2P13",area_break="distrito", selection="1501")
```
| Index | resp | fre | ubigeo |
|-------|--------------|--------------|--------------|
| 0     | Alquilada    | 26985        | 150101       |
| 1     | Propia sin título de propiedad | 10045       | 150101       |
| 2     | Propia con título de propiedad | 31809       | 150101       |
| ...   | Cedida	   | 5326         | 150101       |
| ...   | ...	       | ...          | ...          |
| 516   | Otra forma   | 107          | 150143       |


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


## Citado 

For citation purpose please use the following:

Prieto, Guillermo & Traverso, Diego (2022) "". --> Deberíamos encontrar un espacio para publicarlo aunque sea como reseña