# %%
# month/type selection

# %%
import datetime
from calendar import monthrange
import pandas as pd
import geopandas as gpd
pd.set_option('display.max_columns', 40)

# %%
# config
local_dados = '/mnt/c/Users/jaceguay/Documents/Projetos/urbanismo/waze/scripts/resultados'
local_export = '/mnt/c/Users/jaceguay/Documents/Projetos/urbanismo/waze/scripts/export'
data_hj = datetime.date.today()
hoje = data_hj.strftime('%Y-%m-%d')
num_mesatual = int(data_hj.strftime('%m'))
num_anoatual = int(data_hj.strftime('%Y'))
data_mes_passado = data_hj.replace(day=1) - datetime.timedelta(days=1)
num_mespassado = int(data_mes_passado.strftime('%m'))
num_anopassado = int(data_mes_passado.strftime('%Y'))

# %%

# pegar dados mês/tipo


def pegar_mes(ano, mes, tipo):
    dias_mes = range(monthrange(ano, mes)[1]+1)[1:]
    dias = []
    for d in dias_mes:
        dias.append(f'{ano}-{mes:02}-{d:02}_{tipo}')

    dados_mes = []
    for f in dias:
        try:
            dados_mes.append(gpd.read_file(
                f'{local_dados}/{ano}/{tipo}/{f}.json'))
        except:
            print(f'dia {f} não encontrado')
    return gpd.GeoDataFrame(pd.concat(dados_mes, ignore_index=True),
                            crs=dados_mes[0].crs)

# %%
# ### Acumulados intervalos de tempo de espera por zonas, data atual/anterior:
# dia, semana e mês.
#
#
# ### Listas maior tempo de espera:
# vias/sentido e zona/sentido.
#
# ### Mapa
# seta direção, espessura e cor da linha tempo de espera.


# %%
mes_atual_jams = pegar_mes(num_anoatual, num_mesatual, 'jams')
mes_passado_jams = pegar_mes(num_anopassado, num_mespassado, 'jams')

# %%
# zonas
regioes_itj = gpd.read_file('basedata/regs.shp')

# %%
# união zonas
mes_atual_jams = gpd.overlay(
    mes_atual_jams,
    regioes_itj,
    how='intersection')

mes_passado_jams = gpd.overlay(
    mes_passado_jams,
    regioes_itj,
    how='intersection')

# %%
# separar por faixa horário
# pd.unique(mes_passado_jams['timestamp'].str[11:13])
# 5-8, 8-11, 11-14, 14-17, 17-20, 20-23, 23-5
# mes_passado_jams['hora'] = mes_passado_jams['timestamp'].str[11:13].astype(
#     'int')

mes_passado_jams['intervalohora'] = pd.cut(mes_passado_jams['timestamp'].str[11:13].astype('int'),
                                           [0, 5, 8, 11, 14, 17, 20, 23],
                                           right=False)

mes_atual_jams['intervalohora'] = pd.cut(mes_atual_jams['timestamp'].str[11:13].astype('int'),
                                         [0, 5, 8, 11, 14, 17, 20, 23],
                                         right=False)

# %%
# ## Agregações
# Mês

# Mês passado
mes_passado_jams_total = mes_passado_jams.groupby(
    ['intervalohora']
).agg({
    'delay': sum
}).reset_index()

mes_passado_jams_total['intervalohora'] = mes_passado_jams_total[
    'intervalohora'
].astype(str).str[1:-1]

# exportar json
mes_passado_jams_total.to_json(
    'export/mes_passado_jams_total.json',  orient="columns")

mes_passado_jams_total.to_csv('export/mes_passado_jams_total.csv')

# Mês atual
mes_atual_jams_total = mes_atual_jams.groupby(
    ['intervalohora']
).agg({
    'delay': sum
}).reset_index()

mes_atual_jams_total['intervalohora'] = mes_atual_jams_total[
    'intervalohora'
].astype(str).str[1:-1]

# exportar json
mes_atual_jams_total.to_json(
    'export/mes_atual_jams_total.json', orient="columns")

mes_atual_jams_total.to_csv('export/mes_atual_jams_total.csv',index=False)

# %%
# Mês + dia da semana + hora

mes_passado_jams_total_diasemana = mes_passado_jams.groupby(
    ['dia_semana', 'intervalohora']
).agg({
    'delay': sum
})

mes_atual_jams_total_diasemana = mes_atual_jams.groupby(
    ['dia_semana', 'intervalohora']
).agg({
    'delay': sum
})

# %%
# Mês + dia da semana + bairro + sentido

mes_passado_jams_total_bairro = mes_passado_jams.groupby(
    ['nome', 'orientacao', 'dia_semana']
).agg({
    'delay': sum
})

mes_atual_jams_total_bairro = mes_atual_jams.groupby(
    ['nome', 'orientacao', 'dia_semana']
).agg({
    'delay': sum
})

# %%
# Via + dia da semana + sentido

mes_passado_jams_total_viatotal = mes_passado_jams.groupby(
    ['street', 'orientacao', 'dia_semana', 'intervalohora']
).agg({
    'delay': sum
})

mes_atual_jams_total_viatotal = mes_atual_jams.groupby(
    ['street', 'orientacao', 'dia_semana', 'intervalohora']
).agg({
    'delay': sum
})

# %%
# Via + destino + dia da semana + sentido

mes_passado_jams_total_via_destino = mes_passado_jams.groupby(
    ['street', 'endNode', 'dia_semana', 'intervalohora']
).agg({
    'delay': sum
})

mes_atual_jams_total_via_destino = mes_atual_jams.groupby(
    ['street', 'endNode', 'dia_semana', 'intervalohora']
).agg({
    'delay': sum
})

# %%
