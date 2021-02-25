# %%
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import datetime
import json

# %%
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
gauth.LoadCredentialsFile(gauth)
drive = GoogleDrive(gauth)
pastadestino = '/home/jaceguay/temp/waze_feed'
data_hj = datetime.date.today()
hoje = data_hj.strftime("%Y-%m-%d")
print(data_hj)

# %%
log_atalho = drive.CreateFile({'id': '1Wjw7gzg2z_pe2vjNyWe91CmHqQzDkcaB'})
log_conteudo = json.loads(log_atalho.GetContentString())
print(log_conteudo)

# %%
# Dados Locais
pasta_principal = [dI for dI in os.listdir(
    pastadestino) if os.path.isdir(os.path.join(pastadestino, dI))]

arquivos_locais = []
for arq_loc in log_conteudo['historico_dias_completos']:
    global arquivos_locais
    stripdata = arq_loc.replace('-0', '-')
    localiza = f'{pastadestino}/{arq_loc[0:7]}/{stripdata}'
    bfiles = [f for f in os.listdir(
        localiza) if os.path.isfile(os.path.join(localiza, f))]
    arquivos_locais = arquivos_locais + bfiles

# %%

file_list = drive.ListFile(
    {'q': "'1WLZPWdJ13HDaC0u0j_gG68MzF1GhbPn7' in parents and trashed=false"}).GetList()

ultimo_nome = 0

for feedfolder in file_list:
    global ultimo_nome
    data_diretorio = feedfolder['createdDate'][0:10]
    id_diretorio = feedfolder["id"]

    if data_diretorio in log_conteudo['historico_dias_completos']:
        dadosGoogle = []
        sub_file_list = drive.ListFile(
            {'q': f"'{id_diretorio}' in parents and trashed=false"}).GetList()
        for ee in sub_file_list:
            datacria = ee['createdDate'][0:10]
            mescria = ee['createdDate'][0:7]
            datastriped = ee['createdDate'][0:10].replace('-0', '-')
            nome = ee['title']
            fileid = ee['id']

            if nome not in arquivos_locais:
                try:
                    if int(nome) > ultimo_nome:
                        ultimo_nome = int(nome)
                    filehj = drive.CreateFile({'id': fileid})
                    try:
                        os.makedirs(
                            f'{pastadestino}/{mescria}/{datastriped}')
                        filehj.GetContentFile(
                            f'{pastadestino}/{mescria}/{datastriped}/{nome}')
                        print(
                            f'novo diretorio:{pastadestino}/{mescria}/{datastriped}/{nome}')
                    except:
                        filehj.GetContentFile(
                            f'{pastadestino}/{mescria}/{datastriped}/{nome}')
                        print(f'{pastadestino}/{mescria}/{datastriped}/{nome}')
                    dadosGoogle.append(nome)
                except:
                    print(f'erro arquivo rss: {nome}')

        print(data_diretorio, dadosGoogle)

# %%
log_conteudo['andamento_arquivo_atual'] = ultimo_nome
log_conteudo['andamento_dia_atual'] = hoje
if hoje not in log_conteudo['historico_dias_completos']:
    log_conteudo['historico_dias_completos'].pop(0)
    log_conteudo['historico_dias_completos'].append(hoje)

print(log_conteudo)

log_novo = drive.CreateFile({'id': '1Wjw7gzg2z_pe2vjNyWe91CmHqQzDkcaB'})
log_novo.SetContentString(json.dumps(log_conteudo))
log_novo.Upload()
