import os
import zipfile

pasta_destino = "C:\\Users\\yuri_\\Downloads\\arquivospdfxml\\"

arquivos = []

contador = 0

for arquivo in os.listdir(pasta_destino):
    if arquivo.endswith(".zip"):
        root,ext = os.path.splitext(arquivo)
        nome_arquivo = root
        arquivos.append(root)
        arquivo_zip = zipfile.ZipFile(os.path.join(pasta_destino, arquivo))
        arquivo_zip.extractall(pasta_destino)
        for arquivo in os.listdir(pasta_destino):
            if arquivo.endswith(".xml"):
                caminho_atual = os.path.join(pasta_destino, arquivo)
                novo_caminho = os.path.join(pasta_destino, arquivos[contador])
                os.rename(caminho_atual, novo_caminho + ".xml")
                contador += 1
        arquivo_zip.close()