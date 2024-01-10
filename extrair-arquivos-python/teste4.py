import os
import zipfile
import shutil

pasta_destino = "C:\\Users\\yuri_\\Downloads\\arquivospdfxml\\"
pasta_final = "C:\\Users\\yuri_\\Downloads\\arquivosdownload\\"

if not os.path.exists(pasta_final):
    os.makedirs(pasta_final)

if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)

arquivos = []

# Variável de controle
xml_renomeado = False

for arquivo in os.listdir(pasta_destino):
    if arquivo.endswith(".zip"):
        print("achou o zip")
        print(arquivo)
        root, ext = os.path.splitext(arquivo)
        nome_arquivo = root
        arquivos.append(root)
        print("adicionou na lista")
        print(arquivos)
        arquivo_zip = zipfile.ZipFile(os.path.join(pasta_destino, arquivo))
        arquivo_zip.extractall(pasta_destino)
        print("extraiu o arquivo")
        print(arquivo)
        arquivo_zip.close()
        os.remove(os.path.join(pasta_destino, arquivo))
        print("deletou o arquivo compactado")
        print("NOME DO ARQUIVO APAGADO: " + arquivo)
        for arquivo in os.listdir(pasta_destino):
            print("Inicio do FOR do xml")
            if arquivo.endswith(".xml"):
                print("inicio do IF do xml")
                caminho_atual = os.path.join(pasta_destino, arquivo)
                novo_caminho = os.path.join(pasta_final, arquivos[0])
                os.rename(caminho_atual, novo_caminho + ".xml")
                print("renomeou o xml")
                xml_renomeado = True # Atualiza a variável de controle
        for arquivo in os.listdir(pasta_destino):
            if arquivo.endswith(".pdf") and xml_renomeado and arquivos:
                print("for do PDF")
                caminho_atual = os.path.join(pasta_destino, arquivo)
                shutil.move(caminho_atual, pasta_final)
                print("moveu o pdf")
                print(arquivo)
                arquivos.remove(root) # Remove o item da lista
                print("nome removido da lista")