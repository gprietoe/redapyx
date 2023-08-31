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
            No pagan por el   Sí pagan por el
    ubigeo 	servicio de agua  servicio de agua
    150101	634	              73731
    150102	386	              16341
    150103	2597	          149089
    150104	45	              10908
    ...     ...               ...
    150143  1473              92348

#### Tabla cruzada
También es posible solicitar la consulta de dos variables
```python
redapyx.get(table_type='crosstab',var1="vivienda.C2P8", var2="vivienda.TOTELD",
            area_break="distrito", selection="1501")
```
                                                          freq
    ubigeo	fila	          columna                     
    150101	Sí pagan por el   Vivienda sin Adulto Mayor  64233
            servicio de agua  Vivienda con Adulto Mayor	  9498
                                                  Total  73731
            No pagan por el   Vivienda sin Adulto Mayor	   514
            servicio de agua  Vivienda con Adulto Mayor	   120
       ...               ...                        ...    ...
    150143	Sí pagan por el   Vivienda con Adulto Mayor   6309
            servicio de agua                      Total  92348	
            No pagan por el   Vivienda sin Adulto Mayor   1368
            servicio de agua  Vivienda con Adulto Mayor    105
                                                  Total   1473

#### spatial data
redapyx provee la posibilidad de agregar información georreferenciada a nivel de distrito, provincia o departamento, mediante la integración con datos espaciales del INEI, lo que son descargados en una carpeta denominada como "espatial_data" en la ruta desde donde se ejecuta el script. Si bien este es un proceso que puede realizarse manualmente, redapyx optimiza este paso para integrar la descarga, la limpieza y la visualización en una sola función.
- Este resultado se logra agregando el parámetro output="geodata"

```python
>>> gdf=redapyx.get(table_type='frequency',var1="poblacion.C5P86",area_break="distrito",
                    selection="1501", pivot=True, output="geodata")
    gdf.head(3)
```
    	    No se encuentra afiliado Sí, se encuentra afiliado	
    ubigeo	a ningún seguro          a algún seguro
    150119	25823	                 63372                       
    150139	7168	                 20695
    150140  55351                    273801

    ubigeo	                                         geometry                     fuente
    150119  MULTIPOLYGON (((-76.93986 -12.24773, -76.93962...  INEI - CPV2017 RESULTADOS
    150139  MULTIPOLYGON (((-77.14355 -11.79587, -77.15237...  INEI - CPV2017 RESULTADOS
    150140  MULTIPOLYGON (((-76.94775 -12.11754, -76.94809...  INEI - CPV2017 RESULTADOS

![alt text](https://github.com/gprietoe/redapyx/blob/main/notebooks/viz/Lima_metropolitana_seguro.png?raw=true "resultado_LM")

## Citado 

For citation purpose please use the following:

Prieto, Guillermo & Traverso, Diego (2022) "". --> Deberíamos encontrar un espacio para publicarlo aunque sea como reseña