import os
import zipfile
import shutil

pasta_destino = "C:\\Users\\yuri_\\Downloads\\arquivospdfxml\\"
pasta_final = "C:\\Users\\yuri_\\Downloads\\arquivosdownload\\"

if not os.path.exists(pasta_final):
    os.makedirs(pasta_final)

if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)



def processar_arquivos(pasta_destino, pasta_final):
    
    for arquivo in os.listdir(pasta_destino):
        if arquivo.endswith(".zip"):
            print("achou o zip")
            print(arquivo)
            root, ext = os.path.splitext(arquivo)
            global nome_arquivo
            nome_arquivo = root
            print("adicionou na lista")
            arquivo_zip = zipfile.ZipFile(os.path.join(pasta_destino, arquivo))
            arquivo_zip.extractall(pasta_destino)
            print("extraiu o arquivo")
            print(arquivo)
            arquivo_zip.close()
            os.remove(os.path.join(pasta_destino, arquivo))
            print("deletou o arquivo compactado")
            print("NOME DO ARQUIVO APAGADO:" + arquivo)
            break

def enviar_xml(pasta_destino, pasta_final):
    for arquivo in os.listdir(pasta_destino):
        if arquivo.endswith(".xml"):
            print("Inicio do IF do xml")
            global nome_arquivo
            shutil.move(pasta_destino + arquivo, pasta_final + nome_arquivo + ".xml")
            print("moveu xml")
            break

def enviar_pdf(pasta_destino, pasta_final):            
    for arquivo in os.listdir(pasta_destino):
        if arquivo.endswith(".pdf") and nome_arquivo:
            print("if do PDF")
            shutil.move(pasta_destino + arquivo, pasta_final + arquivo)
            print("moveu o pdf")
            print(arquivo)
            break

funcoes = [processar_arquivos, enviar_pdf, enviar_xml]

while True:
        for funcao in funcoes:
            funcao(pasta_destino, pasta_final)

        if not os.listdir(pasta_destino):
            break
