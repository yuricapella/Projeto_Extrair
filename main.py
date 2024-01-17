import os
import zipfile
import shutil
from dhooks import Webhook

hook = Webhook("https://discord.com/api/webhooks/1196583315394789396/NSeHoScOLSsORZ3JAcuJSBdLCX8jcQm6tOENrqYzo4uUjEVyJ_QLrxbjR-voNSlcrlkW")

#data=input("lalala")

#hook.send("qualquer coisa")

pasta_destino = "C:\\Users\\yuri_\\Downloads\\arquivospdfxml\\"
pasta_final = "C:\\Users\\yuri_\\Downloads\\arquivosdownload\\"


if not os.path.exists(pasta_final):
    os.makedirs(pasta_final)

if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)


def processar_arquivos():

    for arquivo in os.listdir(pasta_destino):
        root, ext = os.path.splitext(arquivo)
        if ext == ".zip" and os.path.exists(pasta_destino + root + ".pdf"):
            nome_arquivo = root
            arquivo_zip = zipfile.ZipFile(os.path.join(pasta_destino, arquivo))
            arquivo_zip.extractall(pasta_destino)
            um_nome = arquivo_zip.namelist()
            um_nome = um_nome[0]
            arquivo_zip.close()
            os.remove(os.path.join(pasta_destino, arquivo))
            enviar_xml(um_nome, nome_arquivo)
            enviar_pdf(nome_arquivo)
        else:
            if ext == ".zip":
                print("Nao achou o zip e pdf")

def enviar_xml(um_nome, nome_arquivo):
    if os.path.exists(pasta_destino + um_nome):
        shutil.move(pasta_destino + um_nome, pasta_final + nome_arquivo + ".xml")
    else:
        hook.send("Nao achou o XML")

def enviar_pdf(nome_arquivo):
    if os.path.exists(pasta_destino + nome_arquivo + ".pdf"):       
        shutil.move(pasta_destino + nome_arquivo + ".pdf", pasta_final)
        print("moveu o pdf")
    else:
        hook.send("Nao achou o PDF")

processar_arquivos()

