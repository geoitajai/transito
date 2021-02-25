# %%
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import datetime
import json

# %%
gauth = GoogleAuth()
drive = GoogleDrive(gauth)
pastadestino = '/home/jaceguay/temp/waze_feed'
data_hj = datetime.date.today()
hoje = data_hj.strftime("%Y-%m-%d")
#hoje = '2021-01-16'
print(hoje)

# %%

# arquivo log


def gerenciamento_downloads(diaatual, arquivoatual, diascompletos):

    fileatalho = drive.CreateFile({'id': '1Wjw7gzg2z_pe2vjNyWe91CmHqQzDkcaB'})
    log_conteudo = json.loads(fileatalho.GetContentString())
    # log_conteudo['historico_dias_completos'].extend(diascompletos)  # lista de dias
    log_conteudo['historico_dias_completos'] = []
    log_conteudo['andamento_dia_atual'] = 0
    log_conteudo['andamento_arquivo_atual'] = 0

    # print(log_conteudo)

    log_novo = drive.CreateFile({'id': '1Wjw7gzg2z_pe2vjNyWe91CmHqQzDkcaB'})
    log_novo.SetContentString(json.dumps(log_conteudo))
    log_novo.Upload()

    # create new file
    # gdrive_id_arquivo = '1UXLVaN0__N5oqdQs5whCn_xd1Ip41vuv'
    # newlog = drive.CreateFile({'parents': [{'id': f'{gdrive_id_arquivo}'}],
    #                          'title': 'log_atual.json',
    #                          'mimeType': 'application/json'})
    #newlog.SetContentString('{"andamento_dia_atual": "0", "andamento_arquivo_atual": "0", "historico_dias_completos": []}')
    # newlog.Upload()


# %%
#gerenciamento_downloads(0, 0, 0)

# %%
fileatalho_log = drive.CreateFile({'id': '1Wjw7gzg2z_pe2vjNyWe91CmHqQzDkcaB'})
log_conteudo_arq = json.loads(fileatalho_log.GetContentString())
print(log_conteudo_arq)

ultimo_proc = 0
# log_conteudo_dia = datetime.datetime.strptime(log_conteudo['andamento_dia_atual'], '%Y-%m-%d').date()

# %%
# pasta dia


def salvararquivo(foldername, folderid):
    global ultimo_proc
    try:
        foldefiles = drive.ListFile(
            {'q': f"'{folderid}' in parents and trashed=false"}).GetList()

        for files in foldefiles:
            datacria = files['createdDate'][0:10]
            nome = files['title']
            fileid = files['id']
            nomeint = int(nome)

            if nomeint > ultimo_proc:
                ultimo_proc = nomeint

            if datacria == hoje:
                try:
                    if int(nome) > int(log_conteudo_arq['andamento_arquivo_atual']):
                        filehj = drive.CreateFile({'id': fileid})
                        try:
                            os.makedirs(
                                f'{pastadestino}/{foldername}/{datacria}')
                            filehj.GetContentFile(
                                f'{pastadestino}/{foldername}/{datacria}/{nome}.json')
                        except:
                            filehj.GetContentFile(
                                f'{pastadestino}/{foldername}/{datacria}/{nome}.json')
                except:
                    print(
                        f"erro {log_conteudo_arq['andamento_arquivo_atual']}{nome}")
            elif nomeint > int(log_conteudo_arq['andamento_arquivo_atual']): #datacria not in log_conteudo_arq['historico_dias_completos'] and
                filehj = drive.CreateFile({'id': fileid})
                try:
                    os.makedirs(f'{pastadestino}/{foldername}/{datacria}')
                    filehj.GetContentFile(
                        f'{pastadestino}/{foldername}/{datacria}/{nome}.json')
                except:
                    filehj.GetContentFile(
                        f'{pastadestino}/{foldername}/{datacria}/{nome}.json')
            else:
                print('historico')

    except:
        #print(f'não foi possível listar pasta: {foldername} id: {folderid}')
        print('pasta_err')

        #print(f'salvo: {pastadestino}/{foldername}/{nome}.json')
        # filehj.GetContentFile(f'{pastadestino}/{foldername}/{nome}.json')


# %%
# pasta principal
file_list = drive.ListFile(
    {'q': "'1WLZPWdJ13HDaC0u0j_gG68MzF1GhbPn7' in parents and trashed=false"}).GetList()
for feedfolder in file_list:
    #print('title: %s, id: %s' % (file1['title'], file1['id']))
    #print(f"{feedfolder['title']} - {feedfolder['createdDate'][0:10]}")
    #print(f"pasta aberta: {feedfolder['createdDate'][0:10]}")

    nomediretorio = feedfolder['createdDate'][0:7]
    iddiretorio = feedfolder["id"]

    try:
        os.makedirs(f'{pastadestino}/{nomediretorio}')
        salvararquivo(nomediretorio, iddiretorio)
    except:
        #print(f'pasta existente: {pastadestino}/{nomediretorio}')
        salvararquivo(nomediretorio, iddiretorio)
    else:
        print(f'diretorio_err: {nomediretorio} - {iddiretorio}')

    if feedfolder['createdDate'][0:10] != hoje:
        log_conteudo_arq['historico_dias_completos'].append(
            feedfolder['createdDate'][0:10])


# %%
log_conteudo_arq['andamento_dia_atual'] = hoje
log_conteudo_arq['historico_dias_completos'] = list(set(log_conteudo_arq['historico_dias_completos']))
log_conteudo_arq['andamento_arquivo_atual'] = ultimo_proc
print(log_conteudo_arq)
log_novo = drive.CreateFile({'id': '1Wjw7gzg2z_pe2vjNyWe91CmHqQzDkcaB'})
log_novo.SetContentString(json.dumps(log_conteudo_arq))
log_novo.Upload()
