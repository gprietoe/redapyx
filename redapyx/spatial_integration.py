import pandas as pd
import numpy as np
import os

def cleaning_square(gdf):
    gdf=gdf.copy()
    gdf["ubigeo"]=gdf.idmanzana.str[0:6]
    gdf["codccpp"]="0001"
    gdf["zona"]=gdf.idmanzana.str[6:11]
    gdf["manzana_su1"]=gdf.idmanzana.str[11:14]
    gdf["manzana_su2"]=gdf.idmanzana.str[14:].replace("0","", regex=True)
    gdf["manzana"]=gdf.manzana_su1+gdf.manzana_su2
    
    gdf["llave_mzs_re"]=gdf.ubigeo+gdf.codccpp+gdf.zona+gdf.manzana
    gdf["fuente"]= "INEI-CENEPRED"
    gdf=gdf.rename({'departamen':'nombdep','provincia':'nombprov','distrito':'nombdist'}, axis=1)
    gdf=gdf[['ubigeo','nombdep','nombprov', 'nombdist', 'llave_mzs_re','fuente','geometry']].copy()

    return gdf

def find_file_path(file_name):
    '''
    Search for a given file name within the directories in the PATH environment variable.

    file_name: Name of the file to search for.
    return: Full path to the file if found; otherwise None.
    '''
    # List of directories in the PATH environment variable
    path_dirs = os.environ['PATH'].split(os.pathsep)

    # Search for the file's name in each directory
    for dir in path_dirs:
        file_path = os.path.join(dir, file_name)
        if os.path.exists(file_path):
            return file_path
    return None 

def download_gpkg_data(level=None):
    '''
    Downloads the .rar file for the specified level from a specific URL and extracts the .gpkg file.

    level: Level of spatial data (e.g., Departamento, Provincia, Distrito).
    return: None, the function saves the .gpkg file in the appropriate directory.
    '''
    import urllib3
    import rarfile
    import requests
    
    try:
        if level=="Manzana":
            response=requests.get(f"https://sigrid.cenepred.gob.pe/sigridv3/storage/escenario_sismo/1_shape.zip")
            data_rar_path=os.path.join("spatial_data",f"{level}.zip")
            with open(data_rar_path, 'wb') as zip_file:
                zip_file.write(response.content)
        else:
            response=requests.get(f"https://ide.inei.gob.pe/files/{level}.rar")
            
            data_rar_path=os.path.join("spatial_data",f"{level}.rar")
            with open(f"{level}.rar", 'wb') as rar_file:
                rar_file.write(response.content)
    except:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if level=="Manzana":
            response=requests.get(f"https://sigrid.cenepred.gob.pe/sigridv3/storage/escenario_sismo/1_shape.zip",verify=False)
            data_rar_path=os.path.join("spatial_data",f"{level}.zip")
            with open(data_rar_path, 'wb') as zip_file:
                zip_file.write(response.content)
        
        else:
            response=requests.get(f"https://ide.inei.gob.pe/files/{level}.rar",verify=False)
            data_rar_path=os.path.join("spatial_data",f"{level}.rar")
            with open(data_rar_path, 'wb') as rar_file:
                rar_file.write(response.content)

    if level=="Manzana":
        return
    else:
        with rarfile.RarFile(data_rar_path) as rar:
            rar.extract(f"{level}.gpkg", os.path.join(os.path.abspath(os.getcwd()),"spatial_data"))
    
        file_path = os.path.join(os.path.abspath(os.getcwd()),"spatial_data",f"{level}.gpkg")
    
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size<=1000:
                os.remove(file_path)
                rarfile.UNRAR_TOOL = find_file_path(file_name='unrar.exe')
                with rarfile.RarFile(data_rar_path) as rar:
                    rar.extract(f"{level}.gpkg", os.path.join(os.path.abspath(os.getcwd()),"spatial_data"))
                os.remove(data_rar_path)
                return None
            else:
                os.remove(data_rar_path)
                return None
        else:
            raise Exception("The .rar file hasn't be downloaded successfully")
    return

def make_output(gdf, level):
    '''
    Builds the output GeoDataFrame based on the level provided.

    gdf: Input GeoDataFrame containing the spatial data.
    level: Level of spatial data (e.g., Departamento, Provincia, Distrito).
    :return: Modified GeoDataFrame containing the data and the selected variables for the specified level.
    '''
    ubigeo_names = ['nombdep', 'nombprov', 'nombdist']
    if level =="Departamento":
        ubigeo_names_output=ubigeo_names[:1]
    if level =="Provincia":
        ubigeo_names_output=ubigeo_names[:2]
    if level =="Distrito":
        ubigeo_names_output=ubigeo_names
    if level =="Manzana":
        ubigeo_names_output=ubigeo_names
        
    geo_position = gdf.columns.get_loc("geometry")
    df_columns = gdf.columns[geo_position + 1:].tolist()
    gdf2 = gdf[ubigeo_names_output + df_columns + ['geometry', 'fuente']]
    
    return gdf2

def open_geodata_and_def_index(file_path=None, level=None):
    '''
    Opens and cleans the geodata downloaded from INEI or CENEPRED webpage.
    file_path: Input path containing the right path with the data
    level: Level of spatial data (e.g., Departamento, Provincia, Distrito or Manzana)
    return: Modified GeoDataFrame containing the data and the right index for the next step.
    '''
    import geopandas as gpd
    
    gdf=gpd.read_file(file_path)
    
    if level=="Manzana":
        gdf=(cleaning_square(gdf).
             set_index('llave_mzs_re')
            )
    elif level=="Provincia":
        gdf=(gdf.rename({"idprov":"ubigeo"},axis=1).
             set_index('ubigeo')
            )
    elif level=="Departamento":
        gdf=(gdf.rename({"ccdd":"ubigeo"},axis=1).
             set_index('ubigeo')
            )
    else:
        gdf=gdf.set_index('ubigeo')

    return gdf
    

def redapyx_output(df=None, path_file=None, area_break=None, selection=None):
    '''
    Processes the spatial data and returns the corresponding GeoDataFrame.

    df: DataFrame to be merged with the spatial data.
    path_file: Path to the GeoPackage file containing the spatial data.
    area_break: Level of spatial data (e.g., Departamento, Provincia, Distrito).
    return: GeoDataFrame containing the merged spatial and input data for the specified level.

    Note:
    - The 'geopandas' library is required for spatial information.
    - If the required data is not found locally, it will attempt to download and extract from the web.
    '''
    try:
        import geopandas as gpd
        import os
    except (ImportError, ModuleNotFoundError):
        raise ImportError("'geopandas' is required for spatial information, "
                "use 'conda install -c conda-forge geopandas' or 'pip install geopandas'."
                )
    
    area_break_re=area_break.upper()
    level=area_break_re[0]+area_break_re.lower()[1:]
    
    if path_file is None:
        if level=="Manzana":
            prov_selected=selection[0:4]
            if prov_selected in ["1501", "0701","1507"]:
                file_name_gpkg=f"{level}.zip"
            else:
                raise Exception("Geodata for the level 'manzana' is only implemented for Lima Metropolitana and Callao. " 
                                "If you have your own data you can pass it through the parameter path_file.")
        else:
            file_name_gpkg=f"{level}.gpkg"
        
        path_file_gpkg=os.path.join(os.path.abspath(os.getcwd()),"spatial_data",file_name_gpkg)
        try:
            gdf=open_geodata_and_def_index(file_path=path_file_gpkg, level=level)
        except:
            try:
                import rarfile
                import requests
                import urllib3
            except (ImportError, ModuleNotFoundError):
                raise ImportError(
                    "'rarfile' and'request' packages are required for accesing gpkg data from INEI main web, "
                    "use 'conda install -c conda-forge geopandas' or 'pip install geopandas'.")
            
            if "spatial_data" in os.listdir(os.path.abspath(os.getcwd())):
                None
            else:
                os.mkdir("spatial_data")
            
            download_gpkg_data(level=level)
            gdf=open_geodata_and_def_index(file_path=path_file_gpkg, level=level)
    else: 
        path_file_gpkg=path_file
        gdf=open_geodata_and_def_index(file_path=path_file_gpkg, level=level)
            
    if level in ["Departamento","Provincia","Distrito"]:
        gdf=(gdf.merge(df, right_index=True, left_index=True, how='inner', validate="1:1").
             pipe(make_output,level=level))
        
        return gdf
        
    else:
        if len(selection)==4:
            gdf["prov_selected_2"]=gdf.ubigeo.str[0:4]
            gdf=gdf.query('prov_selected_2==@selection').merge(df, right_index=True, left_index=True, how='outer', validate='1:1', indicator="join2")
        else:
            gdf=gdf.query('ubigeo==@selection').merge(df, right_index=True, left_index=True, how='outer', validate='1:1', indicator="join2")

        gdf["join2"]=np.where(gdf.join2=="both", "match", gdf["join2"])
        gdf["join2"]=np.where(gdf.join2=="left_only", "sin dato redatam", gdf["join2"])
        gdf["join2"]=np.where(gdf.join2=="right_only", "solo redatam", gdf["join2"])
        gdf=make_output(gdf,level=level)
        
    return gdf
