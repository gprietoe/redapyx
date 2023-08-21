import pandas as pd
import os

def find_file_path(file_name):
    # List of directories in the PATH environment variable
    path_dirs = os.environ['PATH'].split(os.pathsep)

    # Search for the file's name in each directory
    for dir in path_dirs:
        file_path = os.path.join(dir, file_name)
        if os.path.exists(file_path):
            return file_path
    return None 

def download_gpkg_data(level=None):
    import urllib3
    import rarfile
    import requests
    
    try:
        response=requests.get(f"https://ide.inei.gob.pe/files/{level}.rar")
        with open(f"{level}.rar", 'wb') as rar_file:
            rar_file.write(response.content)
    except:
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response=requests.get(f"https://ide.inei.gob.pe/files/{level}.rar",verify=False)
        data_rar_path=os.path.join("spatial_data",f"{level}.rar")
    
        with open(data_rar_path, 'wb') as rar_file:
            rar_file.write(response.content)

    rarfile.UNRAR_TOOL = find_file_path(file_name='unrar.exe')

    with rarfile.RarFile(data_rar_path) as rar:
        rar.extract(f"{level}.gpkg", os.path.join(os.path.abspath(os.getcwd()),"spatial_data"))

    os.remove(data_rar_path)
    return

def make_output(gdf, level):
    ubigeo_names = ['nombdep', 'nombprov', 'nombdist']
    if level =="Departamento":
        ubigeo_names_output=ubigeo_names[:1]
    if level =="Provincia":
        ubigeo_names_output=ubigeo_names[:2]
    if level =="Distrito":
        ubigeo_names_output=ubigeo_names
        
    geo_position = gdf.columns.get_loc("geometry")
    df_columns = gdf.columns[geo_position + 1:].tolist()
    gdf2 = gdf[ubigeo_names_output + df_columns + ['geometry', 'fuente']]
    
    return gdf2

def redapyx_output(df=None, path_file=None, area_break=None):
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
        file_name_gpkg=f"{level}.gpkg"
        path_file_gpkg=os.path.join(os.path.abspath(os.getcwd()),"spatial_data",file_name_gpkg)
        try:
            gdf=gpd.read_file(os.path.join(os.path.abspath(os.getcwd()),"spatial_data",file_name_gpkg))
            if level=="Provincia":
                gdf=(gdf.rename({"idprov":"ubigeo"},axis=1).
                     set_index('ubigeo')
                )
            if level=="Departamento":
                gdf=(gdf.rename({"ccdd":"ubigeo"},axis=1).
                     set_index('ubigeo')
                )
            else:
                gdf=gdf.set_index('ubigeo')
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
            
            gdf=gpd.read_file(os.path.join(os.path.abspath(os.getcwd()),"spatial_data",file_name_gpkg))
            
            if level=="Provincia":
                gdf=(gdf.rename({"idprov":"ubigeo"},axis=1).
                     set_index('ubigeo')
                    )
            elif level=="Departamento":
                gdf=(gdf.rename({"ccdd":"ubigeo"},axis=1).
                    set_index('ubigeo')
                    )
            else:
                gdf=gdf.set_index('ubigeo')
    else: 
        path_file_gpkg=path_file
        gdf=gpd.read_file(path_file_gpkg)
        
        if level=="Provincia":
            gdf=(gdf.rename({"idprov":"ubigeo"},axis=1).
                 set_index('ubigeo')
                )
        elif level=="Departamento":
            gdf=(gdf.rename({"ccdd":"ubigeo"},axis=1).
                set_index('ubigeo')
                )
        else:
            gdf=gdf.set_index('ubigeo')
            
    gdf=(gdf.merge(df, right_index=True, left_index=True, how='inner', validate="1:1").
         pipe(make_output,level=level))

    return gdf
