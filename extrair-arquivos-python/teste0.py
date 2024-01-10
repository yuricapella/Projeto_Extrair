import os
import zipfile

pasta_destino = "C:\\Users\\yuri_\\Downloads\\arquivospdfxml\\"
pasta_destino2 = "C:\\Users\\yuri_\\Downloads\\arquivosdownload\\"

for arquivo in os.listdir(pasta_destino):
    if arquivo.endswith(".zip"):
        root,ext = os.path.splitext(arquivo)
        nome_arquivo = root
        arquivo_zip = zipfile.ZipFile(os.path.join(pasta_destino, arquivo))
        arquivo_zip.extractall(pasta_destino)
        for arquivo in os.listdir(pasta_destino):
            if arquivo.endswith(".xml"):
                caminho_atual = os.path.join(pasta_destino, arquivo)
                novo_caminho = os.path.join(pasta_destino, nome_arquivo)
                os.rename(caminho_atual, novo_caminho + ".xml")
        arquivo_zip.close()
        os.rename(os.path.join(pasta_destino, nome_arquivo + ".xml"), os.path.join(pasta_destino2, nome_arquivo + ".xml"))

for arquivo in os.listdir(pasta_destino): 
    if arquivo.endswith(".pdf"):
        os.rename(os.path.join(pasta_destino, arquivo), os.path.join(pasta_destino2, arquivo))

