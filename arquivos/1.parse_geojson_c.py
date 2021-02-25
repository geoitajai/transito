# %%
# dados feed
import os
import json
import datetime
#from shapely.geometry import LineString

# %%
dia_semana_t = ("Segunda-Feira", "Terça-Feira", "Quarta-Feira",
                "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo")

# caminho base
local_base_feed = '/home/jaceguay/Insync/jaceguay@gmail.com/Google Drive - Shared with me/waze/feed'
pastas_base_feed = os.listdir(local_base_feed)

# %%
dados_coletados = []
for pasta in pastas_base_feed:
    caminho_dia = f'{local_base_feed}/{pasta}'
    lista_dias = os.listdir(caminho_dia)
    for dia_json in lista_dias:
        json_local = f'{caminho_dia}/{dia_json}'
        try:
            with open(json_local, encoding='UTF-8') as arq_json:
                data = json.load(arq_json)
                dados_coletados.append(data)
        except:
            print(f'json err: {json_local}')

# %%
group_alerts = {}
group_irregularities = {}
group_jams = {}


def adicionar_alerta(ee):

    data_utc = datetime.datetime.fromtimestamp(
        float(ee['pubMillis'])/1000.)
    data_alerta = data_utc.strftime('%Y-%m-%d')

    if data_alerta not in group_alerts:
        group_alerts[data_alerta] = {
            'type': 'FeatureCollection',
            'uuids': [],
            'features': []
        }

    if ee['uuid'] in group_alerts[data_alerta]['uuids']:
        pass
        # print('alerta duplicado')
    else:
        # print('novo alerta')
        unidade = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [],
            },
        }
        unidade['properties'] = {k: ee[k]
                                 for k in ee.keys() - {'location'}}
        unidade['properties']['timestamp'] = data_utc
        unidade['properties']['dia_semana'] = dia_semana_t[data_utc.weekday()]

        unidade['geometry']['coordinates'].append(ee['location']['x'])
        unidade['geometry']['coordinates'].append(ee['location']['y'])
        group_alerts[data_alerta]['features'].append(unidade)
        group_alerts[data_alerta]['uuids'].append(ee['uuid'])


def adicionar_irregularidade(ee):

    data_utc = datetime.datetime.fromtimestamp(
        float(ee['updateDateMillis'])/1000.)
    data_irregularidade = data_utc.strftime('%Y-%m-%d')

    if data_irregularidade not in group_irregularities:
        group_irregularities[data_irregularidade] = {
            'type': 'FeatureCollection',
            'ids': [],
            'features': []
        }

    if ee['id'] in group_irregularities[data_irregularidade]['ids']:
        pass
        # print('irregularidade duplicada')
    else:
        # print('nova irregularidade')
        unidade = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [],
            },
        }
        unidade['properties'] = {k: ee[k]
                                 for k in ee.keys() - {'line', 'alerts'}}
        for pts in ee['line']:
            unidade['geometry']['coordinates'].append(
                [pts['x'], pts['y']])

        # orientação da linha
        longdif = ee['line'][0]['x'] - ee['line'][-1]['x']
        latdif = ee['line'][0]['y'] - ee['line'][-1]['y']
        if abs(longdif) > abs(latdif):
            if longdif > 0:
                unidade['properties']['orientacao'] = 'LO'
            else:
                unidade['properties']['orientacao'] = 'OL'
        elif abs(longdif) < abs(latdif):
            if latdif > 0:
                unidade['properties']['orientacao'] = 'NS'
            else:
                unidade['properties']['orientacao'] = 'SN'
        else:
            print(f'longdif: {longdif}, latdif: {latdif}')

        unidade['properties']['alerts'] = []
        for alertas in ee['alerts']:
            adicionar_alerta(alertas)
            unidade['properties']['alerts'].append(alertas['uuid'])
        unidade['properties']['timestamp'] = data_utc
        unidade['properties']['dia_semana'] = dia_semana_t[data_utc.weekday()]

        group_irregularities[data_irregularidade]['ids'].append(ee['id'])
        group_irregularities[data_irregularidade]['features'].append(unidade)


def adicionar_congestionamento(ee):

    data_utc = datetime.datetime.fromtimestamp(
        float(ee['pubMillis'])/1000.)
    data_congestionamento = data_utc.strftime('%Y-%m-%d')

    if data_congestionamento not in group_jams:
        group_jams[data_congestionamento] = {
            'type': 'FeatureCollection',
            'uuids': [],
            'features': []
        }

    if ee['uuid'] in group_jams[data_congestionamento]['uuids']:
        pass
        # print('congestionamento duplicaoa')
    else:
        # print('novo congestionamento')
        unidade = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [],
            },
        }
        unidade['properties'] = {k: ee[k]
                                 for k in ee.keys() - {'line'}}
        unidade['properties']['timestamp'] = data_utc
        unidade['properties']['dia_semana'] = dia_semana_t[data_utc.weekday()]

        for pts in ee['line']:
            unidade['geometry']['coordinates'].append(
                [pts['x'], pts['y']])

        # orientação da linha
        longdif = ee['line'][0]['x'] - ee['line'][-1]['x']
        latdif = ee['line'][0]['y'] - ee['line'][-1]['y']
        if abs(longdif) > abs(latdif):
            if longdif > 0:
                unidade['properties']['orientacao'] = 'LO'
            else:
                unidade['properties']['orientacao'] = 'OL'
        elif abs(longdif) < abs(latdif):
            if latdif > 0:
                unidade['properties']['orientacao'] = 'NS'
            else:
                unidade['properties']['orientacao'] = 'SN'
        else:
            print(f'longdif: {longdif}, latdif: {latdif}')

        group_jams[data_congestionamento]['uuids'].append(ee['uuid'])
        group_jams[data_congestionamento]['features'].append(unidade)


for e in dados_coletados:
    # alertas
    try:
        for ee in e['alerts']:
            adicionar_alerta(ee)
    except:
        pass
        # print('sem alertas')

    # irregularidades
    try:
        for ee in e['irregularities']:
            adicionar_irregularidade(ee)
    except:
        pass
        # print('sem irregularidades')

    # congestionamentos
    try:
        for ee in e['jams']:
            adicionar_congestionamento(ee)
    except:
        pass
        # print('sem congestionamentos')

# %%


def atualiza_arquivo(grupo, dados, id):
    try:
        with open(f'resultados/{dados[0][0:4]}/{grupo}/{dados[0]}_{grupo}.json', encoding='UTF-8') as arq_json:
            data = json.load(arq_json)
            diferencas = set(data[f'{id}s']) ^ set(dados[1][f'{id}s'])
            if len(diferencas) == 0:
                print('registro existente')
            else:
                for uiiddif in diferencas:
                    for novo_registro in dados[1]['features']:
                        if novo_registro['properties'][id] == uiiddif:
                            print('atualizando registro')
                            data['features'].append(novo_registro)
                            data[f'{id}s'].append(
                                novo_registro['properties'][id])
                        else:
                            pass
                    with open(f'resultados/{dados[0][0:4]}/{grupo}/{dados[0]}_{grupo}.json', 'w') as fp:
                        json.dump(data, fp, default=str)
    except:
        try:
            os.makedirs(f'resultados/{dados[0][0:4]}/{grupo}')
            with open(f'resultados/{dados[0][0:4]}/{grupo}/{dados[0]}_{grupo}.json', 'w') as fp:
                json.dump(dados[1], fp, default=str)
        except:
            with open(f'resultados/{dados[0][0:4]}/{grupo}/{dados[0]}_{grupo}.json', 'w') as fp:
                json.dump(dados[1], fp, default=str)


# %%
for arquivo_final in group_alerts.items():
    try:
        os.makedirs(f'resultados/{arquivo_final[0][0:4]}')
        atualiza_arquivo('alerts', arquivo_final, 'uuid')
    except:
        atualiza_arquivo('alerts', arquivo_final, 'uuid')

for arquivo_final in group_irregularities.items():
    try:
        os.makedirs(f'resultados/{arquivo_final[0][0:4]}')
        atualiza_arquivo('irregularities', arquivo_final, 'id')
    except:
        atualiza_arquivo('irregularities', arquivo_final, 'id')

for arquivo_final in group_jams.items():
    try:
        os.makedirs(f'resultados/{arquivo_final[0][0:4]}')
        atualiza_arquivo('jams', arquivo_final, 'uuid')
    except:
        atualiza_arquivo('jams', arquivo_final, 'uuid')

# %%
