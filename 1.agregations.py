#%%
# month/type selection

#%%
import datetime
from calendar import monthrange
import pandas as pd
import geopandas as gpd

#%%
local_dados = '/home/jaceguay/Documents/Projetos/urbanismo/waze/scripts/resultados'
data_hj = datetime.date.today()
hoje = data_hj.strftime("%Y-%m-%d")
print(hoje)

# %%
def pegar_mes(ano, mes, tipo):
    dias_mes = range(monthrange(ano, mes)[1]+1)[1:]
    dias = []
    for d in dias_mes:
        dias.append(f'{ano}-{mes:02}-{d:02}_{tipo}')

    dados_mes = []
    for f in dias:
        try:
            dados_mes.append(gpd.read_file(f'{local_dados}/{ano}/{tipo}/{f}.json'))
        except:
            print(f'dia {f} não encontrado')
    return gpd.GeoDataFrame( pd.concat( dados_mes, ignore_index=True), crs=dados_mes[0].crs )


#%%
janeiro_jams = pegar_mes(2021,1,'jams')
