import os
import zipfile
import shutil

pasta_origem = 'pasta_origem'
pasta_destino = 'pasta_destino'
pasta_final = 'pasta_final'

arquivos = [arq for arq in os.listdir(pasta_origem) if arq.endswith('.zip')]

for arquivo in arquivos:
    caminho_atual = os.path.join(pasta_origem, arquivo)
    with zipfile.ZipFile(caminho_atual, 'r') as arquivo_zip:
        arquivo_zip.extractall(pasta_destino)
    os.remove(caminho_atual)

    for arquivo in os.listdir(pasta_destino):
        if arquivo.endswith(".xml"):
            caminho_atual = os.path.join(pasta_destino, arquivo)
            novo_caminho = os.path.join(pasta_final, arquivos[0])
            os.rename(caminho_atual, novo_caminho + ".xml")

        elif arquivo.endswith(".pdf"):
            caminho_atual = os.path.join(pasta_destino, arquivo)
            shutil.move(caminho_atual, pasta_final)

    print("Arquivos extraídos e movidos para a pasta_final.")