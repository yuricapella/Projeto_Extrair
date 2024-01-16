import os
import zipfile
import shutil

pasta_destino = "C:\\Users\\yuri_\\Downloads\\arquivospdfxml\\"
pasta_final = "C:\\Users\\yuri_\\Downloads\\arquivosdownload\\"



if not os.path.exists(pasta_final):
    os.makedirs(pasta_final)

if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)



def processar_arquivos():

    for arquivo in os.listdir(pasta_destino):
        if arquivo.endswith(".zip"):
            print("achou o zip")
            print(arquivo)
            root, ext = os.path.splitext(arquivo)
            nome_arquivo = root
            print("adicionou na lista")
            arquivo_zip = zipfile.ZipFile(os.path.join(pasta_destino, arquivo))
            arquivo_zip.extractall(pasta_destino)
            um_nome = arquivo_zip.namelist()
            um_nome = um_nome[0]
            print(um_nome)
            print("extraiu o arquivo")
            arquivo_zip.close()
            os.remove(os.path.join(pasta_destino, arquivo))
            print("deletou o arquivo compactado")
            print("NOME DO ARQUIVO APAGADO:" + arquivo)
            enviar_xml(um_nome, nome_arquivo)
            enviar_pdf(nome_arquivo)
        else:
            print("Nao achou o zip")

def enviar_xml(um_nome, nome_arquivo):
    if os.path.exists(pasta_destino + um_nome):
        shutil.move(pasta_destino + um_nome, pasta_final + nome_arquivo + ".xml")
        print("moveu xml")
    else:
        print("Nao achou o XML")

def enviar_pdf(nome_arquivo):
    if os.path.exists(pasta_destino + nome_arquivo + ".pdf"):       
        shutil.move(pasta_destino + nome_arquivo + ".pdf", pasta_final)
        print("moveu o pdf")
    else:
        print("Nao achou o pdf")

processar_arquivos()

